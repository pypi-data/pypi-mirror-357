from __future__ import annotations


import numpy as np
from numpy.typing import NDArray

from .. import __version__
from ..perturbation import create_perturbation, PerturbationLike


def write_spectrum(out_fname: str,
                   frequencies: list[float] | NDArray[np.float64],
                   spectrum: NDArray[np.float64],
                   frequency_broadening: float,
                   total_time: float,
                   timestep: float,
                   perturbation: PerturbationLike):
    """ Write dipole strength function (spectrum) to text file.

    Parameters
    ----------
    out_fname
       File name of the written file.
    frequencies
        Array of frequencies in units of eV.
    spectrum
        Spectrum corresponding to the :attr:`frequencies` in units of 1/eV.
    frequency_broadening
        Gaussian broadening width in units of eV. Default (0) is no broadening.
    total_time
        Total simulation time in units of as.
    timestep
        Timestep in units of as.
    perturbation
        The perturbation that was applied in the :term:`TDDFT` calculation.
    """
    frequencies = np.array(frequencies)
    osc_wv = np.array(spectrum)
    perturbation = create_perturbation(perturbation)

    if frequency_broadening == 0:
        broadening = 'No broadening'
    else:
        broadening = f'Gaussian broadening width {frequency_broadening:.2f} eV'
    perturbationstr = '\n'.join(['Perturbation during calculation was:'] +
                                ['  ' + line for line in str(perturbation).split('\n')])

    header = ('Photoabsorption spectrum from real-time propagation\n'
              f'Calculated using rhodent version: {__version__}\n'
              f'Total time = {total_time*1e-3:.4f} fs, Time steps = {timestep:.2f} as\n'
              f'{perturbationstr}\n'
              f'{broadening}\n'
              f'{"om (eV)":>10} {"S_x (1/eV)":>20} {"S_y (1/eV)":>20} {"S_z (1/eV)":>20}'
              )
    data_wi = np.zeros((len(frequencies), 1 + 3))
    data_wi[:, 0] = frequencies
    data_wi[:, 1:] = osc_wv
    fmt = '%12.6f' + (' %20.10le' * 3)
    np.savetxt(str(out_fname), data_wi, header=header, fmt=fmt)
