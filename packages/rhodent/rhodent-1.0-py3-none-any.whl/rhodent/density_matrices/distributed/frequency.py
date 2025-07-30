from __future__ import annotations

from typing import Generator
import numpy as np

from gpaw.tddft.units import au_to_eV

from .base import BaseDistributor, RhoParameters
from .time import TimeDistributor, AlltoallvTimeDistributor
from ..buffer import DensityMatrixBuffer
from ..readers.gpaw import KohnShamRhoWfsReader
from ...utils import get_array_filter, safe_fill_larger, fast_pad
from ...utils.logging import format_frequencies
from ...utils.memory import MemoryEstimate
from ...perturbation import create_perturbation, PerturbationLike
from ...typing import Array1D


class FourierTransformer(BaseDistributor):

    """ Iteratively take the Fourier transform of density matrices.

    Parameters
    ----------
    rho_nn_reader
        Object that can iteratively read density matrices in the time domain,
        distributed such that different ranks have different chunks of the density
        matrix, but each ranks has all times for the same chunk.
    perturbation
        The perturbation which the density matrices are a response to.
    filter_frequencies
        After Fourier transformation keep only these frequencies (or the frequencies
        closest to them). In atomic units.
    frequency_broadening
        Gaussian broadening width in atomic units. Default (0) is no broadening.
    result_on_ranks
        List of ranks among which the resulting arrays will be distributed.
        Empty list (default) to distribute among all ranks.
    """

    def __init__(self,
                 rho_nn_reader: TimeDistributor,
                 perturbation: PerturbationLike,
                 filter_frequencies: list[float] | Array1D[np.float64] | None = None,
                 frequency_broadening: float = 0,
                 result_on_ranks: list[int] = []):
        super().__init__(rho_nn_reader.rho_wfs_reader,
                         rho_nn_reader._parameters,
                         comm=rho_nn_reader.comm)
        self.rho_nn_reader = rho_nn_reader
        self.perturbation = create_perturbation(perturbation)
        self.frequency_broadening = frequency_broadening
        self._flt_w = get_array_filter(self._omega_w, filter_frequencies)

        if len(result_on_ranks) == 0:
            self._result_on_ranks = set(range(self.comm.size))
        else:
            assert all(isinstance(rank, int) and rank >= 0 and rank < self.comm.size
                       for rank in result_on_ranks), result_on_ranks
            self._result_on_ranks = set(result_on_ranks)

        self._dist_buffer: DensityMatrixBuffer | None = None

    @property
    def dtype(self):
        return np.complex128

    @property
    def xshape(self):
        return (self.nw, )

    @property
    def freq_w(self) -> Array1D[np.float64]:
        return self._omega_w[self.flt_w]  # type: ignore

    @property
    def _omega_w(self) -> Array1D[np.float64]:
        padnt = fast_pad(self.rho_nn_reader.nt)
        dt = self.rho_nn_reader.dt
        omega_w = 2 * np.pi * np.fft.rfftfreq(padnt, dt)

        return omega_w  # type: ignore

    @property
    def nw(self) -> int:
        return len(self.freq_w)

    @property
    def nlocalw(self) -> int:
        return (self.nw + self.nranks_result - 1) // self.nranks_result

    @property
    def flt_w(self) -> slice | Array1D[np.bool_]:
        return self._flt_w

    @property
    def result_on_ranks(self) -> list[int]:
        """ Set of ranks among which the result will be distributed """
        return sorted(self._result_on_ranks)

    @property
    def nranks_result(self) -> int:
        """ Number of ranks that the resulting arrays will be distributed among """
        return len(self._result_on_ranks)

    def distributed_work(self) -> list[list[int]]:
        freqw_r = self.comm.size * [[]]
        for r, rank in enumerate(self.result_on_ranks):
            freqw_r[rank] = list(range(r, self.nw, self.nranks_result))

        return freqw_r

    def my_work(self) -> list[int]:
        freqw_r = self.distributed_work()
        return freqw_r[self.comm.rank]

    def __str__(self) -> str:
        nt = len(self.rho_nn_reader.time_t)
        niters = len(list(self.work_loop_by_ranks()))

        lines = []
        lines.append('Fourier transformer')
        lines.append(f'  Calculating Fourier transform on {self.maxnchunks} ranks')
        lines.append('  Fast Fourier transform')
        lines.append(f'    matrix dimensions {self.rho_nn_reader._parameters.nnshape}')
        lines.append(f'    grid of {nt} times')
        lines.append(f'    {self.describe_reim()}')
        if self.frequency_broadening == 0:
            lines.append('    No frequency broadening')
        else:
            lines.append(f'    Applying frequency broadening of {self.frequency_broadening * au_to_eV:.2f}eV')
        lines.append(f'    keeping frequency grid of {self.nw} frequencies')
        lines.append(f'      {format_frequencies(self.freq_w, units="au")}')
        lines.append('')

        lines.append('  Redistributing into full density matrices')
        lines.append(f'    {niters} iterations to process all chunks')
        lines.append(f'    matrix dimensions {self.rho_nn_reader._parameters.full_nnshape}')
        lines.append(f'    result stored on {self.nranks_result} ranks')

        return '\n'.join(lines)

    def get_memory_estimate(self) -> MemoryEstimate:
        parameters = self.rho_nn_reader._parameters

        narrays = 2 if self.yield_re and self.yield_im else 1
        temp_shape = parameters.nnshape + (self.maxnchunks, self.nlocalw, narrays)
        result_shape = parameters.full_nnshape + (self.nlocalw, narrays)

        total_result_size = int(np.prod(parameters.full_nnshape)) * self.nw * narrays

        comment = f'Buffers hold {narrays} arrays ({self.describe_reim()})'
        own_memory_estimate = MemoryEstimate(comment=comment)
        own_memory_estimate.add_key('Temporary buffer', temp_shape, complex,
                                    on_num_ranks=self.nranks_result)
        own_memory_estimate.add_key('Result buffer', result_shape, complex,
                                    total_size=total_result_size,
                                    on_num_ranks=self.nranks_result)

        memory_estimate = MemoryEstimate()
        memory_estimate.add_child('Time-dependent wave functions reader',
                                  self.rho_nn_reader.rho_wfs_reader.get_memory_estimate())
        memory_estimate.add_child('Parallel density matrices reader',
                                  self.rho_nn_reader.get_memory_estimate())
        memory_estimate.add_child('Fourier transformer',
                                  own_memory_estimate)

        return memory_estimate

    def __iter__(self) -> Generator[DensityMatrixBuffer, None, None]:
        time_t = self.rho_nn_reader.time_t  # Times in wave functions file
        dt = self.rho_nn_reader.dt  # Time step
        padnt = fast_pad(len(time_t))  # Pad with zeros

        dm_buffer = DensityMatrixBuffer(self.rho_nn_reader._parameters.nnshape,
                                        (self.nw, ),
                                        np.complex128)
        if self.yield_re:
            dm_buffer.zeros(True, 0)
        if self.yield_im:
            dm_buffer.zeros(False, 0)

        for read_buffer in self.rho_nn_reader:
            for data_nnt, buffer_nnw in zip(read_buffer._iter_buffers(), dm_buffer._iter_buffers()):
                if self.frequency_broadening == 0:
                    data_nnw = self.perturbation.normalize_frequency_response(data_nnt, time_t, padnt, axis=-1)
                else:
                    data_nnt = self.perturbation.normalize_time_response(data_nnt, time_t, axis=-1)
                    data_nnt[..., :len(time_t)] *= np.exp(-0.5 * self.frequency_broadening ** 2 * time_t**2)
                    data_nnw = np.fft.rfft(data_nnt, n=padnt, axis=-1) * dt
                buffer_nnw[:] = data_nnw[..., self.flt_w].conj()  # Change sign convention

            yield dm_buffer.copy()

    @property
    def dist_buffer(self) -> DensityMatrixBuffer:
        """ Buffer of density matrices on this rank after redistribution """
        if self._dist_buffer is None:
            self._dist_buffer = self.redistribute()
        return self._dist_buffer

    def create_out_buffer(self) -> DensityMatrixBuffer:
        """ Create the DensityMatrixBuffer to hold the temporary density matrix after each redistribution """
        parameters = self.rho_nn_reader._parameters
        nlocalw = self.nlocalw if self.comm.rank in self.result_on_ranks else 0
        out_dm = DensityMatrixBuffer(nnshape=parameters.nnshape,
                                     xshape=(self.maxnchunks, nlocalw),
                                     dtype=np.complex128)
        out_dm.zero_buffers(real=self.yield_re, imag=self.yield_im, derivative_order_s=[0])

        return out_dm

    def create_result_buffer(self) -> DensityMatrixBuffer:
        """ Create the DensityMatrixBuffer to hold the resulting density matrix """
        parameters = self.rho_nn_reader._parameters
        nnshape = parameters.full_nnshape
        full_dm = DensityMatrixBuffer(nnshape=nnshape,
                                      xshape=(len(self.my_work()), ),
                                      dtype=np.complex128)
        full_dm.zero_buffers(real=self.yield_re, imag=self.yield_im, derivative_order_s=[0])

        return full_dm

    def redistribute(self) -> DensityMatrixBuffer:
        """ Perform the Fourier transform and redistribute the data

        When the Fourier transform is performed, the data is distributed such that each rank
        stores the entire time/frequency series for one chunk of the density matrices, i.e. indices n1, n2.

        This function then performs a redistribution of the data such that each rank stores full
        density matrices, for certain frequencies.

        If the density matrices are split into more chunks than there are ranks, then the
        chunks are read, Fourier transformed and distributed in a loop several times until all
        data has been processed.

        Returns
        -------
        Density matrix buffer with x-dimensions (Number of local frequencies, )
        where the Number of local frequencies variers between the ranks.
        """
        local_work = iter(self)
        parameters = self.rho_nn_reader._parameters
        log = self.log
        self.rho_nn_reader.rho_wfs_reader.lcao_rho_reader.striden == 0, \
            'n stride must be 0 (index all) for redistribute'

        # Frequency indices of result on each rank
        freqw_r = self.distributed_work()
        niters = len(list(self.work_loop_by_ranks()))

        out_dm = self.create_out_buffer()
        full_dm = self.create_result_buffer()

        _exhausted = object()

        # Loop over the chunks of the density matrix
        for chunki, indices_r in enumerate(self.work_loop_by_ranks()):
            # At this point, each rank stores one unique chunk of the density matrix.
            # All ranks have the entire time series of data for their own chunk.
            # If there are more chunks than ranks, then this loop will run
            # for several iterations. If the number of chunks is not divisible by the number of
            # ranks then, during the last iteration, some of the chunks are None (meaning the rank
            # currently has no data).

            # List of chunks that each rank currently stores, where element r of the list
            # contains the chunk that rank r works with. Ranks higher than the length of the list
            # currently store no chunks.
            # The list itself is identical on all ranks.
            chunks_by_rank = [indices[2:] for indices in indices_r if indices is not None]

            ntargets = len(chunks_by_rank)

            if self.comm.rank < ntargets:
                # This rank has data to send. Compute the Fourier transform and store the result
                dm_buffer = next(local_work)
            else:
                # This rank has no data to send
                assert next(local_work, _exhausted) is _exhausted
                # Still, we need to create a dummy buffer
                dm_buffer = DensityMatrixBuffer(nnshape=parameters.nnshape,
                                                xshape=(0, ), dtype=np.complex128)
                dm_buffer.zero_buffers(real=self.yield_re, imag=self.yield_im,
                                       derivative_order_s=[0])

            log.start('alltoallv')

            # Redistribute the data:
            # - dm_buffer stores single chunks of density matrices, for all frequencies.
            # - out_dm will store several chunks, for a few frequencies.
            # source_indices_r describes which slices of dm_buffer should be sent to which rank
            # target_indices_r describes to which positions of the out_dm buffer should be received
            # from which rank
            source_indices_r = [None if len(w) == 0 else w for w in freqw_r]
            target_indices_r = [r if r < ntargets else None for r in range(self.comm.size)]
            dm_buffer.redistribute(out_dm,
                                   comm=self.comm,
                                   source_indices_r=source_indices_r,
                                   target_indices_r=target_indices_r,
                                   log=log)

            if self.comm.rank == 0:
                log(f'Chunk {chunki+1}/{niters}: distributed frequency response in '
                    f'{log.elapsed("alltoallv"):.1f}s', flush=True, who='Response')

            for array_nnrw, full_array_nnw in zip(out_dm._iter_buffers(), full_dm._iter_buffers()):
                for r, nn_indices in enumerate(chunks_by_rank):
                    safe_fill_larger(full_array_nnw[nn_indices], array_nnrw[:, :, r])

        assert next(local_work, _exhausted) is _exhausted

        return full_dm

    @classmethod
    def from_reader(cls,  # type: ignore
                    rho_nn_reader: KohnShamRhoWfsReader,
                    parameters: RhoParameters,
                    *,
                    perturbation: PerturbationLike,
                    filter_frequencies: list[float] | Array1D[np.float64] | None = None,
                    frequency_broadening: float = 0,
                    result_on_ranks: list[int] = []) -> FourierTransformer:
        time_distributor = AlltoallvTimeDistributor(rho_nn_reader, parameters)
        fourier_transformer = FourierTransformer(time_distributor,
                                                 perturbation=perturbation,
                                                 filter_frequencies=filter_frequencies,
                                                 frequency_broadening=frequency_broadening,
                                                 result_on_ranks=result_on_ranks)
        return fourier_transformer
