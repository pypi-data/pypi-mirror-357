from __future__ import annotations

from typing import Generator
from pathlib import Path

import numpy as np

from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition
from gpaw.tddft.units import au_to_eV, eV_to_au
from gpaw.mpi import world

from .distributed.frequency import FourierTransformer
from .density_matrix import DensityMatrix
from .readers.numpy import FrequencyDensityMatrixReader
from .base import BaseDensityMatrices, WorkMetadata
from ..perturbation import create_perturbation, PerturbationLike, DeltaKick, NoPerturbation
from ..utils import Logger, two_communicator_sizes
from ..utils.memory import MemoryEstimate
from ..typing import Array1D


class FrequencyDensityMatrixMetadata(WorkMetadata):

    """ Metadata to the density matrices.

    Parameters
    ----------
    density_matrices
        Parent of this object.
    globalw
        Frequency index.
    localw
        Frequency index on this rank.
    globalr
        Real/imaginary index.
    localr
        Real/imaginary index on this rank.
    """

    density_matrices: FrequencyDensityMatrices
    globalw: int
    localw: int
    globalr: int
    localr: int

    def __new__(cls,
                density_matrices: FrequencyDensityMatrices,
                globalw: int,
                globalr: int,
                localw: int,
                localr: int):
        self = WorkMetadata.__new__(cls, density_matrices=density_matrices)
        self.globalw = globalw
        self.globalr = globalr
        self.localw = localw
        self.localr = localr
        return self

    @property
    def global_indices(self):
        return (self.globalw, self.globalr)

    @property
    def freq(self) -> float:
        """ Frequency in units of eV. """
        return self.density_matrices.frequencies[self.globalw]

    @property
    def reim(self) -> str:
        """ Returns real/imaginary tag ``'Re'`` or ``'Im'``.

        The tag corresponds to the Fourier transform of the real
        or imaginary part of the density matrix.
        """
        return self.density_matrices.reim[self.globalr]

    @property
    def desc(self) -> str:
        return f'{self.reim} @ Freq. {self.freq:.3f}eV'

    @property
    def real(self) -> bool:
        return self.reim == 'Re'

    @property
    def imag(self) -> bool:
        return not self.real


class FrequencyDensityMatrices(BaseDensityMatrices[FrequencyDensityMatrixMetadata]):

    """
    Collection of density matrices in the Kohn-Sham basis in the frequency
    domain, for different frequencies.

    Parameters
    ----------
    ksd
        KohnShamDecomposition object or file name.
    frequencies
        Compute density matrices for these frequencies (or as close to them as possible). In units of eV.
    frequency_broadening
        Gaussian broadening width in units of eV. Default (0) is no broadening.
    real
        Calculate the Fourier transform of the real part of the density matrix.
    imag
        Calculate the Fourier transform of the imaginary part of the density matrix.
    calc_size
        Size of the calculation communicator.
    """

    def __init__(self,
                 ksd: KohnShamDecomposition | str,
                 frequencies: list[float] | Array1D[np.float64],
                 frequency_broadening: float = 0,
                 real: bool = True,
                 imag: bool = True,
                 calc_size: int = 1,
                 log: Logger | None = None):
        self._freq_w = np.array(frequencies)
        self._frequency_broadening = frequency_broadening

        super().__init__(ksd=ksd,
                         real=real, imag=imag,
                         calc_size=calc_size, log=log)

    @property
    def frequencies(self) -> Array1D[np.float64]:
        """ Frequencies in units of eV. """
        return self._freq_w  # type: ignore

    @property
    def frequency_broadening(self) -> float:
        """ Gaussian broadening width for frequencies in units of eV. """
        return self._frequency_broadening

    def work_loop(self,
                  rank: int) -> Generator[FrequencyDensityMatrixMetadata | None, None, None]:
        nw = len(self.frequencies)
        nwperrank = (nw + self.loop_comm.size - 1) // self.loop_comm.size

        for localw in range(nwperrank):
            globalw = rank + localw * self.loop_comm.size
            for r in range(len(self.reim)):
                if globalw < nw:
                    yield FrequencyDensityMatrixMetadata(density_matrices=self, globalw=globalw,
                                                         localw=localw, globalr=r, localr=r)
                else:
                    yield None

    def write_to_disk(self,
                      frho_fmt: str):
        """ Calculate the density matrices and save to disk.

        Parameters
        ----------
        frho_fmt
            Formatting string for the density matrices saved to disk.

            The formatting string should be a plain string containing variable
            placeholders within curly brackets ``{}``. It should not be confused with
            a formatted string literal (f-string).

            Example:

             * frho_fmt = ``frho/w{freq:05.2f}-{reim}.npy``.

            Accepts variables:

             * ``{freq}`` - Frequency in units of eV.
             * ``{reim}`` - ``'Re'`` or ``'Im'`` for Fourier transform of real/imaginary
               part of density matrix.
        """
        nlocaltot = len(self.local_work_plan)

        # Iterate over density matrices on all ranks
        for ndone, (work, dm) in enumerate(self, 1):
            avg = self.log.elapsed('read')/ndone
            estrem = avg * (nlocaltot - ndone)
            self.log(f'Obtained density matrix {ndone:4.0f}/{nlocaltot:4.0f} on this rank. '
                     f'Avg: {avg:10.3f}s, estimated remaining: {estrem:10.3f}s', who='Writer', flush=True)
            fname_kw = dict(freq=work.freq, reim=work.reim)
            fpath = Path(frho_fmt.format(**fname_kw))
            rho_ia = dm.rho_ia
            if self.calc_comm.rank == 0:
                assert isinstance(rho_ia, np.ndarray)
                fpath.parent.mkdir(parents=True, exist_ok=True)
                if fpath.suffix == '.npz':
                    # Write numpy archive
                    np.savez(str(fpath), rho_ia=rho_ia)
                else:
                    # Save numpy binary file
                    np.save(str(fpath), rho_ia)
                self.log(f'Written {fpath}', who='Writer', flush=True)
        world.barrier()


