from __future__ import annotations

from abc import abstractmethod, ABC
from typing import Generator, Collection

import numpy as np

from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition

from ..perturbation import create_perturbation, Perturbation, PerturbationLike
from ..density_matrices.density_matrix import DensityMatrix
from ..density_matrices.frequency import (FrequencyDensityMatrixMetadata,
                                          FrequencyDensityMatrices)
from ..density_matrices.time import (ConvolutionDensityMatrixMetadata,
                                     ConvolutionDensityMatrices)
from ..typing import Array1D
from ..utils import add_fake_kpts, Logger


class BaseResponse(ABC):

    """ Object describing response; obtained from :term:`TDDFT` calculation.

    Parameters
    ----------
    ksd
        KohnShamDecomposition object or file name.
    perturbation
        The perturbation that was present during the TDDFT calculation.
        None to mark it as an ne perturbation.
    calc_size
        Size of the calculation communicator.
    """
    def __init__(self,
                 ksd: KohnShamDecomposition | str,
                 perturbation: PerturbationLike = None,
                 calc_size: int = 1):
        if isinstance(ksd, KohnShamDecomposition):
            self._ksd = ksd
        else:
            self._ksd = KohnShamDecomposition(filename=ksd)
        add_fake_kpts(self._ksd)

        self._perturbation = create_perturbation(perturbation)
        self.calc_size = calc_size

    def __str__(self) -> str:
        lines = [f'{self.__class__.__name__}']
        lines += [f'  ksd: {self.ksd.filename if self.ksd.filename is not None else "From calc"}']
        lines += ['  perturbation:']
        lines += ['    ' + line for line in str(self.perturbation).split('\n')]
        return '\n'.join(lines)

    @property
    def ksd(self) -> KohnShamDecomposition:
        """ Kohn-Sham decomposition object. """
        return self._ksd

    @property
    def perturbation(self) -> Perturbation:
        """ The perturbation that caused this response. """
        return self._perturbation

    @abstractmethod
    def _get_time_density_matrices(self,
                                   times: list[float] | Array1D[np.float64],
                                   pulses: Collection[PerturbationLike],
                                   derivative_order_s: list[int] = [0],
                                   real: bool = True,
                                   imag: bool = True,
                                   log: Logger | None = None,
                                   ) -> ConvolutionDensityMatrices:
        raise NotImplementedError

    @abstractmethod
    def _get_frequency_density_matrices(self,
                                        frequencies: list[float] | Array1D[np.float64],
                                        frequency_broadening: float = 0,
                                        real: bool = True,
                                        imag: bool = True,
                                        log: Logger | None = None,
                                        ) -> FrequencyDensityMatrices:
        raise NotImplementedError

    def iterate_density_matrices_in_time(self,
                                         times: list[float] | Array1D[np.float64],
                                         pulses: Collection[PerturbationLike],
                                         derivative_order_s: list[int] = [0],
                                         real: bool = True,
                                         imag: bool = True,
                                         log: Logger | None = None,
                                         ) -> Generator[tuple[ConvolutionDensityMatrixMetadata,
                                                              DensityMatrix], None, None]:
        """ Obtain density matrices at the given times in response to the given pulses.

        If the given pulse(s) differ from the perturbation that caused this response,
        then the pulse convolution trick is applied to obtain the response to the given
        pulse(s).

        Parameters
        ----------
        times
            Calculate density matrices for these times (or as close to them as possible). In units of as.
        pulses
            Calculate density matrices in response to these pulses.
        derivative_order_s
            Calculate density matrix derivatives of the following orders.
            ``0`` for plain density matrix and positive integers for derivatives.
        real
            Calculate the real part of density matrices.
        imag
            Calculate the imaginary part of density matrices.
        log
            Logger object.

        Yields
        ------
        Tuple (work, dm) on the root rank of the calculation communicator:

            work
                An object representing the metadata (time and pulse) for the work done.
            dm
                Density matrix for this time and pulse.
        """
        density_matrices = self._get_time_density_matrices(
                times, pulses, derivative_order_s, real, imag, log)
        yield from density_matrices

    def iterate_density_matrices_in_frequency(self,
                                              frequencies: list[float] | Array1D[np.float64],
                                              frequency_broadening: float = 0,
                                              real: bool = True,
                                              imag: bool = True,
                                              log: Logger | None = None,
                                              ) -> Generator[tuple[FrequencyDensityMatrixMetadata,
                                                                   DensityMatrix], None, None]:
        """ Obtain density matrices at the given frequencies.

        Parameters
        ----------
        frequencies
            Compute density matrices for these frequencies (or as close to them as possible). In units of eV.
        frequency_broadening
            Gaussian broadening width in atomic units. Default (0) is no broadening.
        real
            Calculate the Fourier transform of the real part of the density matrix.
        imag
            Calculate the Fourier transform of the imaginary part of the density matrix.

        Yields
        ------
        Tuple (work, dm) on the root rank of the calculation communicator:

            work
                An object representing the metadata (frequency) for the work done.
            dm
                Density matrix for this frequency.
        """
        density_matrices = self._get_frequency_density_matrices(
                frequencies, frequency_broadening, real, imag, log)
        yield from density_matrices

    def write_in_time(self,
                      pulserho_fmt: str,
                      times: list[float] | Array1D[np.float64],
                      pulses: Collection[PerturbationLike],
                      derivative_order_s: list[int] = [0],
                      real: bool = True,
                      imag: bool = True,
                      log: Logger | None = None):
        density_matrices = self._get_time_density_matrices(
                times, pulses, derivative_order_s, real, imag, log)
        density_matrices.write_to_disk(pulserho_fmt)

    def write_in_frequency(self,
                           frho_fmt: str,
                           frequencies: list[float] | Array1D[np.float64],
                           frequency_broadening: float = 0,
                           real: bool = True,
                           imag: bool = True,
                           log: Logger | None = None):
        density_matrices = self._get_frequency_density_matrices(
                frequencies, frequency_broadening, real, imag, log)
        density_matrices.write_to_disk(frho_fmt)
