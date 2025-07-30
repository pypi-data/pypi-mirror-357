from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from ..density_matrices.frequency import FrequencyDensityMatrices
from ..density_matrices.base import WorkMetadata
from ..density_matrices.time import ConvolutionDensityMatrices
from ..utils import Result, get_gaussian_pulse_values
from .writer import ResultsCollector, Writer


class DipoleWriter(Writer):

    """ Calculate dipole moment contributions, optionally broadened onto
    an energy grid as a transition contribution map

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
        if only_one_pulse:
            if isinstance(self.density_matrices, ConvolutionDensityMatrices):
                assert len(self.density_matrices.pulses) == 1, 'Only one pulse allowed'
        else:
            if isinstance(self.density_matrices, ConvolutionDensityMatrices):
                self._ulm_tag = 'Time TCM'
            else:
                assert isinstance(self.density_matrices, FrequencyDensityMatrices)
                self._ulm_tag = 'TCM'

    @property
    def common_arrays(self) -> dict[str, NDArray[np.float64] | NDArray[np.int64] | int | float]:
        from ..calculators import DipoleCalculator
        assert isinstance(self.calc, DipoleCalculator)

        common = super().common_arrays

        if self.calc.sigma is not None:
            # There is an energy grid
            common['sigma'] = self.calc.sigma
            common['energy_o'] = np.array(self.calc.energies_occ)
            common['energy_u'] = np.array(self.calc.energies_unocc)

        if isinstance(self.density_matrices, ConvolutionDensityMatrices):
            common['time_t'] = self.density_matrices.times * 1e-3
        else:
            assert isinstance(self.density_matrices, FrequencyDensityMatrices)
            common['freq_w'] = self.density_matrices.frequencies
            common['frequency_broadening'] = self.density_matrices.frequency_broadening
            common['osc_prefactor_w'] = self.calc.oscillator_strength_prefactor

        if isinstance(self.density_matrices, ConvolutionDensityMatrices):
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

        return common

    def fill_ulm(self,
                 writer,
                 work: WorkMetadata,
                 result: Result):
        if self.collector.calc_kwargs.get('yield_total_ou', False):
            writer.fill(result['dm_ouv'])

    def write_empty_arrays_ulm(self, writer):
        if not self.collector.calc_kwargs.get('yield_total_ou', False):
            return
        shape_ou = (len(self.calc.energies_occ), len(self.calc.energies_unocc))
        if isinstance(self.density_matrices, ConvolutionDensityMatrices):
            Nt = len(self.density_matrices.times)
            # Real dipole
            writer.add_array('dm_touv', (Nt, ) + shape_ou + (3, ), dtype=float)
        else:
            assert isinstance(self.density_matrices, FrequencyDensityMatrices)
            Nw = len(self.density_matrices.frequencies)
            # Complex polarizability
            writer.add_array('dm_wouv', (Nw, ) + shape_ou + (3, ), dtype=complex)
