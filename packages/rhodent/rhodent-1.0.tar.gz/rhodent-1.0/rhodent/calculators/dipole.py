from __future__ import annotations

import numpy as np
from typing import Any, Generator
from numpy.typing import NDArray

from gpaw.tddft.units import au_to_eA, au_to_eV

from .base import BaseObservableCalculator
from ..density_matrices.base import WorkMetadata
from ..utils import ResultKeys, Result


class DipoleCalculator(BaseObservableCalculator):

    r""" Calculate the induced dipole moment in the time or frequency domain.

    The induced dipole moment (i.e. the dipole moment minus the permanent
    component) is to first order given by

    .. math::

        \delta\boldsymbol{\mu} = -2 \sum_{ia}^\text{eh}
        \boldsymbol{\mu}_{ia} \mathrm{Re}\:\delta\rho_{ia},

    where :math:`\boldsymbol{\mu}_{ia}` is the dipole matrix element of ground state Kohn-Sham
    pair :math:`ia`

    .. math::

        \boldsymbol{\mu}_{ia} = \int \psi^{(0)}_i(\boldsymbol{r}) \boldsymbol{r}
        \psi^{(0)}_a(\boldsymbol{r}) \mathrm{d}\boldsymbol{r},

    and :math:`\delta\rho_{ia}` the induced Kohn-Sham density matrix.

    In the frequency domain, this calculator calculates the polarizability, i.e. the Fourier
    transform of the dipole moment divided by the perturbation.

    .. math::

        \boldsymbol{\alpha}(\omega) = -2 \sum_{ia}^\text{eh}
        \boldsymbol{\mu}_{ia} \frac{\mathcal{F}\left[\mathrm{Re}\:\delta\rho_{ia}\right](\omega)}{v(\omega)}.

    The absorption spectrum in units of dipole strength function is the imaginary part
    of the polarizability times a prefactor

    .. math::

        \boldsymbol{S}(\omega) = \frac{2\omega}{\pi} \mathrm{Im}\:\boldsymbol{\alpha}(\omega).

    This class can also compute projections of the above on Voronoi weights :math:`w_{ia}`.

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
        Compute induced dipole in the time domain, for these times (or as close to them as possible).
        In units of as.

        May not be used together with :attr:`frequencies` or :attr:`frequency_broadening`.
    pulses
        Compute induced dipole in the time domain, in response to these pulses.
        If none, then no pulse convolution is performed.

        May not be used together with :attr:`frequencies` or :attr:`frequency_broadening`.
    frequencies
        Compute polarizability in the frequency domain, for these frequencies. In units of eV.

        May not be used together with :attr:`times` or :attr:`pulses`.
    frequency_broadening
        Compute polarizability in the frequency domain, with Gaussian broadening of this width.
        In units of eV.

        May not be used together with :attr:`times` or :attr:`pulses`.
    """

    def get_result_keys(self,
                        yield_total_ia: bool = False,
                        yield_proj_ia: bool = False,
                        yield_total_ou: bool = False,
                        yield_proj_ou: bool = False,
                        decompose_v: bool = True,
                        v: int | None = None,
                        ) -> ResultKeys:
        r""" Get the keys that each result will contain, and dimensions thereof.

        Parameters
        ----------
        yield_total_ia
            The results should include the total dipole contributions in the electron-hole basis
            :math:`-2 \boldsymbol{\mu}_{ia} \mathrm{Re}\:\delta\rho_{ia}`.
        yield_proj_ia
            The results should include projections of the dipole contributions in the electron-hole basis
            :math:`-2 \boldsymbol{\mu}_{ia} \mathrm{Re}\:\delta\rho_{ia} w_{ia}`.
        yield_total_ou
            The results should include the total dipole contributions on the energy grid.
        yield_proj_ou
            The results should include projections of the dipole contributions on the energy grid.
        decompose_v
            The results should include the dipole moment and/or its contributions decomposed
            by Cartesian direction.
        v
            If not None, then the results should include the v:th Cartesian component
            of the dipole moment and its contributions.
        """
        assert decompose_v or v is not None

        nI = self.nproj
        imin, imax, amin, amax = self.ksd.ialims()
        ni = imax - imin + 1
        na = amax - amin + 1
        no = len(self.energies_occ)
        nu = len(self.energies_unocc)

        # Time domain: save dipole moment, which is real
        # Frequency domain: save polarizability, which is complex
        dtype = float if self._is_time_density_matrices else complex

        resultkeys = ResultKeys()
        if v is not None:
            resultkeys.add_key('dm', dtype=dtype)
            if yield_total_ia:
                resultkeys.add_key('dm_ia', (ni, na), dtype=dtype)
            if yield_total_ou:
                resultkeys.add_key('dm_ou', (no, nu), dtype=dtype)

            resultkeys.add_key('dm_proj_II', (nI, nI), dtype=dtype)
            if yield_proj_ia:
                resultkeys.add_key('dm_occ_proj_Iia', (nI, ni, na), dtype=dtype)
                resultkeys.add_key('dm_unocc_proj_Iia', (nI, ni, na), dtype=dtype)
            if yield_proj_ou:
                resultkeys.add_key('dm_occ_proj_Iou', (nI, no, nu), dtype=dtype)
                resultkeys.add_key('dm_unocc_proj_Iou', (nI, no, nu), dtype=dtype)
        if decompose_v:
            resultkeys.add_key('dm_v', 3, dtype=dtype)
            if yield_total_ia:
                resultkeys.add_key('dm_iav', (ni, na, 3), dtype=dtype)
            if yield_total_ou:
                resultkeys.add_key('dm_ouv', (no, nu, 3), dtype=dtype)

            resultkeys.add_key('dm_proj_IIv', (nI, nI, 3), dtype=dtype)
            if yield_proj_ia:
                resultkeys.add_key('dm_occ_proj_Iiav', (nI, ni, na, 3), dtype=dtype)
                resultkeys.add_key('dm_unocc_proj_Iiav', (nI, ni, na, 3), dtype=dtype)
            if yield_proj_ou:
                resultkeys.add_key('dm_occ_proj_Iouv', (nI, no, nu, 3), dtype=dtype)
                resultkeys.add_key('dm_unocc_proj_Iouv', (nI, no, nu, 3), dtype=dtype)

        return resultkeys

    def icalculate(self,
                   yield_total_ia: bool = False,
                   yield_proj_ia: bool = False,
                   yield_total_ou: bool = False,
                   yield_proj_ou: bool = False,
                   decompose_v: bool = True,
                   v: int | None = None,
                   ) -> Generator[tuple[WorkMetadata, Result], None, None]:
        """ Iteratively calculate dipole contributions.

        Parameters
        ----------
        yield_total_ia
            The results should include the total dipole contributions in the electron-hole basis
            :math:`-2 \\boldsymbol{\\mu}_{ia} \\mathrm{Re}\\:\\delta\\rho_{ia}`.
        yield_proj_ia
            The results should include projections of the dipole contributions in the electron-hole basis
            :math:`-2 \\boldsymbol{\\mu}_{ia} \\mathrm{Re}\\:\\delta\\rho_{ia} w_{ia}`.
        yield_total_ou
            The results should include the total dipole contributions on the energy grid.
        yield_proj_ou
            The results should include projections of the dipole contributions on the energy grid.
        decompose_v
            The results should include the dipole moment and/or its contributions decomposed
            by Cartesian direction.
        v
            If not ``None``, then the results should include the v:th Cartesian component \
            of the dipole moment and its contributions.

        Yields
        ------
        Tuple (work, result) on the root rank of the calculation communicator. \
        Does not yield on non-root ranks of the calculation communicator.

            work
                An object representing the metadata (time, frequency or pulse) for the work done.
            result
                Object containg the calculation results for this time, frequency or pulse.
        """
        include_energy_dists = (yield_total_ou or yield_proj_ou)
        if include_energy_dists:
            assert self.sigma is not None
        need_entire_matrix = (yield_total_ou or yield_proj_ou
                              or yield_total_ia or yield_proj_ia
                              or self.nproj > 0)

        # Time domain: dipole moment in units of eÅ
        # Frequency domain: polarizability in units of (eÅ)**2/eV
        unit = au_to_eA if self._is_time_density_matrices else au_to_eA**2 / au_to_eV
        dm0_iav = -2 * np.moveaxis(np.array([self.ksd.M_ia_from_M_p(dm_p) for dm_p in self.ksd.dm_vp]), 0, -1) * unit

        # List all keys that this method computes
        # This is necessary to safely send and receive data across ranks
        resultkeys = self.get_result_keys(yield_total_ia=yield_total_ia,
                                          yield_proj_ia=yield_proj_ia,
                                          yield_total_ou=yield_total_ou,
                                          yield_proj_ou=yield_proj_ou,
                                          decompose_v=decompose_v,
                                          v=v,
                                          )

        self._read_weights_diagonal()

        # Iterate over the pulses and times
        for work, dm in self.density_matrices:
            if dm.rank > 0:
                continue

            self.log.start('calculate')

            if need_entire_matrix:
                if self._is_time_density_matrices:
                    # Real dipole
                    dm_iav = dm0_iav * dm.rho_ia[..., None].real
                else:
                    # Complex polarizability
                    dm_iav = dm0_iav * dm.rho_ia[..., None]
                dm_v = np.sum(dm_iav, axis=(0, 1))

                if yield_total_ou:
                    dm_ouv = self.broaden_ia2ou(dm_iav)
            else:
                if self._is_time_density_matrices:
                    # Real dipole
                    dm_v = np.einsum('iav,ia->v', dm0_iav, dm.rho_ia.real, optimize=True)
                else:
                    # Complex polarizability
                    dm_v = np.einsum('iav,ia->v', dm0_iav, dm.rho_ia, optimize=True)

            result = Result()
            if decompose_v:
                result['dm_v'] = dm_v
                if yield_total_ia:
                    result['dm_iav'] = dm_iav
                if yield_total_ou:
                    result['dm_ouv'] = dm_ouv
            if v is not None:
                result['dm'] = dm_v[v]
                if yield_total_ia:
                    result['dm_ia'] = dm_iav[..., v]
                if yield_total_ou:
                    result['dm_ou'] = dm_ouv[..., v]

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

                    dm_proj_v = np.einsum('iav,i,a->v', dm_iav, weight_i, weight2_a, optimize=True)
                    result['dm_proj_IIv'][iI, iI2] = dm_proj_v

                if yield_proj_ia or yield_proj_ou:
                    dm_occ_proj_iav = dm_iav * weight_i[:, None, None]
                    dm_unocc_proj_iav = dm_iav * weight_a[None, :, None]

                    if yield_proj_ou:
                        dm_occ_proj_ouv = self.broaden_ia2ou(dm_occ_proj_iav)
                        dm_unocc_proj_ouv = self.broaden_ia2ou(dm_unocc_proj_iav)

                    if decompose_v:
                        if yield_proj_ia:
                            result['dm_occ_proj_Iiav'][iI] = dm_occ_proj_iav
                            result['dm_unocc_proj_Iiav'][iI] = dm_unocc_proj_iav
                        if yield_proj_ou:
                            result['dm_occ_proj_Iouv'][iI] = dm_occ_proj_ouv
                            result['dm_unocc_proj_Iouv'][iI] = dm_unocc_proj_ouv
                    if v is not None:
                        if yield_proj_ia:
                            result['dm_occ_proj_Iia'][iI] = dm_occ_proj_iav[..., v]
                            result['dm_unocc_proj_Iia'][iI] = dm_unocc_proj_iav[..., v]
                        if yield_proj_ou:
                            dm_occ_proj_ouv = self.broaden_ia2ou(dm_occ_proj_iav)
                            dm_unocc_proj_ouv = self.broaden_ia2ou(dm_unocc_proj_iav)

                        if decompose_v:
                            if yield_proj_ia:
                                result['dm_occ_proj_Iiav'][iI] = dm_occ_proj_iav
                                result['dm_unocc_proj_Iiav'][iI] = dm_unocc_proj_iav
                            if yield_proj_ou:
                                result['dm_occ_proj_Iouv'][iI] = dm_occ_proj_ouv
                                result['dm_unocc_proj_Iouv'][iI] = dm_unocc_proj_ouv
                        if v is not None:
                            if yield_proj_ia:
                                result['dm_occ_proj_Iia'][iI] = dm_occ_proj_iav[..., v]
                                result['dm_unocc_proj_Iia'][iI] = dm_unocc_proj_iav[..., v]
                            if yield_proj_ou:
                                result['dm_occ_proj_Iou'][iI] = dm_occ_proj_ouv[..., v]
                                result['dm_unocc_proj_Iou'][iI] = dm_unocc_proj_ouv[..., v]

            self.log_parallel(f'Calculated and broadened dipoles contributions in {self.log.elapsed("calculate"):.2f}s '
                              f'for {work.desc}', flush=True)

            yield work, result

        if self.calc_comm.rank == 0:
            self.log_parallel('Finished calculating dipoles contributions', flush=True)

    @property
    def _need_derivatives_real_imag(self) -> tuple[list[int], bool, bool]:
        # Time domain: We only need the real part of the density matrix.
        # Frequency domain: We need the (complex) Fourier transform of
        #                   the real part of the density matrix.
        return ([0], True, False)

    @property
    def _voronoi_shapes(self) -> dict[str, tuple[int, ...]]:
        nI = self.voronoi.nproj
        if nI == 0:
            return {}
        Nn = self.voronoi.nn
        # Diagonal weights only
        return {'diagonal': (nI, Nn)}

    @property
    def oscillator_strength_prefactor(self) -> NDArray[np.float64]:
        """ Conversion factor from polarizability to dipole strength function.

        """
        from gpaw.tddft.units import eA_to_au, eV_to_au
        # Convert polarizability (eÅ**2/eV) to atomic units
        # Multiply by 2 omega / pi in atomic units
        # Convert to units of dipole strength function (1/eV)
        prefactor_w = 2 * (self.frequencies * eV_to_au) / np.pi * eA_to_au ** 2
        return prefactor_w

    def calculate_and_write(self,
                            out_fname: str,
                            write_extra: dict[str, Any] = dict(),
                            include_tcm: bool = False,
                            only_one_pulse: bool = True):
        """ Calculate induced dipole moments and transition contribution maps.

        Dipole moments and contributions are saved in a numpy archive if
        the file extension is ``.npz`` or in an ULM file if the file extension is ``.ulm``.

        Parameters
        ----------
        out_fname
            File name of the resulting data file.
        write_extra
            Dictionary of extra key-value pairs to write to the data file.
        include_tcm
            Whether the transition contribution map (TCM) to the dipole moments should be computed and saved.
        only_one_pulse
            If False, group arrays by pulse. Only valid in time domain.
        """
        from ..writers.tcm import DipoleWriter
        from ..writers.writer import FrequencyResultsCollector, TimeResultsCollector, PulseConvolutionResultsCollector

        cls = ((TimeResultsCollector if only_one_pulse else PulseConvolutionResultsCollector)
               if self._is_time_density_matrices else FrequencyResultsCollector)
        calc_kwargs = dict(yield_total_ou=include_tcm, yield_proj_ou=include_tcm)

        out_fname = str(out_fname)
        if out_fname[-4:] == '.npz':
            writer = DipoleWriter(cls(self, calc_kwargs), only_one_pulse=only_one_pulse)
            writer.calculate_and_save_npz(out_fname, write_extra=write_extra)
        elif out_fname[-4:] == '.ulm':
            writer = DipoleWriter(cls(self, calc_kwargs, exclude=['dm_ouv']), only_one_pulse=only_one_pulse)
            writer.calculate_and_save_ulm(out_fname, write_extra=write_extra)
        else:
            raise ValueError(f'output-file must have ending .npz or .ulm, is {out_fname}')
