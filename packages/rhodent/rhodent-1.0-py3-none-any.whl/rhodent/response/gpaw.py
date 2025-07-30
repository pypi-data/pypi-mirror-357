from __future__ import annotations

from typing import Collection

import numpy as np
from pathlib import Path

from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition

from .base import BaseResponse
from ..perturbation import create_perturbation, PerturbationLike, NoPerturbation
from ..density_matrices.frequency import (FrequencyDensityMatrices,
                                          FrequencyDensityMatricesFromWaveFunctions)
from ..density_matrices.time import (ConvolutionDensityMatrices,
                                     ConvolutionDensityMatricesFromWaveFunctions,
                                     TimeDensityMatricesFromWaveFunctions)
from ..utils import Logger
from ..typing import Array1D


class ResponseFromWaveFunctions(BaseResponse):

    """ Response from time-dependent wave functions file written by GPAW.

    Parameters
    ----------
    ksd
        KohnShamDecomposition object or file name.
    wfs_fname
        File name of the time-dependent wave functions file, written by ``WaveFunctionsWriter``.
    perturbation
        Perturbation that was present during time propagation.
    calc_size
        Size of the calculation communicator.
    """

    def __init__(self,
                 wfs_fname: Path | str,  # File name of wfs.ulm file
                 ksd: KohnShamDecomposition | str,
                 perturbation: PerturbationLike = None,
                 calc_size: int = 1,
                 stridet: int = 1):
        super().__init__(ksd=ksd,
                         perturbation=perturbation,
                         calc_size=calc_size)

        self.wfs_fname = str(wfs_fname)

        # Options for reading the wfs.ulm file
        self.stridet = stridet

    def __str__(self) -> str:
        lines = [f'{self.__class__.__name__}']
        lines += [f'  ksd: {self.ksd.filename if self.ksd.filename is not None else "From calc"}']
        lines += [f'  wfs_fname: {self.wfs_fname}']
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
        density_matrices: ConvolutionDensityMatrices

        # Perform convolution if pulses differ from perturbation or higher derivatives needed
        if (all(create_perturbation(pulse) == self.perturbation for pulse in pulses) and
                all(derivative == 0 for derivative in derivative_order_s)):
            # No convolution needed
            density_matrices = TimeDensityMatricesFromWaveFunctions(
                ksd=self.ksd,
                wfs_fname=self.wfs_fname,
                times=times,
                real=real,
                imag=imag,
                log=log,
                calc_size=self.calc_size,
                stridet=self.stridet)
        else:
            # Perform convolution
            if isinstance(self.perturbation, NoPerturbation):
                raise ValueError('Perturbation must be given to perform pulse convolution.')
            density_matrices = ConvolutionDensityMatricesFromWaveFunctions(
                ksd=self.ksd,
                wfs_fname=self.wfs_fname,
                perturbation=self.perturbation,
                pulses=pulses,
                times=times,
                derivative_order_s=derivative_order_s,
                real=real,
                imag=imag,
                log=log,
                calc_size=self.calc_size,
                stridet=self.stridet)

        return density_matrices

    def _get_frequency_density_matrices(self,
                                        frequencies: list[float] | Array1D[np.float64],
                                        frequency_broadening: float = 0,
                                        real: bool = True,
                                        imag: bool = True,
                                        log: Logger | None = None,
                                        ) -> FrequencyDensityMatrices:
        if isinstance(self.perturbation, NoPerturbation):
            raise ValueError('Perturbation must be given to normalize Fourier transform.')
        density_matrices = FrequencyDensityMatricesFromWaveFunctions(
            ksd=self.ksd,
            wfs_fname=self.wfs_fname,
            perturbation=self.perturbation,
            frequencies=frequencies,
            frequency_broadening=frequency_broadening,
            real=real,
            imag=imag,
            calc_size=self.calc_size,
            log=log,
            stridet=self.stridet)

        return density_matrices
