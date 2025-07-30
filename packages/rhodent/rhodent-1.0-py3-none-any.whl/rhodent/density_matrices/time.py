from __future__ import annotations

from typing import Generator, Collection

from pathlib import Path
import numpy as np
from numpy.typing import NDArray

from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition
from gpaw.tddft.units import as_to_au, au_to_as, eV_to_au, au_to_eV
from gpaw.mpi import world

from .buffer import DensityMatrixBuffer
from .distributed.pulse import PulseConvolver
from .readers.gpaw import KohnShamRhoWfsReader
from .readers.numpy import FrequencyDensityMatrixReader, TimeDensityMatrixReader
from .density_matrix import DensityMatrix
from .base import BaseDensityMatrices, WorkMetadata
from ..perturbation import create_perturbation, Perturbation, DeltaKick, PerturbationLike, PulsePerturbation
from ..utils import Logger, two_communicator_sizes, get_gaussian_pulse_values
from ..utils.logging import format_times
from ..utils.memory import MemoryEstimate
from ..typing import Array1D, Communicator


class ConvolutionDensityMatrixMetadata(WorkMetadata):
    """ Metadata to the density matrices.

    Properties
    ----------
    density_matrices
        Parent of this object.
    globalt
        Time index.
    localt
        Time index on this rank.
    globalp
        Pulse index.
    localp
        Pulse index on this rank.
    """
    density_matrices: ConvolutionDensityMatrices
    globalt: int
    globalp: int
    localt: int
    localp: int

    def __new__(cls,
                density_matrices: ConvolutionDensityMatrices,
                globalt: int,
                globalp: int,
                localt: int,
                localp: int):
        self = WorkMetadata.__new__(cls, density_matrices=density_matrices)
        self.globalt = globalt
        self.globalp = globalp
        self.localt = localt
        self.localp = localp
        return self

    @property
    def global_indices(self):
        return (self.globalp, self.globalt)

    @property
    def time(self) -> float:
        """ Simulation time in units of as. """
        return self.density_matrices.times[self.globalt]

    @property
    def pulse(self) -> Perturbation:
        """ Pulse. """
        return self.density_matrices.pulses[self.globalp]

    @property
    def desc(self) -> str:
        timestr = f'{self.time:.1f}as'
        if len(self.density_matrices.pulses) == 1:
            return timestr

        d = self.pulse.todict()
        if d['name'] == 'GaussianPulse':
            pulsestr = f'{d["frequency"]:.1f}eV'
        else:
            pulsestr = f'#{self.globalp}'
        return f'{timestr} @ Pulse {pulsestr}'


