from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generator, Collection

import numpy as np
from numpy.typing import NDArray

from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition
from gpaw.mpi import world

from ..typing import Communicator, Array2D, Array3D
from ..response import BaseResponse
from ..perturbation import create_perturbation, Perturbation, PerturbationLike
from ..density_matrices.base import BaseDensityMatrices, WorkMetadata
from ..density_matrices.time import ConvolutionDensityMatrices
from ..density_matrices.frequency import FrequencyDensityMatrices
from ..voronoi import VoronoiWeights, EmptyVoronoiWeights
from ..typing import Array1D
from ..utils import Logger, ResultKeys, Result, broaden_n2e, broaden_xn2e, broaden_ia2ou
from ..utils.memory import HasMemoryEstimate, MemoryEstimate


class BaseObservableCalculator(HasMemoryEstimate, ABC):

    """ Object of this class compute observables.

    Parameters
    ----------
    response
        Response object.
    voronoi
        Voronoi weights object.
    energies_occ
        Energy grid in units of eV for occupied levels (holes).
    energies_unocc
        Energy grid in units of eV for unoccupied levels (electrons).
    sigma
        Gaussian broadening width for energy grid in units of eV.
    times
        Compute observables in the time domain, for these times (or as close to them as possible).
        In units of as.

        May not be used together with :attr:`frequencies` or :attr:`frequency_broadening`.
    pulses
        Compute observables in the time domain, in response to these pulses.
        If none, then no pulse convolution is performed.

        May not be used together with :attr:`frequencies` or :attr:`frequency_broadening`.
    frequencies
        Compute observables in the frequency domain, for these frequencies. In units of eV.

        May not be used together with :attr:`times` or :attr:`pulses`.
    frequency_broadening
        Compute observables in the frequency domain, with Gaussian broadening of this width.
        In units of eV.

        May not be used together with :attr:`times` or :attr:`pulses`.
    """

    def __init__(self,
                 response: BaseResponse,
                 voronoi: VoronoiWeights | None = None,
                 *,
                 energies_occ: list[float] | Array1D[np.float64] | None = None,
                 energies_unocc: list[float] | Array1D[np.float64] | None = None,
                 sigma: float | None = None,
                 times: list[float] | Array1D[np.float64] | None = None,
                 pulses: Collection[PerturbationLike] | None = None,
                 frequencies: list[float] | Array1D[np.float64] | None = None,
                 frequency_broadening: float = 0,
                 ):
        self._log = Logger()
        self.log.startup_message()
        world.barrier()
        self._response = response

        self._is_time_density_matrices: bool
        if times is not None:
            if frequencies is not None or frequency_broadening != 0:
                raise ValueError('The parameters frequencies and frequency_broadening may not '
                                 'be used together with times and pulses.')
            # Time calculator
            if pulses is None:
                pulses = [None]  # No perturbation
            pulses = [create_perturbation(pulse) for pulse in pulses]
            self._is_time_density_matrices = True
        else:
            if frequencies is None:
                raise ValueError('One of the parameters times or frequencies must be given.')
            if pulses is not None:
                raise ValueError('The parameters frequencies and frequency_broadening may not '
                                 'be used together with times and pulses.')
            # Frequency calculator
            self._is_time_density_matrices = False

        derivatives, real, imag = self._need_derivatives_real_imag

        density_matrices: BaseDensityMatrices
        if self._is_time_density_matrices:
            assert times is not None
            assert pulses is not None
            density_matrices = response._get_time_density_matrices(
                    times, pulses, derivatives, real, imag, self.log)
        else:
            assert pulses is None
            assert frequencies is not None
            density_matrices = response._get_frequency_density_matrices(
                    frequencies, frequency_broadening, real, imag, self.log)

        self._density_matrices = density_matrices
        self._voronoi: VoronoiWeights
        if voronoi is None:
            self._voronoi = EmptyVoronoiWeights()
        else:
            self._voronoi = voronoi
        if energies_occ is None:
            energies_occ = []
        if energies_unocc is None:
            energies_unocc = []
        self._energies_occ = np.asarray(energies_occ)
        self._energies_unocc = np.asarray(energies_unocc)
        self._sigma = sigma
        self._weight_In: Array2D[np.float64] | None = None
        self._weight_Iii: Array3D[np.float64] | None = None
        self._weight_Iaa: Array3D[np.float64] | None = None
        world.barrier()
        self.log(f'Set up calculator:\n'
                 f'{self}\n\n'
                 '==================================\n'
                 ' Procedure for obtaining response \n'
                 '==================================\n'
                 f'{self.density_matrices}\n\n'
                 '=================\n'
                 ' Memory estimate \n'
                 '=================\n'
                 f'{self.get_memory_estimate()}\n',
                 rank=0)

    def __str__(self) -> str:
        lines = [f' {self.__class__.__name__} ']

        lines.append('response:')
        lines += ['  ' + line for line in str(self.response).split('\n')]
        lines.append('')

        lines.append('voronoi:')
        if self.nproj == 0:
            lines.append('  No Voronoi decomposition')
        else:
            lines += ['  ' + line for line in str(self.voronoi).split('\n')]
        lines.append('')

        if len(self.energies_occ) == 0 or len(self.energies_unocc) == 0 or self.sigma is None:
            lines.append('No energies for broadening')
        else:
            lines += [f'Energies for broadening (sigma = {self.sigma:.1f} eV)',
                      f'  Occupied: {len(self.energies_occ)} from '
                      f'{self.energies_occ[0]:.1f} to {self.energies_occ[-1]:.1f} eV',
                      f'  Unoccupied: {len(self.energies_unocc)} from '
                      f'{self.energies_unocc[0]:.1f} to {self.energies_unocc[-1]:.1f} eV',
                      ]

        # Make a cute frame
        maxlen = max(len(line) for line in lines)
        lines[0] = '{s:=^{n}}'.format(s=f' {lines[0]} ', n=maxlen)
        lines.append(maxlen * '-')

        return '\n'.join(lines)

    def get_memory_estimate(self) -> MemoryEstimate:
        memory_estimate = MemoryEstimate()
        memory_estimate.add_child('Reading response', self.density_matrices.get_memory_estimate())
        for key, shape in self._voronoi_shapes.items():
            memory_estimate.add_key(f'Voronoi weights {key}', shape, float,
                                    on_num_ranks=self.loop_comm.size)

        return memory_estimate

    @property
    def response(self) -> BaseResponse:
        """ Response object """
        return self._response

    @property
    def density_matrices(self) -> BaseDensityMatrices:
        """ Object that gives the density matrix in the time or freqency domain. """
        return self._density_matrices

    @property
    def nproj(self) -> int:
        """ Number of projections in the Voronoi weights object """
        return self.voronoi.nproj

    @property
    def voronoi(self) -> VoronoiWeights:
        """ Voronoi weights object """
        return self._voronoi

    @property
    def energies_occ(self) -> NDArray[np.float64]:
        """ Energy grid (in units of eV) for occupied levels (hot holes). """
        return self._energies_occ

    @property
    def energies_unocc(self) -> NDArray[np.float64]:
        """ Energy grid (in units of eV) for unoccupied levels (hot electrons). """
        return self._energies_unocc

    @property
    def sigma(self) -> float | None:
        """ Gaussian broadening width in units of eV. """
        return self._sigma

    @property
    def ksd(self) -> KohnShamDecomposition:
        """ Kohn-Sham decomposition object """
        return self.density_matrices.ksd

    @property
    def log(self) -> Logger:
        """ Logger """
        return self._log

    def log_parallel(self, *args, **kwargs) -> Logger:
        """ Log message with communicator information. """
        return self._log(*args, **kwargs, comm=self.loop_comm, who='Calculator')

    @property
    def frequencies(self) -> Array1D[np.float64]:
        """ Frequencies (in units of eV) at which the density matrices are evaluated.

        Only valid when the density matrices object is defined in the frequency domain. """
        assert isinstance(self.density_matrices, FrequencyDensityMatrices)
        return self.density_matrices.frequencies

    @property
    def frequency_broadening(self) -> float:
        """ Value of frequency broadening in units of eV.

        Only valid when the density matrices object is defined in the frequency domain. """
        assert isinstance(self.density_matrices, FrequencyDensityMatrices)
        return self.density_matrices.frequency_broadening

    @property
    def times(self) -> Array1D[np.float64]:
        """ Times (in units of as) at which the density matrices are evaluated.

        Only valid when the density matrices object is defined in the time domain. """
        assert isinstance(self.density_matrices, ConvolutionDensityMatrices)
        return self.density_matrices.times

    @property
    def pulses(self) -> list[Perturbation]:
        """ List of pulses which the density matrices are responses to.

        Only valid when the density matrices object is a convolution with pulses. """
        assert isinstance(self.density_matrices, ConvolutionDensityMatrices)
        return self.density_matrices.pulses

    @property
    def calc_comm(self) -> Communicator:
        """ Calculation communicator.

        Each rank of this communicator calculates the observables corresponding to
        a part (in electron-hole space) of the density matrices. """
        return self.density_matrices.calc_comm

    @property
    def loop_comm(self) -> Communicator:
        """ Loop communicator.

        Each rank of this communicator calculates the density matrices corresponding to
        different times, frequencies or after convolution with a different pulse. """
        return self.density_matrices.loop_comm

    @property
    def eig_n(self) -> Array1D[np.float64]:
        """ Eigenvalues (in units of eV) relative to Fermi level in the full ground state KS basis. """
        eig_n, _ = self.ksd.get_eig_n(zero_fermilevel=True)
        return eig_n  # type: ignore

    @property
    def eig_i(self) -> Array1D[np.float64]:
        """ Eigenvalues (in units of eV) relative to Fermi level of occupied states (holes). """
        return self.eig_n[self.flti]  # type: ignore

    @property
    def eig_a(self) -> Array1D[np.float64]:
        """ Eigenvalues (in units of eV) relative to Fermi level of unoccupied states (electrons). """
        return self.eig_n[self.flta]  # type: ignore

    @property
    def flti(self) -> slice:
        """ Slice for extracting indices corresponding to occupied states. """
        imin, imax, _, _ = self.ksd.ialims()
        return slice(imin, imax+1)

    @property
    def flta(self) -> slice:
        """ Slice for extracting indices corresponding to unoccupied states. """
        _, _, amin, amax = self.ksd.ialims()
        return slice(amin, amax+1)

    @property
    def _need_derivatives_real_imag(self) -> tuple[list[int], bool, bool]:
        """ Derivatives needed by this calculator, and
        whether real and imaginary parts are needed
        """
        raise NotImplementedError

    @property
    def _voronoi_shapes(self) -> dict[str, tuple[int, ...]]:
        """ List of shapes for the Voronoi weights stored on this calculator. """
        return {}

    def _read_weights_diagonal(self) -> None:
        """ Read the diagonal weights from the voronoi object and store them in memory. """
        nI = self.voronoi.nproj
        if nI == 0:
            return
        Nn = self.voronoi.nn

        if self.calc_comm.rank == 0:
            weight_In = np.empty((nI, Nn), dtype=float)
        else:
            weight_In = None
        for iI, weight_nn in enumerate(self.voronoi):
            if self.voronoi.comm.rank == 0:
                assert weight_In is not None
                assert weight_nn is not None
                weight_In[iI, ...] = weight_nn.diagonal()
            else:
                assert weight_nn is None

        if self.calc_comm.rank == 0:
            # Broadcast to all calc_comm rank 0's
            self.loop_comm.broadcast(weight_In, 0)

        self._weight_In = weight_In

    def _read_weights_eh(self) -> None:
        """ Read the electron-hole weights from the voronoi object and store them in memory. """
        nI = self.voronoi.nproj
        if nI == 0:
            return

        if self.calc_comm.rank == 0:
            weight_Iii = np.empty((nI, len(self.eig_i), len(self.eig_i)), dtype=float)
            weight_Iaa = np.empty((nI, len(self.eig_a), len(self.eig_a)), dtype=float)
        else:
            weight_Iii = None
            weight_Iaa = None
        for iI, weight_nn in enumerate(self.voronoi):
            if self.voronoi.comm.rank == 0:
                assert weight_nn is not None
                assert weight_Iii is not None
                assert weight_Iaa is not None
                weight_Iii[iI, ...] = weight_nn[self.flti, self.flti]
                weight_Iaa[iI, ...] = weight_nn[self.flta, self.flta]
            else:
                assert weight_nn is None

        if self.calc_comm.rank == 0:
            # Broadcast to all calc_comm rank 0's
            self.loop_comm.broadcast(weight_Iii, 0)
            self.loop_comm.broadcast(weight_Iaa, 0)

        self._weight_Iii = weight_Iii
        self._weight_Iaa = weight_Iaa

    @property
    def _iterate_weights_diagonal(self) -> Generator[NDArray[np.float64], None, None]:
        """ Iterate over the diagonal weights.

        Yields
        ------
        The diagonal of the Voronoi weights, one projection at a time """
        assert self.calc_comm.rank == 0
        if self.nproj == 0:
            return

        if self._weight_In is None:
            self._read_weights_diagonal()
        assert self._weight_In is not None

        for weight_n in self._weight_In:
            yield weight_n

    @property
    def _iterate_weights_eh(self) -> Generator[tuple[NDArray[np.float64], NDArray[np.float64]], None, None]:
        """ Iterate over the electron-hole part of the weights.

        Yields
        ------
        The electron-hole part of the Voronoi weights, one projection at a time """
        assert self.calc_comm.rank == 0
        if self.nproj == 0:
            return

        if self._weight_Iaa is None or self._weight_Iii is None:
            self._read_weights_eh()
        assert self._weight_Iii is not None
        assert self._weight_Iaa is not None

        for weight_ii, weight_aa in zip(self._weight_Iii, self._weight_Iaa):
            yield weight_ii, weight_aa

    @abstractmethod
    def get_result_keys(self) -> ResultKeys:
        """ Get the keys that each result will contain, and dimensions thereof.

        Returns
        -------
        Object representing the data that will be present in the result objects. """
        raise NotImplementedError

    @abstractmethod
    def icalculate(self) -> Generator[tuple[WorkMetadata, Result], None, None]:
        """ Iteratively calculate results.

        Yields
        ------
        Tuple (work, result) on the root rank of the calculation communicator:

        work
            An object representing the metadata (time, frequency or pulse) for the work done
        result
            Object containg the calculation results for this time, frequency or pulse

        Yields nothing on non-root ranks of the calculation communicator.
        """
        raise NotImplementedError

    def icalculate_gather_on_root(self, **kwargs) -> Generator[
            tuple[WorkMetadata, Result], None, None]:
        """ Iteratively calculate results and gather to the root rank.

        Yields
        ------
        Tuple (work, result) on the root rank of the both calculation and loop communicators:

        work
            An object representing the metadata (time, frequency or pulse) for the work done
        result
            Object containg the calculation results for this time, frequency or pulse

        Yields nothing on non-root ranks of the communicators.
        """
        resultkeys = self.get_result_keys(**kwargs)
        gen = iter(self.icalculate(**kwargs))

        # Loop over the work to be done, and the ranks that are supposed to do it
        for rank, work in self.density_matrices.global_work_loop_with_idle():
            if work is None:
                # Rank rank will not do any work at this point
                continue

            if self.calc_comm.rank > 0:
                continue

            if self.loop_comm.rank == 0 and rank == 0:
                # This is the root rank, and the root rank should yield its own work
                mywork, result = next(gen)
                assert work.global_indices == mywork.global_indices, f'{work.desc} != {mywork.desc}'
                yield mywork, result
                # self.log.start('communicate')
            elif self.loop_comm.rank == 0:
                # This is the root rank, and the root rank should receive the work
                # done by rank rank, and yield that
                result.inplace_receive(resultkeys, rank, comm=self.loop_comm)
                yield work, result
                # self.log(f'Communicated for {self.log.elapsed("communicate"):.2f}s', flush=True)
            elif self.loop_comm.rank == rank:
                # This is not the root rank, but this rank should send its data to root
                _, result = next(gen)
                result.send(resultkeys, 0, comm=self.loop_comm)

        _exhausted = object()
        rem = next(gen, _exhausted)
        assert rem is _exhausted, rem

    def write_response_to_disk(self,
                               fmt: str):
        """ Calculate the response needed for this calculator and write the response to disk.

        The necessary derivatives and real and imaginary parts of the density matrices
        will be written. Can be used both in the time and frequency domains.

        Parameters
        ----------
        fmt
            Formatting string for the density matrices saved to disk.

            The formatting string should be a plain string containing variable
            placeholders within curly brackets ``{}``. It should not be confused with
            a formatted string literal (f-string).

            Examples:

             * frho_fmt = ``'frho/w{freq:05.2f}-{reim}.npy'``.
             * pulserho_fmt =  ``pulserho/t{time:09.1f}{tag}.npy``.

            Accepts variables in the time domain:

             * ``{time}`` - Time in units of as.
             * ``{tag}`` - Derivative tag, ``''``, ``'-Iomega'``, or ``'-omega2'``.
             * ``{pulsefreq}`` - Pulse frequency in units of eV.
             * ``{pulsefwhm}`` - Pulse FWHM in units of fs.

            Accepts variables in the frequency domain:

             * ``{freq}`` - Frequency in units of eV.
             * ``{reim}`` - ``'Re'`` or ``'Im'`` for Fourier transform of real/imaginary
               part of density matrix.
        """
        self._density_matrices.write_to_disk(fmt)

    def broaden_occ(self,
                    M_i: NDArray[np.float64]) -> NDArray[np.float64]:
        """ Broaden array corresponding to occupied levels with Gaussians of width sigma

        Parameters
        ----------
        M_i
            Array to broaden

        Returns
        -------
        Broadened array
        """
        assert self.sigma is not None

        return broaden_n2e(M_i, self.eig_i, self.energies_occ, self.sigma)

    def broaden_unocc(self,
                      M_a: NDArray[np.float64]) -> NDArray[np.float64]:
        """ Broaden array corresponding to unoccupied levels with Gaussians of width sigma

        Parameters
        ----------
        M_a
            Array to broaden

        Returns
        -------
            Broadened array
        """
        assert self.sigma is not None

        return broaden_n2e(M_a, self.eig_a, self.energies_unocc, self.sigma)

    def broaden_xi2o(self,
                     M_xi: NDArray[np.float64]) -> NDArray[np.float64]:
        """ Broaden array corresponding to occupied levels with Gaussians of width sigma

        Parameters
        ----------
        M_xa
            Array to broaden. The last dimension should correspond to the occupied levels

        Returns
        -------
        Broadened array
        """
        assert self.sigma is not None

        return broaden_xn2e(M_xi, self.eig_i, self.energies_occ, self.sigma)

    def broaden_xi2u(self,
                     M_xa: NDArray[np.float64]) -> NDArray[np.float64]:
        """ Broaden array corresponding to unoccupied levels with Gaussians of width sigma

        Parameters
        ----------
        M_xa
            Array to broaden. The last dimension should correspond to the unoccupied levels

        Returns
        -------
            Broadened array
        """
        assert self.sigma is not None

        return broaden_xn2e(M_xa, self.eig_a, self.energies_unocc, self.sigma)

    def broaden_ia2ou(self,
                      M_ia: NDArray[np.float64]) -> NDArray[np.float64]:
        """ Broaden matrix in electron-hole basis with Gaussians of width sigma.

        Parameters
        ----------
        M_ia
            Matrix to broaden. The first dimension should correspond to occupied levels
            and the second to unoccupied levels.

        Returns
        -------
            Broadened array
        """
        assert self.sigma is not None

        return broaden_ia2ou(M_ia, self.eig_i, self.eig_a,
                             self.energies_occ, self.energies_unocc, self.sigma)
