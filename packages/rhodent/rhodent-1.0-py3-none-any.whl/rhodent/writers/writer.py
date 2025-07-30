from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
import numpy as np
from numpy.typing import NDArray

from gpaw.mpi import world
from gpaw.io import Writer as GPAWWriter

from ..density_matrices.base import WorkMetadata, WorkMetadataT, BaseDensityMatrices
from ..density_matrices.frequency import FrequencyDensityMatrices, FrequencyDensityMatrixMetadata
from ..density_matrices.time import ConvolutionDensityMatrices, ConvolutionDensityMatrixMetadata
from ..calculators.base import BaseObservableCalculator
from ..voronoi import VoronoiWeights, EmptyVoronoiWeights, atom_projections_to_numpy
from ..utils import Result, ResultKeys


class ResultsCollector(ABC, Generic[WorkMetadataT]):

    """ Utility class to collect result arrays for different
    times, pulses, or frequencies.

    Parameters
    ----------
    resultkeys
        Result keys to be collected.
    additional_dimension
        Shape of additional dimension(s) due to the different times, frequencies, etc.
    additional_suffix
        String prepended to the suffix if each key.
    """

    def __init__(self,
                 calc: BaseObservableCalculator,
                 calc_kwargs: dict[str, Any],
                 resultkeys: ResultKeys,
                 additional_suffix: str,
                 additional_dimension: tuple[int, ...],
                 exclude: list[str] = []):
        self.calc = calc
        self.calc_kwargs = calc_kwargs
        self.resultkeys = resultkeys.__copy__()
        for key in exclude:
            if key in self.resultkeys:
                self.resultkeys.remove(key)
        self.additional_dimension = additional_dimension
        self.additional_suffix = additional_suffix

        # Create the new result keys for the aggregated data
        self.collect_resultkeys = ResultKeys()
        for key, shape, dtype in self.resultkeys:
            newkey = self.format_key(key)
            self.collect_resultkeys.add_key(newkey, additional_dimension + shape, dtype)

        self.result = Result(mutable=True)

    def empty_results(self):
        if world.rank == 0:
            self.result.create_all_zeros(self.collect_resultkeys)

    def finalize_results(self):
        pass

    def format_key(self,
                   key: str) -> str:
        """ Add the new suffix to the key.

        Parameters
        ----------
        key
            Original result key.

        Returns
        -------
        New result key with the added suffix.
        """
        shape, _ = self.resultkeys[key]
        if len(shape) == 0:
            return key + f'_{self.additional_suffix}'

        s = key.split('_')
        assert len(s) > 1
        s[-1] = self.additional_suffix + s[-1]
        return '_'.join(s)

    @abstractmethod
    def accumulate_results(self,
                           work: WorkMetadataT,
                           result: Result):
        pass


ResultsCollectorT = TypeVar('ResultsCollectorT', bound=ResultsCollector)


class TimeResultsCollector(ResultsCollector):

    """ Collect results after convolution with different pulses.

    The letter t is prepended to the suffix of the result keys to indicate
    an additional dimension of time.

    Parameters
    ----------
    calc
        Calculator.
    calc_kwargs
        Keyword arguments passed to the icalculate function.
    exclude
        Keys that are excluded from collection.
    """

    def __init__(self,
                 calc: BaseObservableCalculator,
                 calc_kwargs: dict[str, Any],
                 exclude: list[str] = []):
        assert isinstance(calc.density_matrices, ConvolutionDensityMatrices)
        assert len(calc.density_matrices.pulses) == 1
        Nt = len(calc.times)

        resultkeys = calc.get_result_keys(**calc_kwargs)
        super().__init__(calc, calc_kwargs, resultkeys,
                         additional_suffix='t', additional_dimension=(Nt, ), exclude=exclude)

    def accumulate_results(self,
                           work: ConvolutionDensityMatrixMetadata,
                           result: Result):
        assert isinstance(work, ConvolutionDensityMatrixMetadata)
        assert world.rank == 0

        for key, _, _ in self.resultkeys:
            newkey = self.format_key(key)
            self.result.set_to(newkey, work.globalt, result[key])