class ConvolutionDensityMatrices(BaseDensityMatrices[ConvolutionDensityMatrixMetadata]):

    """
    Collection of density matrices in the Kohn-Sham basis for different times,
    after convolution with various pulses.

    Plain density matrices and/or derivatives thereof may be represented.

    Parameters
    ----------
    ksd
        KohnShamDecomposition object or file name.
    pulses
        Convolute the density matrices with these pulses.
    times
        Compute density matrices for these times (or as close to them as possible). In units of as.
    derivative_order_s
        Compute density matrix derivatives of the following orders.
        0 for plain density matrix and positive integers for derivatives.
    real
        Calculate the real part of density matrices.
    imag
        Calculate the imaginary part of density matrices.
    calc_size
        Size of the calculation communicator.
    """

    _derivative_order_s: list[int]

    def __init__(self,
                 ksd: KohnShamDecomposition | str,
                 pulses: Collection[PerturbationLike],
                 times: list[float] | NDArray[np.float64],
                 derivative_order_s: list[int] = [0],
                 real: bool = True,
                 imag: bool = True,
                 calc_size: int = 1,
                 log: Logger | None = None):
        self._time_t = np.array(times)
        self._pulses = [create_perturbation(pulse) for pulse in pulses]
        self._derivative_order_s = derivative_order_s

        super().__init__(ksd=ksd,
                         real=real, imag=imag,
                         calc_size=calc_size, log=log)

        tag_s = ['', '-Iomega', '-omega2']
        return_keys_by_order = {0: 'pulserho', 1: 'pulsedrho', 2: 'pulseddrho'}
        self.keys_by_order = {0: 'rho_ia', 1: 'drho_ia', 2: 'ddrho_ia'}
        if 1 not in derivative_order_s:
            tag_s.remove('-Iomega')
            return_keys_by_order.pop(1)
        if 2 not in derivative_order_s:
            tag_s.remove('-omega2')
            return_keys_by_order.pop(2)
        self.tag_s = tag_s
        self.return_keys_by_order = return_keys_by_order

    @property
    def times(self) -> Array1D[np.float64]:
        """ Simulation time in units of as. """
        return self._time_t  # type: ignore

    @property
    def nt(self) -> int:
        """ Number of times. """
        return len(self.times)

    @property
    def pulses(self) -> list[Perturbation]:
        """ Pulses with which density matrices are convoluted. """
        return self._pulses

    @property
    def derivative_order_s(self) -> list[int]:
        """
        List of orders of the density matrix derivatives to be computed.
        ``0`` for plain density matrix and positive integers for derivatives.
        """
        return self._derivative_order_s

    def work_loop(self,
                  rank: int) -> Generator[ConvolutionDensityMatrixMetadata | None, None, None]:
        nt = len(self.times)
        ntperrank = (nt + self.loop_comm.size - 1) // self.loop_comm.size

        # Do convolution pulse-by-pulse, time-by-time
        for p, pulse in enumerate(self.pulses):
            # Determine which times to compute on this loop_comm rank for good load balancing
            shift = (p * nt + rank) % self.loop_comm.size
            for localt in range(ntperrank):
                globalt = shift + localt * self.loop_comm.size
                if globalt < nt:
                    yield ConvolutionDensityMatrixMetadata(density_matrices=self, globalt=globalt,
                                                           localt=localt, globalp=p, localp=p)
                else:
                    yield None

    def write_to_disk(self,
                      pulserho_fmt: str):
        """ Calculate the density matrices and save to disk.

        Parameters
        ----------
        pulserho_fmt
            Formatting string for the density matrices saved to disk.

            The formatting string should be a plain string containing variable
            placeholders within curly brackets ``{}``. It should not be confused with
            a formatted string literal (f-string).

            Example:

             * pulserho_fmt =  ``pulserho/t{time:09.1f}{tag}.npy``.

            Accepts variables

             * ``{time}`` - Time in units of as.
             * ``{tag}`` - Derivative tag, ``''``, ``'-Iomega'``, or ``'-omega2'``.
             * ``{pulsefreq}`` - Pulse frequency in units of eV.
             * ``{pulsefwhm}`` - Pulse FWHM in units of fs.
        """
        nlocaltot = len(self.local_work_plan)

        tags_keys = [(tag, key) for s, (tag, key) in enumerate(
            [('', 'rho_ia'), ('-Iomega', 'drho_ia'), ('-omega2', 'ddrho_ia')]) if s in self.derivative_order_s]

        # Iterate over density matrices on all ranks
        for ndone, (work, dm) in enumerate(self, 1):
            avg = self.log.elapsed('read')/ndone
            estrem = avg * (nlocaltot - ndone)
            self.log(f'Obtained density matrix {ndone:4.0f}/{nlocaltot:4.0f} on this rank. '
                     f'Avg: {avg:10.3f}s, estimated remaining: {estrem:10.3f}s', who='Writer', flush=True)
            for tag, key in tags_keys:
                fname_kw = dict(time=work.time, tag=tag, **get_gaussian_pulse_values(work.pulse))
                fpath = Path(pulserho_fmt.format(**fname_kw))
                rho_ia = getattr(dm, key)
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


