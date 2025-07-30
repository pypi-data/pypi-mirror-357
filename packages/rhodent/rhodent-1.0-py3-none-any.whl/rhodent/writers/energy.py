from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from gpaw.tddft.units import au_to_eV

from ..density_matrices.base import WorkMetadata
from ..density_matrices.time import ConvolutionDensityMatrices
from .writer import Writer, ResultsCollector
from ..utils import Result, get_gaussian_pulse_values


class EnergyWriter(Writer):

    """ Calculate energy contributions

    Parameters
    ----------
    collector
        ResultsCollector object
    """

    def __init__(self,
                 collector: ResultsCollector,
                 only_one_pulse: bool):
        super().__init__(collector)
        self.only_one_pulse = only_one_pulse
        self._ulm_tag = 'EnergyDecomposition'
        if only_one_pulse:
            if isinstance(self.density_matrices, ConvolutionDensityMatrices):
                assert len(self.density_matrices.pulses) == 1, 'Only one pulse allowed'
        else:
            assert isinstance(self.density_matrices, ConvolutionDensityMatrices)

    @property
    def common_arrays(self) -> dict[str, NDArray[np.float64] | NDArray[np.int64] | int | float]:
        common = super().common_arrays

        if self.calc.sigma is not None:
            # There is an energy grid
            common['sigma'] = self.calc.sigma
            common['energy_o'] = np.array(self.calc.energies_occ)
            common['energy_u'] = np.array(self.calc.energies_unocc)

        assert isinstance(self.density_matrices, ConvolutionDensityMatrices)
        common['time_t'] = self.density_matrices.times * 1e-3

        # If pulses are Gaussian pulses, then get dictionaries of 'pulsefreq' and 'pulsefwhm'
        pulsedicts = [get_gaussian_pulse_values(pulse) for pulse in self.density_matrices.pulses]

        try:
            pulsefreqs = [d['pulsefreq'] for d in pulsedicts]
            pulsefwhms = [d['pulsefwhm'] for d in pulsedicts]

            if self.only_one_pulse:
                common['pulsefreq'] = pulsefreqs[0]
                common['pulsefwhm'] = pulsefwhms[0]
            else:
                common['pulsefreq_p'] = np.array(pulsefreqs)
                common['pulsefwhm_p'] = np.array(pulsefwhms)
        except KeyError:
            # Not GaussianPulses
            pass

        common['resonant_low'] = self.calc._filter_pair_low * au_to_eV  # type: ignore
        common['resonant_high'] = self.calc._filter_pair_high * au_to_eV  # type: ignore
        return common

    def fill_ulm(self,
                 writer,
                 work: WorkMetadata,
                 result: Result):
        assert self.only_one_pulse
        if self.collector.calc_kwargs['yield_total_E_ou']:
            writer.fill(result['E_ou'])

    def write_empty_arrays_ulm(self, writer):
        assert self.only_one_pulse
        if not self.collector.calc_kwargs['yield_total_E_ou']:
            return
        shape_ou = (len(self.calc.energies_occ), len(self.calc.energies_unocc))
        Nt = len(self.density_matrices.times)
        writer.add_array('E_tou', (Nt, ) + shape_ou, dtype=float)
