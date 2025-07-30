from __future__ import annotations

from pathlib import Path
import numpy as np
from numpy.typing import NDArray
from typing import Any, Generator, Sequence, Collection

from ase.units import Bohr
from gpaw import GPAW
from gpaw.grid_descriptor import GridDescriptor
from gpaw.lcaotddft.densitymatrix import get_density

from .base import BaseObservableCalculator
from ..typing import GPAWCalculator
from ..density_matrices.base import WorkMetadata
from ..density_matrices.frequency import FrequencyDensityMatrixMetadata
from ..density_matrices.time import ConvolutionDensityMatrixMetadata
from ..perturbation import PerturbationLike
from ..response import BaseResponse
from ..typing import ArrayIsOnRootRank, Array1D, DistributedArray
from ..utils import ResultKeys, Result, get_gaussian_pulse_values, ParallelMatrix


class DensityCalculator(BaseObservableCalculator):

    r""" Calculate densities in the time or frequency domain.

    The induced density (i.e. the density minus the ground state density) is to first
    order given by

    .. math::

        \delta n(\boldsymbol{r}) = -2 \sum_{ia}^\text{eh}
        n_{ia}(\boldsymbol{r}) \mathrm{Re}\:\delta\rho_{ia}

    plus PAW corrections, where :math:`n_{ia}(\boldsymbol{r})` is the density of
    ground state Kohn-Sham pair :math:`ia`

    .. math::

        n_{ia}(\boldsymbol{r}) = \psi^{(0)}_i(\boldsymbol{r}) \psi^{(0)}_a(\boldsymbol{r}).

    In the time domain, electrons and holes densities can be computed.

    .. math::

        \begin{align}
            n^\text{holes}(\boldsymbol{r}) &= \sum_{ii'}
            n_{ii'}(\boldsymbol{r}) \delta\rho_{ii'} \\
            n^\text{electrons}(\boldsymbol{r}) &= \sum_{aa'}
            n_{aa'}(\boldsymbol{r}) \delta\rho_{aa'}.
        \end{align}

    Refer to the documentation of
    :class:`HotCarriersCalculator <rhodent.calculators.HotCarriersCalculator>` for definitions
    of :math:`\delta\rho_{ii'}` and :math:`\delta\rho_{aa'}`.

    Parameters
    ----------
    gpw_file
        File name of GPAW ground state file.
    response
        Response object.
    filter_occ
        Filters for occupied states (holes). Provide a list of tuples (low, high)
        to compute the density of holes with energies within the interval low-high.
    filter_unocc
        Filters for unoccupied states (electrons). Provide a list of tuples (low, high)
        to compute the density of excited electrons with energies within the interval low-high.
    times
        Compute densities in the time domain, for these times (or as close to them as possible).
        In units of as.

        May not be used together with :attr:`frequencies` or :attr:`frequency_broadening`.
    pulses
        Compute densities in the time domain, in response to these pulses.
        If none, then no pulse convolution is performed.

        May not be used together with :attr:`frequencies` or :attr:`frequency_broadening`.
    frequencies
        Compute densities in the frequency domain, for these frequencies. In units of eV.

        May not be used together with :attr:`times` or :attr:`pulses`.
    frequency_broadening
        Compute densities in the frequency domain, with Gaussian broadening of this width.
        In units of eV.

        May not be used together with :attr:`times` or :attr:`pulses`.
    """

    def __init__(self,
                 gpw_file: str,
                 response: BaseResponse,
                 filter_occ: Sequence[tuple[float, float]] = [],
                 filter_unocc: Sequence[tuple[float, float]] = [],
                 *,
                 times: list[float] | Array1D[np.float64] | None = None,
                 pulses: Collection[PerturbationLike] | None = None,
                 frequencies: list[float] | Array1D[np.float64] | None = None,
                 frequency_broadening: float = 0,
                 ):
        super().__init__(response=response,
                         times=times,
                         pulses=pulses,
                         frequencies=frequencies,
                         frequency_broadening=frequency_broadening)
        self._occ_filters = [self._build_single_filter('o', low, high) for low, high in filter_occ]
        self._unocc_filters = [self._build_single_filter('u', low, high) for low, high in filter_unocc]

        self.log.start('load_gpaw')
        self._calc = GPAW(gpw_file, txt=None, communicator=self.calc_comm,
                          parallel={'domain': self.calc_comm.size})
        msg = f'Loaded/initialized GPAW in {self.log.elapsed("load_gpaw"):.1f}'
        self.log.start('init_gpaw')

        self.calc.initialize_positions()  # Initialize in order to calculate density
        msg += f'/{self.log.elapsed("init_gpaw"):.1f} s'
        if self.calc_comm.rank == 0:
            self.log_parallel(msg)
        self.ksd.density = self.calc.density

    @property
    def gdshape(self) -> tuple[int, int, int]:
        """ Shape of the real space grid.
        """
        shape = tuple(int(N) - 1 for N in self.N_c)
        return shape  # type: ignore

    @property
    def gd(self) -> GridDescriptor:
        """ Real space grid. """
        return self.ksd.density.finegd

    @property
    def N_c(self) -> NDArray[np.int_]:
        """ Number of points in each Cartesian direction of the grid.
        """
        return self.gd.N_c

    @property
    def cell_cv(self) -> NDArray[np.float64]:
        """ Cell vectors. """
        return self.gd.cell_cv * Bohr

    @property
    def occ_filters(self) -> list[slice]:
        """ List of energy filters for occupied states. """
        return self._occ_filters

    @property
    def unocc_filters(self) -> list[slice]:
        """ List of energy filters for unoccupied states. """
        return self._unocc_filters

    @property
    def calc(self) -> GPAWCalculator:
        """ GPAW calculator instance. """
        return self._calc  # type: ignore

    def get_result_keys(self,
                        yield_total: bool = True,
                        yield_electrons: bool = False,
                        yield_holes: bool = False) -> ResultKeys:
        noccf = len(self.occ_filters)
        nunoccf = len(self.unocc_filters)
        if (yield_electrons or yield_holes) and not self._is_time_density_matrices:
            raise ValueError('Electron or hole densities can only be computed in the time domain.')

        resultkeys = ResultKeys()
        if yield_total:
            resultkeys.add_key('rho_g', self.gdshape)

        if yield_holes:
            resultkeys.add_key('occ_rho_g', self.gdshape)
            if noccf > 0:
                resultkeys.add_key('occ_rho_rows_fg', (noccf, ) + self.gdshape)
                resultkeys.add_key('occ_rho_diag_fg', (noccf, ) + self.gdshape)

        if yield_electrons:
            resultkeys.add_key('unocc_rho_g', self.gdshape)
            if nunoccf > 0:
                resultkeys.add_key('unocc_rho_rows_fg', (nunoccf, ) + self.gdshape)
                resultkeys.add_key('unocc_rho_diag_fg', (nunoccf, ) + self.gdshape)

        return resultkeys

    @property
    def _need_derivatives_real_imag(self) -> tuple[list[int], bool, bool]:
        # Time domain: We only need the real part of the density matrix.
        # Frequency domain: We need the (complex) Fourier transform of
        #                   the real part of the density matrix.
        return ([0], True, False)

    def _find_limit(self,
                    lim: float) -> int:
        """ Find the first eigenvalue larger than :attr:`lim`.

        Parameters
        ----------
        lim
            Threshold value in units of eV.

        Returns
        -------
        The index of the first eigenvalue larger than :attr:`lim`.
        Returns ``len(eig_n)`` if :attr:`lim` is larger than all eigenvalues.
        """
        if lim > self.eig_n[-1]:
            return len(self.eig_n)
        return int(np.argmax(self.eig_n > lim))

    def _build_single_filter(self,
                             key: str,
                             low: float,
                             high: float) -> slice:
        imin, imax, amin, amax = self.ksd.ialims()

        if key == 'o':
            nlow = min(self._find_limit(low), imax) - imin
            nhigh = min(self._find_limit(high), imax) - imin
        elif key == 'u':
            nlow = min(self._find_limit(low), amax) - amin
            nhigh = min(self._find_limit(high), amax) - amin
        else:
            raise RuntimeError(f'Unknown key {key}. Key must be "o" or "u"')
        return slice(nlow, nhigh)

    def get_density(self,
                    rho_nn: DistributedArray,
                    nn_indices: str,
                    fltn1: slice | NDArray[np.bool_] = slice(None),
                    fltn2: slice | NDArray[np.bool_] = slice(None),
                    u: int = 0) -> DistributedArray:
        r""" Calculate a real space density from a density matrix in the Kohn-Sham basis.

        Parameters
        ----------
        rho_nn
            Density matrix :math:`\delta\rho_{ia}`, :math:`\delta\rho_{ii'}`, or
            :math:`\delta\rho_{aa'}`.
        nn_indices
            Indices describing the density matrices :attr:`rho_nn`. One of

            - `ia` for induced density :math:`\delta\rho_{ia'}`.
            - `ii` for holes density :math:`\delta\rho_{ii'}`.
            - `aa` for electrons density :math:`\delta\rho_{aa'}`.
        flt_n1
            Filter selecting rows of the density matrix.
        flt_n2
            Filter selecting columns of the density matrix.
        u
            Kpoint index.
        Returns
        -------
        Distributed array with the density in real space on the root rank.
        """
        imin, imax, amin, amax = self.ksd.ialims()
        if nn_indices not in ['ia', 'ii', 'aa']:
            raise ValueError(f'Parameter nn_indices must be either "ia", "ii" or "aa". Is {nn_indices}.')
        n1 = slice(imin, imax + 1) if nn_indices[0] == 'i' else slice(amin, amax + 1)
        n2 = slice(imin, imax + 1) if nn_indices[1] == 'i' else slice(amin, amax + 1)

        nn1, nn2 = n1.stop - n1.start, n2.stop - n2.start
        nM = self.ksd.C0_unM[0].shape[-1]

        if self.calc_comm.rank == 0:
            C0_nM = self.ksd.C0_unM[u]
            rho_n1n2 = ParallelMatrix((nn1, nn2), np.float64, comm=self.calc_comm,
                                      array=rho_nn[fltn1][:, fltn2])
            C0_n1M = ParallelMatrix((nn1, nM), np.float64, comm=self.calc_comm,
                                    array=C0_nM[n1][fltn1])
            C0_n2M = ParallelMatrix((nn2, nM), np.float64, comm=self.calc_comm,
                                    array=C0_nM[n2][fltn2])
        else:
            rho_n1n2 = ParallelMatrix((nn1, nn2), np.float64, comm=self.calc_comm)
            C0_n1M = ParallelMatrix((nn1, nM), np.float64, comm=self.calc_comm)
            C0_n2M = ParallelMatrix((nn2, nM), np.float64, comm=self.calc_comm)

        # Transform to LCAO basis C0_n1M.T @ rho_n1n2 @ C0_n2M
        self.log.start('transform_dm')

        rho_MM = (C0_n1M.T @ rho_n1n2 @ C0_n2M).broadcast()
        # assert np.issubdtype(rho_nn.dtype, float)
        rho_MM = 0.5 * (rho_MM + rho_MM.T)

        msg = f'Transformed DM and constructed density in {self.log.elapsed("transform_dm"):.1f}s'
        self.log.start('get_density')
        rho_g = get_density(rho_MM, self.calc.wfs, self.calc.density, u=u)
        msg += f'+{self.log.elapsed("get_density"):.1f}s'
        if self.calc_comm.rank == 0:
            self.log_parallel(msg, flush=True)

        big_rho_g = self.gd.collect(rho_g)

        if self.calc_comm.rank == 0:
            return big_rho_g
        else:
            return ArrayIsOnRootRank()

    def icalculate(self,
                   yield_total: bool = True,
                   yield_electrons: bool = False,
                   yield_holes: bool = False) -> Generator[tuple[WorkMetadata, Result], None, None]:
        """ Iteratively calculate results.

        Parameters
        ----------
        yield_total
            The results should include the total induced density.
        yield_holes
            The results should include the holes densities, optionally decomposed by `filter_occ`.
        yield_electrons
            The results should include the electrons densities, optionally decomposed by `filter_unocc`.

        Yields
        ------
        Tuple (work, result) on the root rank of the calculation communicator. \
        Does not yield on non-root ranks of the calculation communicator.

            work
                An object representing the metadata (time, frequency or pulse) for the work done.
            result
                Object containg the calculation results for this time, frequency or pulse.
        """
        noccf = len(self.occ_filters)
        nunoccf = len(self.unocc_filters)

        if (yield_electrons or yield_holes) and not self._is_time_density_matrices:
            raise ValueError('Electron or hole densities can only be computed in the time domain.')

        # Iterate over the pulses and times, or frequencies
        for work, dm in self.density_matrices:
            if self._is_time_density_matrices:
                # Real part contributes to density
                rho_ia = dm.rho_ia.real
            else:
                # Imaginary part gives absorption contribution
                rho_ia = -dm.rho_ia.imag

            self.log.start('calculate')

            # Non-root ranks on calc_comm will write empty arrays to result, but will not be yielded
            result = Result()

            if yield_total:
                result['rho_g'] = self.get_density(rho_ia.real, 'ia') * Bohr ** -3

            if yield_holes:
                # Holes
                M_ii = 0.5 * (dm.Q_ia @ dm.Q_ia.T + dm.P_ia @ dm.P_ia.T)

                result['occ_rho_g'] = self.get_density(M_ii, 'ii') * Bohr ** -3

                if noccf > 0:
                    result['occ_rho_rows_fg'] = np.array([self.get_density(M_ii, 'ii', fltn1=flt)
                                                          for flt in self.occ_filters]) * Bohr ** -3
                    result['occ_rho_diag_fg'] = np.array([self.get_density(M_ii, 'ii', fltn1=flt, fltn2=flt)
                                                          for flt in self.occ_filters]) * Bohr ** -3

            if yield_electrons:
                # Electrons
                M_aa = 0.5 * (dm.Q_ia.T @ dm.Q_ia + dm.P_ia.T @ dm.P_ia)

                result['unocc_rho_g'] = self.get_density(M_aa, 'aa') * Bohr ** -3

                if nunoccf > 0:
                    result['unocc_rho_rows_fg'] = np.array([self.get_density(M_aa, 'aa', fltn1=flt)
                                                            for flt in self.unocc_filters]) * Bohr ** -3
                    result['unocc_rho_diag_fg'] = np.array([self.get_density(M_aa, 'aa', fltn1=flt, fltn2=flt)
                                                            for flt in self.unocc_filters]) * Bohr ** -3
            if dm.rank > 0:
                continue

            self.log_parallel(f'Calculated density in {self.log.elapsed("calculate"):.2f}s '
                              f'for {work.desc}', flush=True)

            yield work, result

        if self.calc_comm.rank == 0:
            self.log_parallel('Finished calculating density contributions', flush=True)

    def calculate_and_write(self,
                            out_fname: str,
                            which: str | list[str] = 'induced',
                            write_extra: dict[str, Any] = dict()):
        """ Calculate density contributions.

        Densities are saved in a numpy archive, ULM file or cube file depending on
        whether the file extension is ``.npz``, ``.ulm``, or ``.cube``.

        If the file extension is ``.cube`` then :attr:`out_fname` is taken to be a formatting string.

        The formatting string should be a plain string containing variable
        placeholders within curly brackets ``{}``. It should not be confused with
        a formatted string literal (f-string).

        It acccepts variables

         * ``{time}`` - Time in units of as (time domain only).
         * ``{freq}`` - Frequency in units of eV (frequency domain only).
         * ``{which}`` - The :attr:`which` argument.
         * ``{pulsefreq}`` - Pulse frequency in units of eV (time domain only).
         * ``{pulsefwhm}`` - Pulse FWHM in units of fs (time domain only).

        Examples:

         * out_fname = `{which}_density_t{time:09.1f}.cube`.
         * out_fname = `{which}_density_w{freq:05.2f}.cube`.

        Parameters
        ----------
        out_fname
            File name of the resulting data file.
        which
            String, or list of strings specifying the types of density to compute:

            * `induced` - Induced density.
            * `holes` - Holes density (only allowed in the time domain).
            * `electrons` - Electrons density (only allowed in the time domain).
        write_extra
            Dictionary of extra key-value pairs to write to the data file.
        """
        from ..writers.density import DensityWriter, write_density
        from ..writers.writer import FrequencyResultsCollector, TimeResultsCollector

        cls = TimeResultsCollector if self._is_time_density_matrices else FrequencyResultsCollector

        if isinstance(which, str):
            which = [which]

        for which_key in which:
            if which_key in ['holes', 'electrons'] and not self._is_time_density_matrices:
                raise ValueError(f'Option which={which_key} not allowed in the frequency domain.')
            if which_key not in ['induced', 'holes', 'electrons']:
                raise ValueError(f'Option which={which} not recognized. '
                                 'Must be one of: induced, holes, electrons')

        calc_kwargs = dict(yield_total='induced' in which,
                           yield_holes='holes' in which,
                           yield_electrons='electrons' in which)

        keys = {'induced': 'rho_g',
                'holes': 'occ_rho_g',
                'electrons': 'unocc_rho_g'}

        out_fname = str(out_fname)
        if out_fname.endswith('.npz'):
            exclude = ['occ_rho_rows_fg', 'occ_rho_diag_fg', 'unocc_rho_rows_fg', 'unocc_rho_diag_fg']
            writer = DensityWriter(cls(self, calc_kwargs=calc_kwargs, exclude=exclude))
            writer.calculate_and_save_npz(out_fname=out_fname, write_extra=write_extra)
        elif out_fname.endswith('.ulm'):
            exclude = ['rho_g', 'occ_rho_rows_fg', 'occ_rho_diag_fg', 'unocc_rho_rows_fg', 'unocc_rho_diag_fg']
            writer = DensityWriter(cls(self, calc_kwargs=calc_kwargs, exclude=exclude))
            writer.calculate_and_save_ulm(out_fname=out_fname, write_extra=write_extra)
        elif out_fname.endswith('.cube'):
            atoms = self.calc.atoms
            for work, res in self.icalculate(**calc_kwargs):
                if self.calc_comm.rank > 0:
                    continue
                for which_key in which:
                    key = keys[which_key]
                    fname_kw: dict[str, float | str] = dict(which=which_key)
                    data = res[key]
                    if self._is_time_density_matrices:
                        assert isinstance(work, ConvolutionDensityMatrixMetadata)
                        fname_kw.update(time=work.time, **get_gaussian_pulse_values(work.pulse))
                    else:
                        assert isinstance(work, FrequencyDensityMatrixMetadata)
                        fname_kw.update(freq=work.freq)
                    fpath = Path(out_fname.format(**fname_kw))
                    fpath.parent.mkdir(parents=True, exist_ok=True)
                    write_density(str(fpath), atoms, data)
                    self.log_parallel(f'Written {fpath}', flush=True)

        else:
            raise ValueError(f'output-file must have ending .npz or .ulm, is {out_fname}')