class TimeDensityMatricesFromWaveFunctions(ConvolutionDensityMatrices):

    """
    Collection of density matrices in the Kohn-Sham basis for different times,
    obtained by reading the time-dependent wave functions file.

    Parameters
    ----------
    ksd
        KohnShamDecomposition object or file name.
    wfs_fname
        File name of the time-dependent wave functions file.
    times
        Compute density matrices for these times (or as close to them as possible). In units of as.
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
                 times: list[float] | Array1D[np.float64],
                 real: bool = True,
                 imag: bool = True,
                 calc_size: int = 1,
                 log: Logger | None = None,
                 stridet: int = 1):
        rho_nn_direct = KohnShamRhoWfsReader(wfs_fname=wfs_fname, ksd=ksd,
                                             yield_re=real, yield_im=imag,
                                             filter_times=np.array(times) * as_to_au,  # type: ignore
                                             stridet=stridet, log=log)
        self.rho_nn_direct = rho_nn_direct

        super().__init__(ksd=rho_nn_direct.ksd,
                         times=rho_nn_direct.time_t * au_to_as,
                         real=real,
                         imag=imag,
                         pulses=[None],
                         calc_size=1,
                         log=rho_nn_direct.log)

        imin, imax, amin, amax = self.ksd.ialims()

        # Read density matrices corresponding to ksd ialims
        self._n1slice = slice(imin, imax + 1)
        self._n2slice = slice(amin, amax + 1)

    def __str__(self) -> str:
        lines = ['Response from time-dependent wave functions']

        lines.append('')
        lines += ['  ' + line for line in str(self.rho_nn_direct).split('\n')]
        shape = (self._n1slice.stop - self._n1slice.start,
                 self._n2slice.stop - self._n2slice.start,)
        if 'Re' in self.reim and 'Im' in self.reim:
            reim_desc = 'real and imaginary parts'
        elif 'Re' in self.reim:
            reim_desc = 'real parts'
        else:
            reim_desc = 'imaginary parts'

        lines.append('')
        lines.append(f'Density matrix shape {shape}')
        lines.append(f'reading {reim_desc}')

        return '\n'.join(lines)

    def get_memory_estimate(self) -> MemoryEstimate:
        shape = (self._n1slice.stop - self._n1slice.start,
                 self._n2slice.stop - self._n2slice.start,)
        narrays = 2 if 'Re' in self.reim and 'Im' in self.reim else 1
        for t_r in self.rho_nn_direct.work_loop_by_ranks():
            nreading = len(t_r)
            break
        memory_estimate = MemoryEstimate()
        memory_estimate.add_child('Time-dependent wave functions reader',
                                  self.rho_nn_direct.get_memory_estimate())
        memory_estimate.add_key('Density matrix', (shape) + (narrays, ),
                                on_num_ranks=nreading)

        return memory_estimate

    def __iter__(self) -> Generator[tuple[ConvolutionDensityMatrixMetadata, DensityMatrix], None, None]:
        assert self.calc_comm.size == 1  # TODO

        for work, dm_buffer in zip(self.work_loop(self.loop_comm.rank),
                                   self.rho_nn_direct.iread(0, 0, self._n1slice, self._n2slice)):
            assert work is not None
            if 'Re' in self.reim:
                Rerho_ia = dm_buffer._get_real(0)
            if 'Im' in self.reim:
                Imrho_ia = dm_buffer._get_imag(0)
            if 'Re' in self.reim and 'Im' in self.reim:
                # Complex result
                # Compared to numpy, we use another convention, hence the minus sign
                rho_ia = Rerho_ia - 1j * Imrho_ia
            elif 'Re' in self.reim:
                # Real result
                rho_ia = Rerho_ia
            else:
                rho_ia = -1j * Imrho_ia
            matrices: dict[int, NDArray[np.complex128] | None] = {0: rho_ia}
            dm = DensityMatrix(ksd=self.ksd, matrices=matrices, comm=self.calc_comm)

            yield work, dm

    def parallel_prepare(self):
        self.rho_nn_direct.parallel_prepare()


class ConvolutionDensityMatricesFromDisk(ConvolutionDensityMatrices):

    """
    Collection of density matrices in the Kohn-Sham basis after convolution with
    one or several pulses, for different times. Read from disk.

    Parameters
    ----------
    ksd
        KohnShamDecomposition object or file name.
    pulserho_fmt
        Formatting string for the density matrices saved to disk.

        The formatting string should be a plain string containing variable
        placeholders within curly brackets ``{}``. It should not be confused with
        a formatted string literal (f-string).

        Example:

         * pulserho_fmt =  ``pulserho/t{time:09.1f}{tag}.npy``.

        Accepts variables

         * ``{time}`` - Time in units of as.
         * ``{tag}`` - Derivative tag, ``''``, ``'-Iomega'``, or ``'-omega2'``.
         * ``{pulsefreq}`` - Pulse frequency in units of eV.
         * ``{pulsefwhm}`` - Pulse FWHM in units of fs.
    pulses
        Convolute the density matrices with these pulses.
    times
        Compute density matrices for these times (or as close to them as possible). In units of as.
    derivative_order_s
        Compute density matrix derivatives of the following orders.
        ``0`` for plain density matrix and positive integers for derivatives.
    real
        Calculate real part of density matrices.
    imag
        Calculate imaginary part of density matrices.
    calc_size
        Size of the calculation communicator.
    """

    def __init__(self,
                 ksd: KohnShamDecomposition | str,
                 pulserho_fmt: str,
                 pulses: Collection[PerturbationLike],
                 times: list[float] | Array1D[np.float64],
                 derivative_order_s: list[int] = [0],
                 log: Logger | None = None,
                 real: bool = True,
                 imag: bool = True,
                 calc_size: int = 1):
        reader = TimeDensityMatrixReader(pulserho_fmt=pulserho_fmt,
                                         ksd=ksd,
                                         pulses=pulses,
                                         filter_times=times,
                                         derivative_order_s=derivative_order_s,
                                         log=log)
        self.reader = reader
        super().__init__(ksd=reader.ksd, pulses=reader.pulses, times=reader.times,
                         real=real, imag=imag,
                         derivative_order_s=derivative_order_s, calc_size=calc_size, log=reader.log)
        self.ksd.distribute(self.calc_comm)
        self.pulserho_fmt = pulserho_fmt

    def __str__(self) -> str:
        return str(self.reader)

    def __iter__(self) -> Generator[tuple[ConvolutionDensityMatrixMetadata, DensityMatrix], None, None]:
        for work in self.local_work_plan:
            self.log.start('read')
            matrices: dict[int, NDArray[np.complex128] | None] = dict()
            for derivative in self.derivative_order_s:
                if self.calc_comm.rank > 0:
                    # Don't read on non calc comm root ranks
                    matrices[derivative] = None
                    continue

                matrices[derivative] = self.reader.read(work.time, work.pulse, derivative)

            dm = DensityMatrix(ksd=self.ksd, matrices=matrices, comm=self.calc_comm)

            yield work, dm


class ConvolutionDensityMatricesFromFrequency(ConvolutionDensityMatrices):

    """
    Collection of density matrices in the Kohn-Sham basis after convolution with
    one or several pulses, for different times. Obtained from the the density
    matrices in frequency space, which are read from disk.

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

         * frho_fmt = ``frho/w{freq:05.2f}-{reim}.npy'``.

        Accepts variables:

         * ``{freq}`` - Frequency in units of eV.
         * ``{reim}`` - ``'Re'`` or ``'Im'`` for Fourier transform of real/imaginary
           part of density matrix.
    perturbation
        Perturbation that was present during time propagation.
    pulses
        Convolute the density matrices with these pulses.
    times
        Compute density matrices for these times (or as close to them as possible). In units of as.
    derivative_order_s
        Compute density matrix derivatives of the following orders.
        `0` for plain density matrix and positive integers for derivatives.
    real
        Calculate real part of density matrices.
    imag
        Calculate imaginary part of density matrices.
    calc_size
        Size of the calculation communicator.
    """

    def __init__(self,
                 ksd: KohnShamDecomposition | str,
                 frho_fmt: str,
                 perturbation: PerturbationLike,
                 pulses: Collection[PerturbationLike],
                 times: list[float] | NDArray[np.float64],
                 derivative_order_s: list[int] = [0],
                 log: Logger | None = None,
                 real: bool = True,
                 imag: bool = True,
                 calc_size: int = 1):
        super().__init__(ksd=ksd, pulses=pulses, times=times,
                         real=real, imag=imag,
                         derivative_order_s=derivative_order_s, calc_size=calc_size, log=log)
        # Frequency grid for convolution
        if not all(pulse.todict()['name'] == 'GaussianPulse' for pulse in self.pulses):
            raise NotImplementedError('Only Gaussian pulses implemented for ResponseFromFourierTransform')

        freq_spacing = 0.05  # 50meV
        freq_min = min((pulse.pulse.omega0 - 4 * pulse.pulse.sigma) * au_to_eV  # type: ignore
                       for pulse in self.pulses)
        freq_min = max(freq_min, freq_spacing)
        freq_max = min((pulse.pulse.omega0 + 4 * pulse.pulse.sigma) * au_to_eV  # type: ignore
                       for pulse in self.pulses)

        transformer = ExactFourierTransformer.from_file(
                frho_fmt=frho_fmt, ksd=ksd, perturbation=perturbation,
                real=real, imag=imag, log=self.log, comm=self.calc_comm,
                freq_spacing=freq_spacing, freq_min=freq_min, freq_max=freq_max)
        self.transformer = transformer

    def __str__(self) -> str:
        lines = ['Response from Fourier transform of density matrices on disk']
        lines.append('')
        lines.append(f'Calculating response for {self.nt} times and {len(self.pulses)} pulses')
        lines.append(f'  times: {format_times(self.times)}')

        return '\n'.join(lines)

    def __iter__(self) -> Generator[tuple[ConvolutionDensityMatrixMetadata, DensityMatrix], None, None]:
        self.transformer.parallel_prepare()

        for work in self.local_work_plan:
            matrices: dict[int, NDArray[np.complex128] | None] = dict()

            for derivative in self.derivative_order_s:
                buffer = self.transformer.convolve(work.time, work.pulse, derivative)
                if self.calc_comm.rank > 0:
                    matrices[derivative] = None
                    continue
                assert buffer is not None
                # Buffer shape is i, a, pulses, times
                if 'Re' in self.reim:
                    Rerho_ia = buffer._get_real(derivative)
                if 'Im' in self.reim:
                    Imrho_ia = buffer._get_imag(derivative)
                if 'Re' in self.reim and 'Im' in self.reim:
                    # Complex result
                    rho_ia = Rerho_ia + 1j * Imrho_ia
                elif 'Re' in self.reim:
                    # Real result
                    rho_ia = Rerho_ia
                else:
                    rho_ia = 1j * Imrho_ia
                matrices[derivative] = rho_ia

            dm = DensityMatrix(ksd=self.ksd, matrices=matrices, comm=self.calc_comm)

            yield work, dm


class ConvolutionDensityMatricesFromWaveFunctions(ConvolutionDensityMatrices):

    """
    Collection of density matrices in the Kohn-Sham basis after convolution with
    one or several pulses, for different times. Obtained from the time-dependent wave functions file,
    which is read from disk.

    Parameters
    ----------
    ksd
        KohnShamDecomposition object or file name.
    wfs_fname
        File name of the time-dependent wave functions file.
    perturbation
        Perturbation that was present during time propagation.
    pulses
        Convolute the density matrices with these pulses.
    times
        Compute density matrices for these times (or as close to them as possible). In units of as.
    derivative_order_s
        Compute density matrix derivatives of the following orders.
        ``0`` for plain density matrix and positive integers for derivatives.
    real
        Calculate real part of density matrices.
    imag
        Calculate imaginary part of density matrices.
    calc_size
        Size of the calculation communicator.
    stridet
        Skip this many steps when reading the time-dependent wave functions file.
    """

    def __init__(self,
                 ksd: KohnShamDecomposition | str,
                 wfs_fname: str,
                 perturbation: PerturbationLike,
                 pulses: Collection[PerturbationLike],
                 times: list[float] | Array1D[np.float64],
                 derivative_order_s: list[int] = [0],
                 real: bool = True,
                 imag: bool = True,
                 calc_size: int = 1,
                 log: Logger | None = None,
                 stridet: int = 1):
        _, calc_size = two_communicator_sizes(-1, calc_size)
        # The calc_comm rank 0's are world ranks 0, with a spacing of calc_size
        result_on_ranks = list(range(0, world.size, calc_size))

        rho_nn_conv = PulseConvolver.from_parameters(
                wfs_fname, ksd,
                pulses=pulses,
                perturbation=perturbation,
                yield_re=real, yield_im=imag,
                filter_times=np.array(times) * as_to_au,
                derivative_order_s=list(sorted(derivative_order_s)),
                stridet=stridet,
                result_on_ranks=result_on_ranks,
                log=log)
        self.rho_nn_conv = rho_nn_conv

        super().__init__(ksd=rho_nn_conv.ksd, pulses=pulses, times=rho_nn_conv.time_t * au_to_as,
                         real=real, imag=imag,
                         derivative_order_s=derivative_order_s, calc_size=calc_size,
                         log=rho_nn_conv.log)

    def __str__(self) -> str:
        lines = []
        lines.append('Response from time-dependent wave functions ')
        lines.append('')
        lines += ['' + line for line in str(self.rho_nn_conv.rho_nn_reader.rho_wfs_reader).split('\n')]
        lines.append('')
        lines += ['' + line for line in str(self.rho_nn_conv.rho_nn_reader).split('\n')]
        lines.append('')
        lines += ['' + line for line in str(self.rho_nn_conv).split('\n')]

        return '\n'.join(lines)

    def get_memory_estimate(self) -> MemoryEstimate:
        return self.rho_nn_conv.get_memory_estimate()

    @property
    def myt(self) -> list[int]:
        """ List of indices corresponding to the time indices on held on this rank. """
        return self.rho_nn_conv.my_work()

    def work_loop(self,
                  rank: int) -> Generator[ConvolutionDensityMatrixMetadata | None, None, None]:
        nt = len(self.times)
        ntperrank = (nt + self.loop_comm.size - 1) // self.loop_comm.size

        for p, pulse in enumerate(self.pulses):
            for localt in range(ntperrank):
                globalt = rank + localt * self.loop_comm.size
                if globalt < nt:
                    yield ConvolutionDensityMatrixMetadata(density_matrices=self, globalt=globalt,
                                                           localt=localt, globalp=p, localp=p)
                else:
                    yield None

    def __iter__(self) -> Generator[tuple[ConvolutionDensityMatrixMetadata, DensityMatrix], None, None]:
        parameters = self.rho_nn_conv.rho_nn_reader._parameters
        flt = (slice(parameters.n1size), slice(parameters.n2size))

        dist_buffer = self.rho_nn_conv.dist_buffer  # Perform the redistribution
        self.ksd.distribute(self.calc_comm)

        if self.calc_comm.rank != 0:
            assert len(self.myt) == 0, self.myt

        for work in self.local_work_plan:
            if self.calc_comm.rank == 0:
                assert self.myt[work.localt] == work.globalt
            localflt = flt + (work.localp, work.localt)

            matrices: dict[int, NDArray[np.complex128] | None] = dict()
            for derivative in self.derivative_order_s:
                if self.calc_comm.rank > 0:
                    matrices[derivative] = None
                    continue
                # Buffer shape is i, a, pulses, times
                if 'Re' in self.reim:
                    Rerho_ia = dist_buffer._get_real(derivative)[localflt]
                if 'Im' in self.reim:
                    Imrho_ia = dist_buffer._get_imag(derivative)[localflt]
                if 'Re' in self.reim and 'Im' in self.reim:
                    # Complex result
                    # Compared to numpy, we use another convention, hence the minus sign
                    rho_ia = Rerho_ia - 1j * Imrho_ia
                elif 'Re' in self.reim:
                    # Real result
                    rho_ia = Rerho_ia
                else:
                    rho_ia = -1j * Imrho_ia
                matrices[derivative] = rho_ia
            dm = DensityMatrix(ksd=self.ksd, matrices=matrices, comm=self.calc_comm)

            yield work, dm

    def parallel_prepare(self):
        self.rho_nn_conv.dist_buffer  # Perform the redistribution


class ExactFourierTransformer:

    def __init__(self,
                 reader: FrequencyDensityMatrixReader,
                 perturbation: PerturbationLike,
                 real: bool = True,
                 imag: bool = True,
                 comm: Communicator | None = None,
                 log: Logger | None = None):
        if comm is None:
            comm = world
        self._comm = comm
        self.reader = reader
        if log is None:
            log = Logger()
        self.log = log

        self.real = real
        self.imag = imag

        self.frequency_buffer = DensityMatrixBuffer(self.nnshape, (self.reader.nw, ), np.complex128)
        self._ready = False

        omega_w = self.reader.frequencies * eV_to_au

        self.perturbation = create_perturbation(perturbation)
        assert isinstance(self.perturbation, DeltaKick)

        # Need a uniform spacing for Simpson's integration rule
        dw = omega_w[1] - omega_w[0]
        nw = len(omega_w)
        if not np.allclose(omega_w[1:] - dw, omega_w[:-1]):
            raise ValueError('Variable frequency spacing.')
        # integration weights from Simpson's integration rule
        self._weight_w = dw / 3 * np.array([1] + [4, 2] * int((nw - 2) / 2)
                                           + [4] * (nw % 2) + [1])

        self._weight_w *= 2 / (2 * np.pi)
        self._weight_w /= self.perturbation.strength

    @property
    def comm(self) -> Communicator:
        """ MPI commonicator.

        During convolution, the density matrices are distributed with
        different chunks on different ranks of this communicator.
        """
        return self._comm

    @property
    def full_nnshape(self) -> tuple[int, int]:
        imin, imax, amin, amax = [int(i) for i in self.reader.ksd.ialims()]
        return (imax - imin + 1, amax - amin + 1)

    @property
    def nnshape(self) -> tuple[int, int]:
        stridei = (self.full_nnshape[0] + self.comm.size - 1) // self.comm.size
        return (stridei, self.full_nnshape[1])

    @property
    def myslice(self) -> slice:
        return self.slice_of_rank(self.comm.rank)

    def slice_of_rank(self, rank: int) -> slice:
        stridei = (self.full_nnshape[0] + self.comm.size - 1) // self.comm.size
        return slice(rank * stridei, (rank + 1) * stridei)

    def parallel_prepare(self):
        # Read all the Fourier transform of density matrices
        self.frequency_buffer.zero_buffers(real=self.real, imag=self.imag, derivative_order_s=[0])
        for w, freq in enumerate(self.reader.frequencies):
            if self.real:
                rho_ia = self.reader.read(frequency=freq, real=True)[self.myslice]
                self.frequency_buffer[w].real[:len(rho_ia)] = rho_ia
            if self.imag:
                rho_ia = self.reader.read(frequency=freq, real=False)[self.myslice]
                self.frequency_buffer[w].imag[:len(rho_ia)] = rho_ia
        self._ready = True

    def convolve(self,
                 time: float,
                 pulse: Perturbation,
                 derivative: int) -> DensityMatrixBuffer | None:
        if not self._ready:
            self.parallel_prepare()

        assert isinstance(pulse, PulsePerturbation)
        omega_w = self.reader.frequencies * eV_to_au
        pulse_w = pulse.pulse.fourier(omega_w)

        buffer = DensityMatrixBuffer(self.frequency_buffer.nnshape, (), dtype=np.float64)

        self.log.start('convolve')
        exp_w = np.exp(-1j * omega_w * time * as_to_au)
        exp_w *= self._weight_w * pulse_w * (-1j * omega_w) ** derivative

        if self.real:
            # Real part
            rho_iaw = self.frequency_buffer.real[:]
            conv_rho_ia = rho_iaw.real @ exp_w.real
            conv_rho_ia -= rho_iaw.imag @ exp_w.imag

            buffer.store(True, derivative, conv_rho_ia)

        if self.imag:
            # Imaginary part
            rho_iaw = self.frequency_buffer.imag[:]
            conv_rho_ia = rho_iaw.real @ exp_w.real
            conv_rho_ia -= rho_iaw.imag @ exp_w.imag

            buffer.store(False, derivative, conv_rho_ia)

        if self.comm.rank == 0:
            full_buffer = DensityMatrixBuffer(self.frequency_buffer.nnshape, (), dtype=np.float64)
            full_buffer.zero_buffers(real=self.real, imag=self.imag, derivative_order_s=[derivative])

        # Send to root
        for rank in range(self.comm.size):
            if rank == self.comm.rank:
                # Send own work to root
                buffer.send_arrays(self.comm, 0)

            if self.comm.rank == 0:
                # Receive on root, fill buffer
                buffer.recv_arrays(self.comm, rank)
                for full_rho_ia, part_rho_ia in zip(full_buffer._iter_buffers(),
                                                    buffer._iter_buffers()):
                    full_slice_ia = full_rho_ia[self.slice_of_rank(rank)]
                    full_slice_ia[:] = part_rho_ia[:len(full_slice_ia)]

        if self.comm.rank == 0:
            self.log(f'Convolved density matrices in {self.log.elapsed("convolve"):.1f} s',
                     who='Response', flush=True)

        if self.comm.rank == 0:
            return full_buffer

        return None

    @classmethod
    def from_file(cls,
                  frho_fmt: str,
                  ksd: KohnShamDecomposition | str,
                  perturbation: PerturbationLike,
                  freq_min: float,
                  freq_spacing: float,
                  freq_max: float,
                  real: bool = True,
                  imag: bool = True,
                  comm: Communicator | None = None,
                  log: Logger | None = None) -> ExactFourierTransformer:
        frequencies = np.arange(freq_min, freq_max + freq_spacing * 0.1, freq_spacing)

        reader = FrequencyDensityMatrixReader(frho_fmt=frho_fmt,
                                              ksd=ksd,
                                              filter_frequencies=frequencies,
                                              real=real, imag=imag,
                                              comm=None,  # Look for files on world
                                              log=log)
        if reader.frequencies[0] > freq_min:
            raise ValueError(f'Could not satisfy lower bound for frequency grid with files matching {frho_fmt}. '
                             f'Found {reader.frequencies[0]:.2f}eV, reqested {freq_min:.2f}eV.')

        if reader.frequencies[-1] > freq_max:
            raise ValueError(f'Could not satisfy upper bound for frequency grid with files matching {frho_fmt}. '
                             f'Found {reader.frequencies[-1]:.2f}eV, reqested {freq_max:.2f}eV.')

        dw = reader.frequencies[1] - reader.frequencies[0]
        if dw > freq_spacing + 1e-8:
            raise ValueError(f'Could not construct sufficiently dense frequency grid with files matching {frho_fmt}. '
                             f'Found spacing of {dw:.4f}eV, reqested {freq_spacing:.4f}eV.')

        return cls(reader=reader, perturbation=perturbation, real=real, imag=imag, comm=comm, log=log)
