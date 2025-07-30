from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from gpaw.mpi import world

from ..voronoi import AtomProjectionsType


def write_density_of_states(out_fname: str,
                            energies: list[float] | NDArray[np.float64],
                            dos: list[float] | NDArray[np.float64],
                            sigma: float,
                            zerofermi: bool = False):
    """ Write the broadened :term:`DOS` to a text file.

    Parameters
    ----------
    out_fname
        File name of the resulting data file.
    energies
        Array of energies in units of eV.
    dos
        Array of DOS corresponding to the :attr:`energies`.
    sigma
        Gaussian broadening width in units of eV.
    zerofermi
        True if energies are to be relative to Fermi level, False if relative to vacuum.
    """
    if zerofermi:
        zerostr = 'relative to Fermi level'
    else:
        zerostr = 'relative to vacuum level'

    header = (f'DOS {zerostr}\n'
              f'Gaussian folding, Width {sigma:.4f} eV\n'
              'Energy (eV)        DOS (1/eV)')
    np.savetxt(out_fname, np.array([energies, dos]).T, fmt=['%12.6f', '%18.8e'], header=header)


def write_partial_density_of_states(out_fname: str,
                                    energies: list[float] | NDArray[np.float64],
                                    pdos: list[float] | NDArray[np.float64],
                                    atom_projections: AtomProjectionsType,
                                    sigma: float,
                                    zerofermi: bool = False):
    """ Write the broadened :term:`PDOS` to a text file.

    Parameters
    ----------
    out_fname
        File name of the resulting data file.
    energies
        Array of energies in units of eV.
    pdos
        Array of PDOS corresponding to the :attr:`energies`.
    atom_projections
        Atom projections.
    sigma
        Gaussian broadening width in units of eV.
    zerofermi
        True if energies are to be relative to Fermi level, False if relative to vacuum.
    """
    if world.rank != 0:
        return

    Ni = len(atom_projections)
    if zerofermi:
        zerostr = 'relative to Fermi level'
    else:
        zerostr = 'relative to vacuum level'

    savedata = np.zeros((len(energies), Ni + 1))
    savedata[:, 0] = energies
    savedata[:, 1:] = pdos

    projectionsstr = '\n'.join([f'  {i:4.0f}: {str(proj)}'
                                for i, proj in enumerate(atom_projections)])
    projcolumns = '   '.join([f'PDOS {i:4.0f} (1/eV)' for i in range(Ni)])

    header = (f'PDOS {zerostr}\n'
              'Atomic projections:\n'
              f'{projectionsstr}\n'
              f'Gaussian folding, Width {sigma:.4f} eV\n'
              f'Energy (eV)   {projcolumns}')
    fmt = ['%13.6f'] + Ni*['%18.8e']
    np.savetxt(out_fname, savedata, fmt, header=header)