class FrequencyDensityMatricesFromDisk(FrequencyDensityMatrices):

    """
    Collection of density matrices in the Kohn-Sham basis in the frequency
    domain, for different frequencies. Read from disk.

    Parameters
    ----------
    ksd
        KohnShamDecomposition object or file name.
    frho_fmt
        Formatting string for the density matrices
        in frequency space saved to disk.

        The formatting string should be a plain string containing variable
        placeholders within curly brackets ``{}``. It should not be confused with
        a formatted string literal (f-string).

        Example:

         * frho_fmt = ``frho/w{freq:05.2f}-{reim}.npy``.

        Accepts variables:

         * ``{freq}`` - Frequency in units of eV.
         * ``{reim}`` - ``'Re'`` or ``'Im'`` for Fourier transform of real/imaginary
           part of density matrix.
    perturbation
        The perturbation which the density matrices are a response to.
    frequencies
        Compute density matrices for these frequencies (or as close to them as possible). In units of eV.
    real
        Calculate the Fourier transform of the real part of the density matrix
    imag
        Calculate the Fourier transform of the imaginary part of the density matrix.
    calc_size
        Size of the calculation communicator.
    """

    def __init__(self,
                 ksd: KohnShamDecomposition | str,
                 frho_fmt: str,
                 perturbation: PerturbationLike,
                 frequencies: list[float] | Array1D[np.float64],
                 real: bool = True,
                 imag: bool = True,
                 calc_size: int = 1,
                 log: Logger | None = None):
        reader = FrequencyDensityMatrixReader(frho_fmt=frho_fmt,
                                              ksd=ksd,
                                              filter_frequencies=frequencies,
                                              real=real, imag=imag,
                                              log=log)
        self.reader = reader
        super().__init__(ksd=reader.ksd, frequencies=reader.frequencies,
                         real=real, imag=imag,
                         calc_size=calc_size,
                         log=reader.log)
        self.perturbation = create_perturbation(perturbation)
        assert isinstance(self.perturbation, (DeltaKick, NoPerturbation))

    def __str__(self) -> str:
        return str(self.reader)

    def __iter__(self) -> Generator[tuple[FrequencyDensityMatrixMetadata, DensityMatrix], None, None]:
        for work in self.local_work_plan:
            self.log.start('read')
            rho = self.reader.read(work.freq, work.reim == 'Re')
            if isinstance(self.perturbation, DeltaKick):
                # Only delta kick supported at this point for normalization
                rho /= self.perturbation.strength
            matrices = {0: rho if self.calc_comm.rank == 0 else None}
            dm = DensityMatrix(ksd=self.ksd, matrices=matrices)

            yield work, dm


