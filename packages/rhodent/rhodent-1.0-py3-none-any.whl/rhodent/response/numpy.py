from __future__ import annotations

from typing import Collection

import numpy as np

from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition

from .base import BaseResponse
from ..perturbation import DeltaKick, PerturbationLike, NoPerturbation
from ..density_matrices.frequency import (FrequencyDensityMatrices,
                                          FrequencyDensityMatricesFromDisk)
from ..density_matrices.time import (ConvolutionDensityMatricesFromDisk,
                                     ConvolutionDensityMatricesFromFrequency,
                                     ConvolutionDensityMatrices)
from ..utils import Logger
from ..typing import Array1D


class ResponseFromDensityMatrices(BaseResponse):

    """ Response from density matrices saved on disk.

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
    ksd
        KohnShamDecomposition object or file name.
    perturbation
        Perturbation that was present during time propagation.
    calc_size
        Size of the calculation communicator.
    """

    def __init__(self,
                 pulserho_fmt: str,
                 ksd: KohnShamDecomposition | str,
                 perturbation: PerturbationLike = None,
                 calc_size: int = 1):
        super().__init__(ksd=ksd,
                         perturbation=perturbation,
                         calc_size=calc_size)
        self.pulserho_fmt = pulserho_fmt

    def __str__(self) -> str:
        lines = [f'{self.__class__.__name__}']
        lines += [f'  ksd: {self.ksd.filename if self.ksd.filename is not None else "From calc"}']
        lines += [f'  pulserho_fmt: {self.pulserho_fmt}']
        lines += ['  perturbation:']
        lines += ['    ' + line for line in str(self.perturbation).split('\n')]
        return '\n'.join(lines)

    def _get_time_density_matrices(self,
                                   times: list[float] | Array1D[np.float64],
                                   pulses: Collection[PerturbationLike],
                                   derivative_order_s: list[int] = [0],
                                   real: bool = True,
                                   imag: bool = True,
                                   log: Logger | None = None,
                                   ) -> ConvolutionDensityMatrices:
        if (len(pulses) == 1 and list(pulses)[0] == self.perturbation) or isinstance(self.perturbation, NoPerturbation):
            # Yield the density matrices without performing convolution
            density_matrices = ConvolutionDensityMatricesFromDisk(
                     ksd=self.ksd,
                     pulserho_fmt=self.pulserho_fmt,
                     times=times,
                     pulses=pulses,
                     derivative_order_s=derivative_order_s,
                     real=real,
                     imag=imag,
                     log=log,
                     calc_size=self.calc_size)
        else:
            raise NotImplementedError('Pulse convolution of density matrices on disk is not implemented')

        return density_matrices

    def _get_frequency_density_matrices(self,
                                        frequencies: list[float] | Array1D[np.float64],
                                        frequency_broadening: float = 0,
                                        real: bool = True,
                                        imag: bool = True,
                                        log: Logger | None = None,
                                        ) -> FrequencyDensityMatrices:
        raise NotImplementedError('Fourier transformation of density matrices on disk is not implemented')


class ResponseFromFourierTransform(BaseResponse):

    """ Response from Fourier transform of density matrices save on disk.

    Parameters
    ----------
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
    ksd
        KohnShamDecomposition object or file name.
    perturbation
        Perturbation that was present during time propagation.
    calc_size
        Size of the calculation communicator.
    """

    def __init__(self,
                 frho_fmt: str,
                 ksd: KohnShamDecomposition | str,
                 perturbation: PerturbationLike = None,
                 calc_size: int = 1):
        super().__init__(ksd=ksd,
                         perturbation=perturbation,
                         calc_size=calc_size)

        if not isinstance(self.perturbation, (DeltaKick, NoPerturbation)):
            raise NotImplementedError('Only delta kick implemented')

        self.frho_fmt = frho_fmt

    def __str__(self) -> str:
        lines = [f'{self.__class__.__name__}']
        lines += [f'  ksd: {self.ksd.filename if self.ksd.filename is not None else "From calc"}']
        lines += [f'  frho_fmt: {self.frho_fmt}']
        lines += ['  perturbation:']
        lines += ['    ' + line for line in str(self.perturbation).split('\n')]
        return '\n'.join(lines)

    def _get_time_density_matrices(self,
                                   times: list[float] | Array1D[np.float64],
                                   pulses: Collection[PerturbationLike],
                                   derivative_order_s: list[int] = [0],
                                   real: bool = True,
                                   imag: bool = True,
                                   log: Logger | None = None,
                                   ) -> ConvolutionDensityMatrices:
        if not isinstance(self.perturbation, DeltaKick):
            raise NotImplementedError('Only delta kick implemented')

        density_matrices = ConvolutionDensityMatricesFromFrequency(
            ksd=self.ksd,
            frho_fmt=self.frho_fmt,
            perturbation=self.perturbation,
            pulses=pulses,
            times=times,
            derivative_order_s=derivative_order_s,
            real=real,
            imag=imag,
            log=log,
            calc_size=self.calc_size)

        return density_matrices

    def _get_frequency_density_matrices(self,
                                        frequencies: list[float] | Array1D[np.float64],
                                        frequency_broadening: float = 0,
                                        real: bool = True,
                                        imag: bool = True,
                                        log: Logger | None = None,
                                        ) -> FrequencyDensityMatrices:
        if frequency_broadening > 0:
            raise NotImplementedError(f'Frequency broadening not implemented for {self.__class__.__name__}')

        density_matrices = FrequencyDensityMatricesFromDisk(
            ksd=self.ksd,
            frho_fmt=self.frho_fmt,
            perturbation=self.perturbation,
            frequencies=frequencies,
            real=real,
            imag=imag,
            log=log,
            calc_size=self.calc_size)

        return density_matrices
