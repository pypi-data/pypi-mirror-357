from __future__ import annotations

from collections.abc import Sequence
import numpy as np
from typing import Any, Collection, Generator
from ase.units import Hartree, Bohr
from gpaw.tddft.units import as_to_au, au_to_eV, au_to_eA, eV_to_au

from .base import BaseObservableCalculator
from ..density_matrices.base import WorkMetadata
from ..density_matrices.time import ConvolutionDensityMatrixMetadata
from ..density_matrices.distributed.pulse import PulsePerturbation
from ..perturbation import PerturbationLike
from ..response import BaseResponse
from ..voronoi import VoronoiWeights
from ..typing import Array1D
from ..utils import ResultKeys, Result, broaden_n2e


class EnergyCalculator(BaseObservableCalculator):

    r""" Calculate energy contributions in the time domain.

    The total energy can be written

    .. math::

        E_\text{tot}(t) = E^{(0)}_\text{tot} + \sum_{ia}^\text{eh} E_{ia}(t) + E_\text{pulse}(t).

    The contributions to the total energy are

    .. math::

        E_{ia} = \frac{1}{2} \left[
        p_{ia}\dot{q}_{ia} - q_{ia} \dot{p}_{ia} - v_{ia} q_{ia} \right],

    the contributions to the Hartree-xc energy are

    .. math::

        E_{ia}^\text{Hxc} = -\frac{1}{2} \left[
        \omega_{ia} q_{ia}^2 - q_{ia} \dot{p}_{ia} - v_{ia} q_{ia} \right],

    and the rate of energy change is

    .. math::

        \dot{E}_{ia} = \frac{1}{2} \left[
        p_{ia}\ddot{q}_{ia} - q_{ia} \ddot{p}_{ia}
        - v_{ia} \dot{q}_{ia} - \dot{v}_{ia} q_{ia} \right].

    The matrix element :math:`v_{ia}` can be computed from the dipole matrix element

    .. math::

        \boldsymbol{\mu}_{ia} = \int \psi^{(0)}_i(\boldsymbol{r}) \boldsymbol{r}
        \psi^{(0)}_a(\boldsymbol{r}) \mathrm{d}\boldsymbol{r}

    projected on the direction of the perturbation :math:`\hat{\boldsymbol{e}}`,
    the occupation number difference :math:`f_{ia}` and
    the pulse amplitude :math:`v_\text{pulse}(t)`

    .. math::

        v_{ia} = \sqrt{2 f_{ia}}
        \boldsymbol{\mu}_{ia} \cdot\hat{\boldsymbol{e}}
        v_\text{pulse}.


    Parameters
    ----------
    response
        Response object.
    voronoi
        Voronoi weights object.
    filter_pair
        Filter electron-hole pairs (occupied-unoccupied transitions) in summation of energies.
        Provide a tuples (low, high) to compute the sum of energies
        :math:`E_{ia}` and :math:`E_{ia}^\text{Hxc}` for pairs with transition energy
        :math:`\varepsilon_a-\varepsilon_{i}` in the interval low-high (in units of eV).
    energies_occ
        Energy grid in units of eV for occupied levels (holes).
    energies_unocc
        Energy grid in units of eV for unoccupied levels (electrons).
    sigma
        Gaussian broadening width for energy grid in units of eV.
    times
        Compute energies in the time domain, for these times (or as close to them as possible).
        In units of as.
    pulses
        Compute energies in the time domain, in response to these pulses.
        If none, then no pulse convolution is performed.
    """
    def __init__(self,
                 response: BaseResponse,
                 voronoi: VoronoiWeights | None = None,
                 *,
                 filter_pair: tuple[float, float] = (0, np.inf),
                 energies_occ: list[float] | Array1D[np.float64] | None = None,
                 energies_unocc: list[float] | Array1D[np.float64] | None = None,
                 sigma: float | None = None,
                 times: list[float] | Array1D[np.float64] | None = None,
                 pulses: Collection[PerturbationLike] | None = None,
                 ):
        super().__init__(response=response,
                         voronoi=voronoi,
                         energies_occ=energies_occ,
                         energies_unocc=energies_unocc,
                         sigma=sigma,
                         times=times,
                         pulses=pulses)
        if len(filter_pair) != 2:
            raise ValueError('filter_pair must be tuple of two floats')
        self._filter_pair_low = float(filter_pair[0]) * eV_to_au
        self._filter_pair_high = float(filter_pair[1]) * eV_to_au

    def get_result_keys(self,
                        yield_total_E_ia: bool = False,
                        yield_proj_E_ia: bool = False,
                        yield_total_E_ou: bool = False,
                        yield_total_dists: bool = False,
                        direction: int | Sequence[int] = 2,
                        ) -> ResultKeys:
        r""" Get the keys that each result will contain, and dimensions thereof.

        Parameters
        ----------
        yield_total_E_ia
            The results should include the contributions in the electron-hole basis to
            the total energy :math:`E_{ia}` and Hartree-xc energy :math:`E_{ia}^\text{Hxc}`
        yield_proj_E_ia
            The results should include the contributions in the electron-hole basis to
            the total energy projected on the occupied and unoccupied Voronoi weights
            :math:`E_{ia} w_i` and :math:`E_{ia} w_a`.
        yield_total_E_ou
            The results should include the contributions the total energy broadened on the
            occupied and unoccupied energy grids
            :math:`\sum_{ia} E_{ia}\delta(\varepsilon_\text{occ}-\varepsilon_{i})
            \delta(\varepsilon_\text{unocc}-\varepsilon_{a})` and
        yield_total_dists
            The results should include the contributions the total energy and Hartree-xc energy
            broadened by electronic transition energy onto the unoccupied energies grid
            :math:`\sum_{ia} E_{ia} \delta(\varepsilon-\omega_{ia})` and
            :math:`\sum_{ia} E_{ia}^\text{Hxc} \delta(\varepsilon-\omega_{ia})`
        direction
            Direction :math:`\hat{\boldsymbol{e}}` of the polarization of the
            pulse. Integer 0, 1 or 2 to specify x, y or z, or the direction vector specified as
            a list of three values. Default: polarization along z.
        """
        nI = self.nproj
        imin, imax, amin, amax = self.ksd.ialims()
        ni = int(imax - imin + 1)
        na = int(amax - amin + 1)
        no = len(self.energies_occ)
        nu = len(self.energies_unocc)

        assert direction in [0, 1, 2] or (isinstance(direction, Sequence) and len(direction) == 3)

        resultkeys = ResultKeys('dm', 'total', 'total_Hxc', 'field',
                                'total_resonant', 'total_resonant_Hxc', 'Epulse')

        if yield_total_E_ia:
            resultkeys.add_key('E_ia', (ni, na))
            resultkeys.add_key('Ec_ia', (ni, na))
        if yield_total_dists:
            resultkeys.add_key('E_transition_u', nu)
            resultkeys.add_key('Ec_transition_u', nu)
        if yield_total_E_ou:
            resultkeys.add_key('E_ou', (no, nu))
            resultkeys.add_key('Ec_ou', (no, nu))

        resultkeys.add_key('total_proj_II', (nI, nI))
        resultkeys.add_key('total_Hxc_proj_II', (nI, nI))
        if yield_proj_E_ia:
            resultkeys.add_key('E_occ_proj_Iia', (nI, ni, na))
            resultkeys.add_key('E_unocc_proj_Iia', (nI, ni, na))

        return resultkeys

    def icalculate(self,
                   yield_total_E_ia: bool = False,
                   yield_proj_E_ia: bool = False,
                   yield_total_E_ou: bool = False,
                   yield_total_dists: bool = False,
                   direction: int | Sequence[int] = 2,
                   ) -> Generator[tuple[WorkMetadata, Result], None, None]:
        """ Iteratively calculate energies.

        Parameters
        ----------
        yield_total_E_ia
            The results should include the contributions in the electron-hole basis to
            the total energy :math:`E_{ia}` and Hartree-xc energy :math:`E_{ia}^\\text{Hxc}`
        yield_proj_E_ia
            The results should include the contributions in the electron-hole basis to
            the total energy projected on the occupied and unoccupied Voronoi weights
            :math:`E_{ia} w_i` and :math:`E_{ia} w_a`.
        yield_total_E_ou
            The results should include the contributions the total energy broadened on the
            occupied and unoccupied energy grids
            :math:`\\sum_{ia} E_{ia}\\delta(\\varepsilon_\\text{occ}-\\varepsilon_{i})
            \\delta(\\varepsilon_\\text{unocc}-\\varepsilon_{a})` and
        yield_total_dists
            The results should include the contributions the total energy and Hartree-xc energy
            broadened by electronic transition energy onto the unoccupied energies grid
            :math:`\\sum_{ia} E_{ia} \\delta(\\varepsilon-\\omega_{ia})` and
            :math:`\\sum_{ia} E_{ia}^\\text{Hxc} \\delta(\\varepsilon-\\omega_{ia})`
        direction
            Direction :math:`\\hat{\\boldsymbol{e}}` of the polarization of the
            pulse. Integer 0, 1 or 2 to specify x, y or z, or the direction vector specified as
            a list of three values. Default: polarization along z.

        Yields
        ------
        Tuple (work, result) on the root rank of the calculation communicator. \
        Does not yield on non-root ranks of the calculation communicator.

            work
                An object representing the metadata (time or pulse) for the work done.
            result
                Object containg the calculation results for this time and pulse.
        """
        include_energy_dists = (yield_total_dists or yield_total_E_ou)
        if include_energy_dists:
            assert self.sigma is not None

        assert direction in [0, 1, 2] or (isinstance(direction, Sequence) and len(direction) == 3)
        direction_v = np.zeros(3)
        if direction in [0, 1, 2]:
            direction_v[direction] = 1
        else:
            direction_v[:] = direction
            direction_v /= np.linalg.norm(direction_v)

        dm_p = direction_v @ self.ksd.dm_vp
        v0_p = dm_p * np.sqrt(2 * self.ksd.f_p)
        dm_ia = self.ksd.M_ia_from_M_p(dm_p)
        v0_ia = self.ksd.M_ia_from_M_p(v0_p)
        w_ia = self.ksd.M_ia_from_M_p(self.ksd.w_p)

        # List all keys that this method computes
        # This is necessary to safely send and receive data across ranks
        resultkeys = self.get_result_keys(yield_total_dists=yield_total_dists,
                                          yield_total_E_ia=yield_total_E_ia,
                                          yield_proj_E_ia=yield_proj_E_ia,
                                          yield_total_E_ou=yield_total_E_ou,
                                          )

        self._read_weights_diagonal()

        # Iterate over the pulses and times
        for work, dm in self.density_matrices:
            if dm.rank > 0:
                continue
            self.log.start('calculate')

            assert isinstance(work, ConvolutionDensityMatrixMetadata)
            assert isinstance(work.pulse, PulsePerturbation)
            pulsestr = work.pulse.pulse.strength(work.time * as_to_au)

            dipmom = - 2 * np.sum(dm_ia * dm.rho_ia.real)
            resonant_filter_ia = (w_ia > self._filter_pair_low) & (w_ia < self._filter_pair_high)

            Epulse = dipmom * pulsestr * au_to_eV

            # Calculate v_ia
            v_ia = v0_ia * pulsestr

            E_ia = -v_ia * dm.Q_ia
            E_ia -= dm.Q_ia * dm.dP_ia

            Ec_ia = E_ia.copy()

            E_ia += dm.P_ia * dm.dQ_ia
            E_ia *= 0.5 * au_to_eV

            Ec_ia -= w_ia * dm.Q_ia ** 2
            Ec_ia *= 0.5 * au_to_eV

            result = Result()
            if yield_total_E_ia:
                result['E_ia'] = E_ia
                result['Ec_ia'] = Ec_ia

            result['dm'] = dipmom * au_to_eA
            result['Epulse'] = Epulse
            result['field'] = pulsestr * Hartree / Bohr  # V/Å
            result['total'] = np.sum(E_ia)
            result['total_Hxc'] = np.sum(Ec_ia)
            result['total_resonant'] = E_ia.ravel() @ resonant_filter_ia.ravel()
            result['total_resonant_Hxc'] = Ec_ia.ravel() @ resonant_filter_ia.ravel()

            # (Optional) Broaden transitions by transition energy
            if yield_total_dists:
                assert self.sigma is not None
                result['E_transition_u'] = broaden_n2e(E_ia.ravel(), w_ia.ravel() * au_to_eV,
                                                       self.energies_unocc, self.sigma)
                result['Ec_transition_u'] = broaden_n2e(Ec_ia.ravel(), w_ia.ravel() * au_to_eV,
                                                        self.energies_unocc, self.sigma)

            # (Optional) Compute energy contribution matrix
            if yield_total_E_ou:
                result['E_ou'] = self.broaden_ia2ou(E_ia)
                result['Ec_ou'] = self.broaden_ia2ou(Ec_ia)

            # Initialize the remaining empty arrays
            result.create_all_empty(resultkeys)

            # Iterate over projections
            for iI, weight_n in enumerate(self._iterate_weights_diagonal):
                assert weight_n is not None
                weight_i = weight_n[self.flti]
                weight_a = weight_n[self.flta]

                for iI2, weight2_n in enumerate(self._iterate_weights_diagonal):
                    assert weight2_n is not None
                    weight2_a = weight2_n[self.flta]

                    result['total_proj_II'][iI, iI2] = np.einsum(
                        'ia,i,a->', E_ia, weight_i, weight2_a, optimize=True)
                    result['total_Hxc_proj_II'][iI, iI2] = np.einsum(
                        'ia,i,a->', Ec_ia, weight_i, weight2_a, optimize=True)

                if yield_proj_E_ia:
                    E_occ_proj_ia = E_ia * weight_i[:, None]
                    E_unocc_proj_ia = E_ia * weight_a[None, :]

                    result['E_occ_proj_Iia'][iI] = E_occ_proj_ia
                    result['E_unocc_proj_Iia'][iI] = E_unocc_proj_ia

            self.log_parallel(f'Calculated and broadened energies in {self.log.elapsed("calculate"):.2f}s '
                              f'for {work.desc}', flush=True)

            yield work, result

        if self.calc_comm.rank == 0:
            self.log_parallel('Finished calculating energies', flush=True)

    @property
    def _need_derivatives_real_imag(self) -> tuple[list[int], bool, bool]:
        return ([0, 1], True, True)

    @property
    def _voronoi_shapes(self) -> dict[str, tuple[int, ...]]:
        nI = self.voronoi.nproj
        if nI == 0:
            return {}
        Nn = self.voronoi.nn
        # Diagonal weights only
        return {'diagonal': (nI, Nn)}

    def calculate_and_write(self,
                            out_fname: str,
                            write_extra: dict[str, Any] = dict(),
                            include_tcm: bool = False,
                            save_dist: bool = False,
                            only_one_pulse: bool = True):
        """ Calculate energy contributions.

        Energies are saved in a numpy archive if the file extension is ``.npz``
        or in an ULM file if the file extension is ``.ulm``.

        Parameters
        ----------
        out_fname
            File name of the resulting data file.
        write_extra
            Dictionary of extra key-value pairs to write to the data file.
        include_tcm
            Whether the transition contribution map (TCM) to the energies should be computed and saved.
        save_dist
            Whether the transition energy distributions should be computed and saved.
        only_one_pulse
            If False, group arrays by pulse.
        """
        from ..writers.energy import EnergyWriter
        from ..writers.writer import TimeResultsCollector, PulseConvolutionResultsCollector

        out_fname = str(out_fname)
        if out_fname[-4:] == '.npz':
            calc_kwargs = dict(yield_total_E_ou=include_tcm, yield_total_dists=save_dist)
            cls = TimeResultsCollector if only_one_pulse else PulseConvolutionResultsCollector
            writer = EnergyWriter(cls(self, calc_kwargs), only_one_pulse=only_one_pulse)
            writer.calculate_and_save_npz(out_fname, write_extra=write_extra)
        elif out_fname[-4:] == '.ulm':
            assert only_one_pulse
            calc_kwargs = dict(yield_total_E_ou=include_tcm, yield_total_dists=save_dist)
            writer = EnergyWriter(TimeResultsCollector(self, calc_kwargs, exclude=['E_ou']), only_one_pulse=True)
            writer.calculate_and_save_ulm(out_fname, write_extra=write_extra)
        else:
            raise ValueError(f'output-file must have ending .npz or .ulm, is {out_fname}')
