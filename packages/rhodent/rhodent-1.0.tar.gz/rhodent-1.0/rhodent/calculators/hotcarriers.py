from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from typing import Any, Generator

from .base import BaseObservableCalculator
from ..density_matrices.base import WorkMetadata
from ..utils import ResultKeys, Result


class HotCarriersCalculator(BaseObservableCalculator):

    r""" Calculate hot-carrier distributions in the time domain.

    For weak perturbations, the response of the density matrix is
    to first order non-zero only in the occupied-unoccupied space,
    i.e. the block off-diagonals

    .. math::

        \delta\rho = \begin{bmatrix}
            0         &  [\delta\rho_{ai}^*] \\
            [\delta\rho_{ia}] &  0
        \end{bmatrix}.

    The unoccupied-occupied, or electron-hole, part of the density matrix is thus
    linear in perturbation and can by transformed using Fourier transforms.

    From the first-order response, the second order response, i.e. the hole-hole
    (:math:`\delta\rho_{ii'}`) and electron-electron (:math:`\delta\rho_{aa'}`) parts
    can be obtained.

    The hole-hole part is

    .. math::

        \delta\rho_{ii'} = - \frac{1}{2} \sum_n^{f_n > f_i, f_n > f_{i'}}
                           P_{ni} P_{ni'} + Q_{ni} Q_{ni'}

    and the electron-hole part

    .. math::

        \delta\rho_{aa'} = \frac{1}{2} \sum_n^{f_n < f_a, f_n < f_a'}
                           P_{ia} P_{ia'} + Q_{ia} Q_{ia'}

    where

    .. math::

        \begin{align}
            P_{ia} &= \frac{2 \mathrm{Im}\:\delta\rho_{ia}}{\sqrt{2 f_{ia}}} \\
            Q_{ia} &= \frac{2 \mathrm{Re}\:\delta\rho_{ia}}{\sqrt{2 f_{ia}}} ,
        \end{align}

    where :math:`f_{ia}` is the occupation number difference of pair :math:`ia`.

    Hot-carrier distributions are calculated by convolution of :math:`\delta\rho_{ii'}` (holes)
    and :math:`\delta\rho_{aa'}` (electrons) by Gaussian broadening functions on the energy
    grid.

    .. math::

        \begin{align}
            P^\text{holes}(\varepsilon) &=
            \sum_i \delta\rho_{ii'} G(\varepsilon - \varepsilon_i) \\
            P^\text{electrons}(\varepsilon) &=
            \sum_a \delta\rho_{aa'} G(\varepsilon - \varepsilon_a)
        \end{align}


    where :math:`\varepsilon_n` are Kohn-Sham energies and

    .. math::

       G(\varepsilon - \varepsilon_n)
        = \frac{1}{\sqrt{2 \pi \sigma^2}}
        \exp\left(-\frac{
            \left(\varepsilon_i - \varepsilon\right)^2
        }{
            2 \sigma^2
        }\right).

    Projected hot-carrier distributions are defined

    .. math::

        \begin{align}
            P^\text{holes}(\varepsilon) &=
            \sum_{ii'} \delta\rho_{ii'} w_{ii'} G(\varepsilon - \varepsilon_i) \\
            P^\text{electrons}(\varepsilon) &=
            \sum_{aa'} \delta\rho_{aa'} w_{aa'} G(\varepsilon - \varepsilon_a).
        \end{align}

    The Voronoi weights are

    .. math::

        W_{nn}
        = \left<\psi_n|\hat{w}|\psi_{n}\right>
        = \int w(\boldsymbol{r}) \psi_n^*(\boldsymbol{r}) \psi_{n}(\boldsymbol{r}) d\boldsymbol{r}

    where the operator :math:`\hat{w} = w(\boldsymbol{r})` is 1 in the Voronoi
    region of the atomic projections and 0 outside.

    Parameters
    ----------
    response
        Response object.
    voronoi
        Voronoi weights object.
    energies_occ
        Energy grid in units of eV for occupied levels (holes).
    energies_unocc
        Energy grid in units of eV for unoccupied levels (electrons)
    sigma
        Gaussian broadening width for energy grid in units of eV.
    times
        Compute hot carriers in the time domain, for these times (or as close to them as possible).
        In units of as.
    pulses
        Compute hot carriers in the time domain, in response to these pulses.
        If ``None`` no pulse convolution is performed.
    """

    def get_result_keys(self,
                        yield_total_hcdists: bool = False,
                        yield_proj_hcdists: bool = False,
                        yield_total_P: bool = False,
                        yield_proj_P: bool = False,
                        yield_total_P_ou: bool = False,
                        ):
        """ Get the keys that each result will contain, and dimensions thereof.

        Parameters
        ----------
        yield_total_hcdists
            The results should include the total hot-carrier distributions on the energy grid.
        yield_proj_hcdists
            The results should include the projections of the hot-carrier distributions on the energy grid.
        yield_total_P
            The results should include the total hot-carrier distributions in the electron-hole basis.
        yield_proj_P
            The results should include the projections of the hot-carrier distributions in the electron-hole basis.
        yield_total_P_ou
            The results should include the transition matrix broadened on the energy grid.
        """
        nI = self.nproj
        imin, imax, amin, amax = self.ksd.ialims()
        ni = int(imax - imin + 1)
        na = int(amax - amin + 1)
        no = len(self.energies_occ)
        nu = len(self.energies_unocc)

        resultkeys = ResultKeys('sumocc', 'sumunocc')

        if yield_total_P:
            resultkeys.add_key('P_i', ni)
            resultkeys.add_key('P_a', na)
        if yield_total_hcdists:
            resultkeys.add_key('hcdist_o', no)
            resultkeys.add_key('hcdist_u', nu)

        if yield_total_P_ou:
            resultkeys.add_key('P_ou', (no, nu))

        resultkeys.add_key('sumocc_proj_I', nI)
        resultkeys.add_key('sumunocc_proj_I', nI)
        if yield_proj_P:
            resultkeys.add_key('P_proj_Ii', (nI, ni))
            resultkeys.add_key('P_proj_Ia', (nI, na))
        if yield_proj_hcdists:
            resultkeys.add_key('hcdist_proj_Io', (nI, no))
            resultkeys.add_key('hcdist_proj_Iu', (nI, nu))

        return resultkeys

    def icalculate(self,
                   yield_total_hcdists: bool = False,
                   yield_proj_hcdists: bool = False,
                   yield_total_P: bool = False,
                   yield_proj_P: bool = False,
                   yield_total_P_ou: bool = False,
                   ) -> Generator[tuple[WorkMetadata, Result], None, None]:
        """ Iteratively calculate second order density matrices and hot-carrier distributions.

        Parameters
        ----------
        yield_total_hcdists
            The results should include the total hot-carrier distributions on the energy grid.
        yield_proj_hcdists
            The results should include the projections of the hot-carrier distributions on the energy grid.
        yield_total_P
            The results should include the total hot-carrier distributions in the electron-hole basis.
        yield_proj_P
            The results should include the projections of the hot-carrier distributions in the electron-hole basis.
        yield_total_P_ou
            The results should include the transition matrix broadened on the energy grid.

        Yields
        ------
        Tuple (work, result) on the root rank of the calculation communicator. \
        Does not yield on non-root ranks of the calculation communicator.

            work
                An object representing the metadata (time and pulse) for the work done.
            result
                Object containg the calculation results for this time and pulse.
        """
        include_energy_dists = (yield_proj_hcdists or yield_total_hcdists)
        if include_energy_dists:
            assert self.sigma is not None

        # List all keys that this method computes
        # This is necessary to safely send and receive data across ranks
        resultkeys = self.get_result_keys(yield_total_hcdists=yield_total_hcdists,
                                          yield_proj_hcdists=yield_proj_hcdists,
                                          yield_total_P=yield_total_P,
                                          yield_proj_P=yield_proj_P,
                                          yield_total_P_ou=yield_total_P_ou,
                                          )

        self._read_weights_eh()

        # Iterate over the pulses and times
        for work, dm in self.density_matrices:
            Q_ia = dm.Q_ia
            P_ia = dm.P_ia

            if dm.rank > 0:
                continue

            # Holes
            M_ii = 0.5 * (Q_ia @ Q_ia.T + P_ia @ P_ia.T)

            # Electrons
            M_aa = 0.5 * (Q_ia.T @ Q_ia + P_ia.T @ P_ia)

            result = Result()

            # (Optional) Compute broadened transition matrix
            if yield_total_P_ou:
                transition_ia = 0.5 * (Q_ia**2 + P_ia**2)
                result['P_ou'] = self.broaden_ia2ou(transition_ia)

            # Compute quantities in all space
            P_i = calculate_hcdist(None, M_ii)
            P_a = calculate_hcdist(None, M_aa)
            result['sumocc'] = np.sum(P_i)
            result['sumunocc'] = np.sum(P_a)
            if yield_total_hcdists:
                result['hcdist_o'] = self.broaden_occ(P_i)
                result['hcdist_u'] = self.broaden_unocc(P_a)
            if yield_total_P:
                result['P_i'] = P_i
                result['P_a'] = P_a

            result.create_all_empty(resultkeys)

            # Iterate over projections
            for iI, (weight_ii, weight_aa) in enumerate(self._iterate_weights_eh):
                P_proj_i = calculate_hcdist(weight_ii, M_ii)
                P_proj_a = calculate_hcdist(weight_aa, M_aa)
                result['sumocc_proj_I'][iI] = np.sum(P_proj_i)
                result['sumunocc_proj_I'][iI] = np.sum(P_proj_a)
                if yield_proj_hcdists:
                    result['hcdist_proj_Io'][iI] = self.broaden_occ(P_proj_i)
                    result['hcdist_proj_Iu'][iI] = self.broaden_unocc(P_proj_a)
                if yield_proj_P:
                    result['P_proj_Ii'][iI] = P_proj_i
                    result['P_proj_Ia'][iI] = P_proj_a

            self.log_parallel(f'Calculated and broadened HC distributions in {self.log.elapsed("calculate"):.2f}s '
                              f'for {work.desc}', flush=True)

            yield work, result

        if self.calc_comm.rank == 0 and self.density_matrices.localn > 0:
            self.log_parallel('Finished calculating hot-carrier matrices', flush=True)

    @property
    def _need_derivatives_real_imag(self) -> tuple[list[int], bool, bool]:
        return ([0], True, True)

    @property
    def _voronoi_shapes(self) -> dict[str, tuple[int, ...]]:
        nI = self.voronoi.nproj
        if nI == 0:
            return {}
        # Hole-hole part and electron-electron part
        Ni, Na = len(self.eig_i), len(self.eig_a)
        return {'ii': (nI, Ni, Ni), 'aa': (nI, Na, Na)}

    def calculate_totals_by_pulse_and_write(self,
                                            out_fname: str,
                                            write_extra: dict[str, Any] = dict()):
        """ Calculate the number of generated hot carriers, projected on groups of atoms, for
        a list of pulses.

        HC numbers are saved in a numpy archive if the file extension is ``.npz``
        or in a comma separated file if the file extension is ``.dat``.

        Parameters
        ----------
        out_fname
            File name of the resulting data file.
        """
        from ..writers.hcdist import HotCarriersWriter, write_hot_carrier_totals_by_pulse
        from ..writers.writer import PulseConvolutionAverageResultsCollector

        calc_kwargs = dict(yield_total_hcdists=False, yield_proj_hcdists=False)
        collector = PulseConvolutionAverageResultsCollector(self, calc_kwargs)
        writer = HotCarriersWriter(collector, only_one_pulse=False)

        out_fname = str(out_fname)
        if out_fname[-4:] == '.npz':
            writer.calculate_and_save_npz(out_fname, write_extra=write_extra)
        elif out_fname[-4:] == '.dat':
            write_hot_carrier_totals_by_pulse(out_fname, writer)
        else:
            raise ValueError(f'output-file must have ending .npz or .dat, is {out_fname}')

    def calculate_totals_by_time_and_write(self,
                                           out_fname: str,
                                           write_extra: dict[str, Any] = dict()):
        """ Calculate the number of generated hot carriers, projected on groups of atoms, for
        a list of times.

        HC numbers are saved in a numpy archive if the file extension is ``.npz``
        or in a comma separated file if the file extension is ``.dat``.

        Parameters
        ----------
        out_fname
            File name of the resulting data file.
        """
        from ..writers.hcdist import HotCarriersWriter, write_hot_carrier_totals_by_time
        from ..writers.writer import TimeResultsCollector

        calc_kwargs = dict(yield_total_hcdists=False, yield_proj_hcdists=False)
        collector = TimeResultsCollector(self, calc_kwargs)
        writer = HotCarriersWriter(collector, only_one_pulse=True)

        if out_fname[-4:] == '.npz':
            writer.calculate_and_save_npz(out_fname, write_extra=write_extra)
        elif out_fname[-4:] == '.dat':
            write_hot_carrier_totals_by_time(out_fname, writer)
        else:
            raise ValueError(f'output-file must have ending .npz or .dat, is {out_fname}')

    def calculate_distributions_and_write(self,
                                          out_fname: str,
                                          write_extra: dict[str, Any] = dict(),
                                          average_times: bool = True,
                                          only_one_pulse: bool = True):
        """ Calculate broadened hot-carrier energy distributions, optionally averaged over time.

        HC distributions are saved in a numpy archive if the file extension is ``.npz``
        or in a comma separated file if the file extension is ``.dat``.

        Parameters
        ----------
        out_fname
            File name of the resulting data file.
        write_extra
            Dictionary of extra key-value pairs to write to the data file.
        average_times
            If ``True``, an average over the given times will be taken. If false, then
            hot-carrier distributions are computed separately over the times, and
            each output is written separately for each time.
        only_one_pulse
            There is only one pulse, don't group by pulse.
        """
        from ..writers.hcdist import HotCarriersWriter, write_hot_carrier_distributions
        from ..writers.writer import TimeResultsCollector, TimeAverageResultsCollector

        if len(self.energies_occ) == 0 and len(self.energies_unocc) == 0:
            raise ValueError('Either occupied or unoccupied energies grid must be given')

        calc_kwargs = dict(yield_total_hcdists=True, yield_proj_hcdists=True)
        cls = TimeAverageResultsCollector if average_times else TimeResultsCollector
        writer = HotCarriersWriter(cls(self, calc_kwargs), only_one_pulse=only_one_pulse)

        if out_fname[-4:] == '.npz':
            writer.calculate_and_save_npz(out_fname, write_extra=write_extra)
        elif out_fname[-4:] == '.dat':
            write_hot_carrier_distributions(out_fname, writer)
        else:
            raise ValueError(f'output-file must have ending .npz or .dat, is {out_fname}')


def calculate_hcdist(weight_xx: NDArray[np.float64] | None,
                     M_xx: NDArray[np.float64],
                     ) -> NDArray[np.float64]:
    r""" Calculate row-wise summed hot carrier distribution.

    .. math::

        \rho_n = \sum_{n'} \rho_{nn'} w_{nn'}

    Parameters
    ----------
    weight_xx
        Voronoi weights :math:`w_{ii}` or :math:`w_{aa}`.
        Specify None to let the weights be the identity matrix
    M_xx
        Matrix :math:`M_{ii}` or :math:`M_{aa}`

    Returns
    -------
        Hot carrier distribution by eigenvalue :math:`\rho_n`
    """
    if weight_xx is None:
        P_x = np.diag(M_xx)
    else:
        P_x = np.sum(weight_xx*M_xx, axis=0)

    return P_x