class TimeAverageResultsCollector(ResultsCollector):

    """ Collect results and average over times.

    Parameters
    ----------
    calc
        Calculator.
    calc_kwargs
        Keyword arguments passed to the icalculate function.
    exclude
        Keys that are excluded from collection.
    """

    def __init__(self,
                 calc: BaseObservableCalculator,
                 calc_kwargs: dict[str, Any],
                 exclude: list[str] = []):
        assert isinstance(calc.density_matrices, ConvolutionDensityMatrices)
        assert len(calc.density_matrices.pulses) == 1

        resultkeys = calc.get_result_keys(**calc_kwargs)
        super().__init__(calc, calc_kwargs, resultkeys,
                         additional_suffix='', additional_dimension=(), exclude=exclude)

    def accumulate_results(self,
                           work: ConvolutionDensityMatrixMetadata,
                           result: Result):
        assert isinstance(work, ConvolutionDensityMatrixMetadata)
        assert world.rank == 0

        for key, _, _ in self.resultkeys:
            newkey = self.format_key(key)
            self.result.add_to(newkey, slice(None), result[key])

    def finalize_results(self):
        if world.rank > 0:
            return

        nt = len(self.calc.density_matrices.times)
        for key, _, _ in self.collect_resultkeys:
            self.result[key] /= nt


class PulseConvolutionResultsCollector(ResultsCollector):

    """ Collect results after convolution with different pulses.

    The letters pt are prepended to the suffix of the result keys to indicate
    an additional dimension of pulse and time.

    Parameters
    ----------
    calc
        Calculator.
    calc_kwargs
        Keyword arguments passed to the icalculate function.
    exclude
        Keys that are excluded from collection.
    """

    def __init__(self,
                 calc: BaseObservableCalculator,
                 calc_kwargs: dict[str, Any],
                 exclude: list[str] = []):
        assert isinstance(calc.density_matrices, ConvolutionDensityMatrices)
        Np = len(calc.pulses)
        Nt = len(calc.times)

        resultkeys = calc.get_result_keys(**calc_kwargs)
        super().__init__(calc, calc_kwargs, resultkeys,
                         additional_suffix='pt', additional_dimension=(Np, Nt), exclude=exclude)

    def accumulate_results(self,
                           work: ConvolutionDensityMatrixMetadata,
                           result: Result):
        assert isinstance(work, ConvolutionDensityMatrixMetadata)
        assert world.rank == 0

        for key, _, _ in self.resultkeys:
            newkey = self.format_key(key)
            self.result.set_to(newkey, (work.globalp, work.globalt), result[key])


class PulseConvolutionAverageResultsCollector(ResultsCollector):

    """ Collect results after convolution with different pulses, average over times.

    The letter p is prepended to the suffix of the result keys to indicate
    an additional dimension of pulse.

    Parameters
    ----------
    calc
        Calculator.
    calc_kwargs
        Keyword arguments passed to the icalculate function.
    exclude
        Keys that are excluded from collection.
    """

    def __init__(self,
                 calc: BaseObservableCalculator,
                 calc_kwargs: dict[str, Any],
                 exclude: list[str] = []):
        assert isinstance(calc.density_matrices, ConvolutionDensityMatrices)
        Np = len(calc.pulses)

        resultkeys = calc.get_result_keys(**calc_kwargs)
        super().__init__(calc, calc_kwargs, resultkeys,
                         additional_suffix='p', additional_dimension=(Np, ), exclude=exclude)

    def accumulate_results(self,
                           work: ConvolutionDensityMatrixMetadata,
                           result: Result):
        assert isinstance(work, ConvolutionDensityMatrixMetadata)
        assert world.rank == 0

        for key, _, _ in self.resultkeys:
            newkey = self.format_key(key)
            self.result.add_to(newkey, work.globalp, result[key])

    def finalize_results(self):
        if world.rank > 0:
            return

        nt = len(self.calc.density_matrices.times)
        for key, _, _ in self.collect_resultkeys:
            self.result[key] /= nt


class FrequencyResultsCollector(ResultsCollector):

    """ Collect results in the frequency domain.

    This class should work with the Fourier transform of
    the real part of density matrices.

    The letter w is prepended to the suffix of the result keys to indicate
    an additional dimension of frequency.

    Parameters
    ----------
    calc
        Calculator.
    calc_kwargs
        Keyword arguments passed to the icalculate function.
    exclude
        Keys that are excluded from collection
    """

    def __init__(self,
                 calc: BaseObservableCalculator,
                 calc_kwargs: dict[str, Any],
                 exclude: list[str] = []):
        assert isinstance(calc.density_matrices, FrequencyDensityMatrices)
        Nw = len(calc.frequencies)
        assert 'Im' not in calc.density_matrices.reim

        resultkeys = calc.get_result_keys(**calc_kwargs)
        super().__init__(calc, calc_kwargs, resultkeys,
                         additional_suffix='w', additional_dimension=(Nw, ), exclude=exclude)

    def accumulate_results(self,
                           work: FrequencyDensityMatrixMetadata,
                           result: Result):
        assert isinstance(work, FrequencyDensityMatrixMetadata)
        assert world.rank == 0

        for key, _, _ in self.resultkeys:
            newkey = self.format_key(key)
            self.result.set_to(newkey, work.globalw, result[key])