class FrequencyDensityMatricesFromWaveFunctions(FrequencyDensityMatrices):

    """
    Collection of density matrices in the Kohn-Sham basis in the frequency
    domain, for different frequencies. Obtained from the time-dependent wave functions file,
    which is read from disk.

    Parameters
    ----------
    ksd
        KohnShamDecomposition object or file name.
    wfs_fname
        File name of the time-dependent wave functions file.
    perturbation
        The perturbation which the density matrices are a response to.
    frequencies
        Compute density matrices for these frequencies (or as close to them as possible). In units of eV.
    frequency_broadening
        Gaussian broadening width in units of eV. Default (0) is no broadening.
    real
        Calculate the real part of density matrices.
    imag
        Calculate the imaginary part of density matrices.
    calc_size
        Size of the calculation communicator.
    stridet
        Skip this many steps when reading the time-dependent wave functions file.
    """

    def __init__(self,
                 ksd: KohnShamDecomposition | str,
                 wfs_fname: str,
                 perturbation: PerturbationLike,
                 frequencies: list[float] | Array1D[np.float64],
                 frequency_broadening: float = 0,
                 real: bool = True,
                 imag: bool = True,
                 log: Logger | None = None,
                 calc_size: int = 1,
                 stridet: int = 1):
        _, calc_size = two_communicator_sizes(-1, calc_size)
        # The calc_comm rank 0's are world ranks 0, with a spacing of calc_size
        result_on_ranks = list(range(0, world.size, calc_size))

        rho_nn_fft = FourierTransformer.from_parameters(
                wfs_fname, ksd,
                perturbation=perturbation,
                yield_re=real,
                yield_im=imag,
                filter_frequencies=np.array(frequencies) * eV_to_au,
                frequency_broadening=frequency_broadening * eV_to_au,
                stridet=stridet,
                result_on_ranks=result_on_ranks,
                log=log)
        self.rho_nn_fft = rho_nn_fft
        super().__init__(ksd=rho_nn_fft.ksd, frequencies=rho_nn_fft.freq_w * au_to_eV,
                         frequency_broadening=frequency_broadening,
                         real=real, imag=imag,
                         calc_size=calc_size,
                         log=rho_nn_fft.log)

    def __str__(self) -> str:
        lines = []
        lines.append('Response from time-dependent wave functions')
        lines.append('')
        lines += ['' + line for line in str(self.rho_nn_fft.rho_nn_reader.rho_wfs_reader).split('\n')]
        lines.append('')
        lines += ['' + line for line in str(self.rho_nn_fft.rho_nn_reader).split('\n')]
        lines.append('')
        lines += ['' + line for line in str(self.rho_nn_fft).split('\n')]

        return '\n'.join(lines)

    def get_memory_estimate(self) -> MemoryEstimate:
        return self.rho_nn_fft.get_memory_estimate()

    @property
    def myw(self) -> list[int]:
        """ List of indices corresponding to the frequency indices on held on this rank. """
        return self.rho_nn_fft.my_work()

    def __iter__(self) -> Generator[tuple[FrequencyDensityMatrixMetadata, DensityMatrix], None, None]:
        parameters = self.rho_nn_fft.rho_nn_reader._parameters
        flt = (slice(parameters.n1size), slice(parameters.n2size))

        dist_buffer = self.rho_nn_fft.dist_buffer  # Perform the redistribution
        self.ksd.distribute(self.calc_comm)

        for work in self.local_work_plan:
            if self.calc_comm.rank == 0:
                assert self.myw[work.localw] == work.globalw

            if self.calc_comm.rank == 0:
                # Buffer shape is i, a, frequencies
                rho_ia = dist_buffer._get_data(work.reim == 'Re', 0)[flt + (work.localw, )]
            matrices = {0: rho_ia if self.calc_comm.rank == 0 else None}
            dm = DensityMatrix(ksd=self.ksd, matrices=matrices, comm=self.calc_comm)

            yield work, dm

    def parallel_prepare(self):
        self.rho_nn_fft.dist_buffer  # Perform the redistribution
