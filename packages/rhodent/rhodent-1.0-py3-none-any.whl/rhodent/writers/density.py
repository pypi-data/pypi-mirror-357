from __future__ import annotations

from time import strftime
import numpy as np
from numpy.typing import NDArray
from ase.io.cube import write_cube

from ..density_matrices.frequency import FrequencyDensityMatrices
from ..density_matrices.base import WorkMetadata
from ..density_matrices.time import ConvolutionDensityMatrices
from ..utils import Result, get_gaussian_pulse_values
from ..voronoi import VoronoiWeights, EmptyVoronoiWeights
from .writer import Writer, ResultsCollector


class DensityWriter(Writer):

    """ Calculate density contributions

    Parameters
    ----------
    collector
        ResultsCollector object
    """

    def __init__(self,
                 collector: ResultsCollector):
        super().__init__(collector)
        if isinstance(self.density_matrices, ConvolutionDensityMatrices):
            self._ulm_tag = 'Time Density'
            assert len(self.density_matrices.pulses) == 1, 'Only one pulse allowed'
        else:
            assert isinstance(self.density_matrices, FrequencyDensityMatrices)
            self._ulm_tag = 'Frequency Density'

    @property
    def voronoi(self) -> VoronoiWeights:
        return EmptyVoronoiWeights()

    @property
    def common_arrays(self) -> dict[str, NDArray[np.float64] | NDArray[np.int64] | int | float]:
        from ..calculators import DensityCalculator

        common = super().common_arrays
        common.pop('eig_i')
        common.pop('eig_a')
        common.pop('eig_n')
        common.pop('imin')
        common.pop('imax')
        common.pop('amin')
        common.pop('amax')

        assert isinstance(self.calc, DensityCalculator)
        common['N_c'] = self.calc.N_c
        common['cell_cv'] = self.calc.cell_cv

        atoms = self.density_matrices.ksd.atoms
        common['atom_numbers_i'] = atoms.get_atomic_numbers()
        common['atom_positions_iv'] = atoms.get_positions()

        if isinstance(self.density_matrices, ConvolutionDensityMatrices):
            common['time_t'] = self.density_matrices.times * 1e-3
        else:
            assert isinstance(self.density_matrices, FrequencyDensityMatrices)
            common['freq_w'] = self.density_matrices.frequencies

        if isinstance(self.density_matrices, ConvolutionDensityMatrices):
            # If pulse is Gaussian pulse, then get dictionary with 'pulsefreq' and 'pulsefwhm'
            common.update(**get_gaussian_pulse_values(self.density_matrices.pulses[0]))

        return common

    def fill_ulm(self,
                 writer,
                 work: WorkMetadata,
                 result: Result):
        writer.fill(result['rho_g'])

    def write_empty_arrays_ulm(self, writer):
        if isinstance(self.density_matrices, ConvolutionDensityMatrices):
            Nt = len(self.density_matrices.times)
            writer.add_array('rho_tg', (Nt, ) + self.calc.gdshape, dtype=float)
        else:
            assert isinstance(self.density_matrices, FrequencyDensityMatrices)
            Nw = len(self.density_matrices.frequencies)
            writer.add_array('rho_wg', (Nw, ) + self.calc.gdshape, dtype=float)


def write_density(out_fname: str,
                  atoms,
                  data,
                  comment: str | None = None):
    """ Calculate density contribution and save in Gaussian cube file format.

    Parameters
    ----------
    out_fname
        File name of the resulting cube file.
    comment
        Comment line in the cube file.
    """

    if comment is None:
        comment = f'Cube file from rhodent, written on {strftime("%c")}'
    else:
        comment = comment.strip()

    assert data is not None
    with open(out_fname, 'w') as fp:
        write_cube(fp, atoms, data=data, comment=comment)