class Writer(Generic[ResultsCollectorT]):

    def __init__(self, collector: ResultsCollectorT):
        self._collector = collector
        self._ulm_tag = 'RhodentResults'

    @property
    def collector(self) -> ResultsCollectorT:
        return self._collector

    @property
    def calc(self) -> BaseObservableCalculator:
        return self.collector.calc

    @property
    def density_matrices(self) -> BaseDensityMatrices:
        return self.collector.calc.density_matrices

    @property
    def voronoi(self) -> VoronoiWeights:
        voronoi = self.calc.voronoi
        if voronoi is None:
            return EmptyVoronoiWeights()
        return voronoi

    @property
    def common_arrays(self) -> dict[str, NDArray[np.float64] | NDArray[np.int64] | int | float]:
        """ Dictionary of eigenvalues and limits. """
        imin, imax, amin, amax = self.calc.ksd.ialims()
        arrays: dict[str, NDArray[np.float64] | NDArray[np.int64] | int | float] = dict()
        arrays['eig_n'] = self.calc.eig_n
        arrays['eig_i'] = self.calc.eig_i
        arrays['eig_a'] = self.calc.eig_a
        arrays['imin'] = imin
        arrays['imax'] = imax
        arrays['amin'] = amin
        arrays['amax'] = amax

        return arrays

    @property
    def icalculate_kwargs(self) -> dict:
        """ Keyword arguments to icalculate. """
        return self.collector.calc_kwargs

    def fill_ulm(self,
                 writer,
                 work: WorkMetadata,
                 result: Result):
        """ Fill one entry of the ULM file.

        Parameters
        ----------
        writer
            Open ULM writer object.
        work
            Metadata to current piece of data.
        result
            Result containing the current observables.
        """
        raise NotImplementedError

    def write_empty_arrays_ulm(self, writer):
        """ Add empty arrays in to the ULM file.

        Parameters
        ----------
        writer
            Open ULM writer object.
        """
        raise NotImplementedError

    def calculate_data(self) -> Result:
        """ Calculate results on all ranks and return Result object.

        Returns
        -------
        Retult object. Is empty on non-root ranks.
        """
        self.collector.empty_results()

        for work, res in self.calc.icalculate_gather_on_root(**self.icalculate_kwargs):
            self.collector.accumulate_results(work, res)

        self.collector.finalize_results()

        return self.collector.result

    def calculate_and_save_npz(self,
                               out_fname: str,
                               write_extra: dict[str, Any] = dict()):
        """ Calculate results on all ranks and save to npz file.

        Parameters
        ----------
        out_fname
            File name.
        """
        result = self.calculate_data()

        if world.rank > 0:
            return

        atom_projections = atom_projections_to_numpy(self.voronoi.atom_projections)
        np.savez(out_fname, **self.common_arrays, **result._data,  # type: ignore
                 atom_projections=atom_projections)
        self.calc.log_parallel(f'Written {out_fname}', flush=True)

    def calculate_and_save_ulm(self,
                               out_fname: str,
                               write_extra: dict[str, Any] = dict()):
        """ Calculate results on all ranks and save to ULM file.

        Parameters
        ----------
        out_fname
            File name.
        """
        self.collector.empty_results()

        with GPAWWriter(out_fname, world, mode='w', tag=self._ulm_tag[:16]) as writer:
            writer.write(version=1)
            writer.write('atom_projections', self.voronoi.atom_projections)
            writer.write(**(self.common_arrays if world.rank == 0 else dict()))

            self.write_empty_arrays_ulm(writer)

            for work, res in self.calc.icalculate_gather_on_root(**self.icalculate_kwargs):
                self.fill_ulm(writer, work, res)
                self.collector.accumulate_results(work, res)

            self.collector.finalize_results()
            writer.write(**self.collector.result._data)

        if world.rank == 0:
            self.calc.log_parallel(f'Written {out_fname}', flush=True)
