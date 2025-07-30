from __future__ import annotations

from typing import Any, Generator
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from ase.io.ulm import Reader
from gpaw.mpi import world

from .typing import GPAWCalculator
from .utils import gauss_ij, Logger
from .voronoi import VoronoiWeights, atom_projections_to_numpy


class DOSCalculator:

    r""" Density of states (:term:`DOS`) and partial DOS (:term:`PDOS`) calculator.

    Calculates DOS

    .. math::

       \mathrm{DOS}(\varepsilon) = \Sigma_n G(\varepsilon - \varepsilon_n)

    and PDOS

    .. math::

       \mathrm{PDOS}(\varepsilon) = \Sigma_n w_{nn} G(\varepsilon - \varepsilon_n)

    where :math:`\varepsilon_n` are Kohn-Sham energies and :math:`G(\varepsilon - \varepsilon_n)`
    a Gaussian broadening function

    .. math::

       G(\varepsilon - \varepsilon_n)
        = \frac{1}{\sqrt{2 \pi \sigma^2}}
        \exp\left(-\frac{
            \left(\varepsilon_i - \varepsilon\right)^2
        }{
            2 \sigma^2
        }\right).

    The Voronoi weights are defined

    .. math::

        W_{nn}
        = \left<\psi_n|\hat{w}|\psi_{n}\right>
        = \int w(\boldsymbol{r}) \psi_n^*(\boldsymbol{r}) \psi_{n}(\boldsymbol{r}) d\boldsymbol{r}

    where the operator :math:`\hat{w} = w(\boldsymbol{r})` is 1 in the Voronoi
    region of the atomic projections and 0 outside.

    Parameters
    ----------
    eigenvalues
        List of eigenvalues :math:`\varepsilon_n` (relative to Fermi level).
    fermilevel
        Fermi level.
    voronoi
        Voronoi weights object defining the atomic projections for :term:`PDOS`.

        Leave out if only :term:`DOS` is desired.
    energies
        Array of energies (in units of eV) for which the broadened :term:`PDOS` is computed.
    sigma
        Gaussian broadening width :math:`\sigma` in units of eV.
    zerofermi
        Eigenvalues relative to Fermi level if ``True``, else relative to vacuum
    """

    def __init__(self,
                 eigenvalues: list[float] | NDArray[np.float64],
                 fermilevel: float,
                 voronoi: VoronoiWeights | None,
                 energies: list[float] | NDArray[np.float64],
                 sigma: float,
                 zerofermi: bool = False):
        self._voronoi = voronoi
        self._eig_n = np.array(eigenvalues)
        self._fermilevel = fermilevel
        self._energies = np.array(energies)
        self._sigma = sigma
        self._zerofermi = zerofermi
        if voronoi is None:
            self._log = Logger()
        else:
            self._log = voronoi.log

    @property
    def voronoi(self) -> VoronoiWeights | None:
        """ Voronoi weights object. """
        return self._voronoi

    @property
    def log(self) -> Logger:
        """ Logger. """
        return self._log

    @property
    def zero(self) -> float:
        if self._zerofermi:
            return self._fermilevel
        else:
            return 0

    @property
    def eig_n(self) -> NDArray[np.float64]:
        return self._eig_n - self.zero

    @property
    def energies(self) -> NDArray[np.float64]:
        """ Energy grid in units of eV. """
        return self._energies

    @property
    def sigma(self) -> float:
        """ Gaussian broadening width in units of eV. """
        return self._sigma

    def calculate_dos(self) -> NDArray[np.float64] | None:
        """ Calculate :term:`DOS`.

        Returns
        ------
        DOS on the root rank, None on other ranks.
        """
        if world.rank != 0:
            return None

        # Construct gaussians
        gauss_en = gauss_ij(self.energies, self.eig_n, self.sigma)
        dos_e = np.sum(gauss_en, axis=1)
        self.log('Computed DOS', who='Calculator', comm=world, flush=True)
        return dos_e

    def icalculate_pdos(self) -> Generator[dict[str, NDArray[np.float64] | None], None, None]:
        """ Calculate :term:`PDOS` for each of the atomic projections in the :attr:`voronoi` object..

        Yields
        ------
        Once per set of Voronoi weights a dictionary with keys
            * ``weight_n`` - Array of dimensions ``(Nn)`` of projections. ``None`` on non-root ranks.
            * ``pdos_e`` - Broadened PDOS. ``None`` on non-root ranks.
        """
        if self.voronoi is None:
            raise ValueError('Voronoi must be given to the calculator')

        if world.rank == 0:
            # Construct gaussians
            gauss_en = gauss_ij(self.energies, self.eig_n, self.sigma)
            self.log('Computed gaussians', who='Calculator', comm=world, flush=True)

        for i, weight_nn in enumerate(self.voronoi):
            if world.rank == 0:
                assert weight_nn is not None
                weight_n = weight_nn.diagonal()
                pdos_e = gauss_en @ weight_n
                self.log(f'Computed PDOS for projection {self.voronoi.atom_projections[i]}',
                         who='Calculator', comm=world, flush=True)
                yield dict(weight_n=weight_n, pdos_e=pdos_e)
            else:
                yield dict(weight_n=None, pdos_e=None)

    @classmethod
    def from_gpw(cls,
                 gpw_file: Path | str,
                 voronoi: VoronoiWeights | None,
                 energies: list[float] | NDArray[np.float64],
                 sigma: float,
                 zerofermi: bool = False):
        r"""
        Initialize from ``.gpw`` file.

        Parameters
        ----------
        gpw_file
            File name of GPAW ground state file.
        voronoi
            Voronoi weights object defining the atomic projections for :term:`PDOS`.

            Leave out if only :term:`DOS` is desired.
        energies
            Array of energies (in units of eV) for which the broadened :term:`PDOS` is computed.
        sigma
            Gaussian broadening width :math:`\sigma` in units of eV.
        zerofermi
            Eigenvalues relative to Fermi level if ``True``, else relative to vacuum.
        """

        reader = Reader(gpw_file)
        eig_skn = reader.wave_functions.eigenvalues
        # Assume only one spin channel and one k point
        assert eig_skn.shape[:2] == (1, 1), 'Many spins or kpoints'
        eig_n = eig_skn[0, 0]
        fermilevel = reader.wave_functions.fermi_levels[0]

        return cls(eig_n, fermilevel, voronoi, energies, sigma, zerofermi)

    @classmethod
    def from_calc(cls,
                  calc: GPAWCalculator,
                  voronoi: VoronoiWeights | None,
                  energies: list[float] | NDArray[np.float64],
                  sigma: float,
                  zerofermi: bool = False):
        r"""
        Initialize from GPAW calculator.

        Parameters
        ----------
        calc
            GPAW calculator.
        voronoi
            Voronoi weights object defining the atomic projections for :term:`PDOS`.

            Leave out if only :term:`DOS` is desired.
        energies
            Array of energies (in units of eV) for which the broadened :term:`PDOS` is computed.
        sigma
            Gaussian broadening width :math:`\sigma` in units of eV.
        zerofermi
            Eigenvalues relative to Fermi level if ``True``, else relative to vacuum.
        """
        eig_n = calc.get_eigenvalues()
        fermilevel = calc.get_fermi_level()

        return cls(eig_n, fermilevel, voronoi, energies, sigma, zerofermi)

    def calculate_dos_and_write(self,
                                out_fname: Path | str,
                                write_extra: dict[str, Any] = dict()):
        """ Calculate the :term:`DOS` and write to file.

        The DOS is saved in a numpy archive if the file extension is ``.npz``
        or in a comma separated file if the file extension is ``.dat``.

        Parameters
        ----------
        out_fname
            File name of the resulting data file.
        write_extra
            Dictionary of additional data written to numpy archive (ignored for ``.dat``) files.
        """
        from .writers.dos import write_density_of_states

        # Calculate
        if world.rank == 0:
            dos_e = self.calculate_dos()

        # Write to file on root
        if world.rank > 0:
            world.barrier()
            return
        assert dos_e is not None

        out_fname = str(out_fname)
        if out_fname[-4:] == '.npz':
            write: dict[str, Any] = dict(
                energy_e=self.energies,
                dos_e=dos_e,
                sigma=self.sigma,
                zerofermi=self._zerofermi,
            )
            write.update(sigma=self.sigma, zerofermi=self._zerofermi)
            write.update(write_extra)

            np.savez_compressed(out_fname, **write)
        elif out_fname[-4:] == '.dat':
            write_density_of_states(out_fname=out_fname,
                                    energies=self.energies,
                                    dos=dos_e,
                                    sigma=self.sigma,
                                    zerofermi=self._zerofermi)
        else:
            raise ValueError(f'output-file must have ending .npz or .dat, is {out_fname}')

        self.log(f'Written {out_fname}', flush=True, who='Calculator', rank=0)
        world.barrier()

    def calculate_pdos_and_write(self,
                                 out_fname: Path | str,
                                 write_extra: dict[str, Any] = dict(),
                                 write_extra_from_voronoi: bool = False):
        """ Calculate the :term:`PDOS` and write to file.

        The PDOS is saved in a numpy archive if the file extension is ``.npz``
        or in a comma separated file if the file extension is ``.dat``.

        Parameters
        ----------
        out_fname
            File name of the resulting data file.
        write_extra
            Dictionary of additional data written to numpy archive (ignored for ``.dat``) files.
        write_extra_from_voronoi
            If true, and voronoi is a ULM reader, extra key-value pairs are read from
            voronoi and written to the ``.npz`` file (ignored for ``.dat``) files.
        """
        from .writers.dos import write_partial_density_of_states

        if self.voronoi is None:
            raise ValueError('Voronoi must be given to the calculator')

        # Calculate
        if world.rank == 0:
            pdos_ei = np.zeros((len(self.energies), len(self.voronoi)))
        for i, ret in enumerate(self.icalculate_pdos()):
            if world.rank != 0:
                continue
            pdos_ei[:, i] = ret['pdos_e']

        # Write to file on root
        if world.rank > 0:
            world.barrier()
            return

        out_fname = str(out_fname)
        if out_fname[-4:] == '.npz':
            write: dict[str, Any] = dict(
                energy_e=self.energies,
                pdos_ei=pdos_ei,
                atom_projections=atom_projections_to_numpy(self.voronoi.atom_projections),
                sigma=self.sigma,
                zerofermi=self._zerofermi,
            )
            write.update(sigma=self.sigma, zerofermi=self._zerofermi)
            if write_extra_from_voronoi:
                write.update(self.voronoi.saved_fields)
            write.update(write_extra)

            np.savez_compressed(out_fname, **write)
        elif out_fname[-4:] == '.dat':
            write_partial_density_of_states(out_fname=out_fname,
                                            energies=self.energies,
                                            pdos=pdos_ei,
                                            atom_projections=self.voronoi.atom_projections,
                                            sigma=self.sigma,
                                            zerofermi=self._zerofermi)
        else:
            raise ValueError(f'output-file must have ending .npz or .dat, is {out_fname}')

        self.log(f'Written {out_fname}', flush=True, who='Calculator', rank=0)
        world.barrier()
