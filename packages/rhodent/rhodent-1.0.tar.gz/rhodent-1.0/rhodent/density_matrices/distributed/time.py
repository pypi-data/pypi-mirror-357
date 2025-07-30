from __future__ import annotations

from typing import Generator
import numpy as np

from .base import RhoParameters
from rhodent.density_matrices.buffer import DensityMatrixBuffer
from rhodent.density_matrices.readers.gpaw import KohnShamRhoWfsReader
from rhodent.utils import safe_fill
from .base import BaseDistributor, RhoIndices
from ...typing import Communicator
from ...utils.memory import MemoryEstimate


class TimeDistributor(BaseDistributor):

    """ Iteratively read density matrices in the time domain

    This class uses the KohnShamRhoWfsReader to iteratively read wave functions
    (each rank reading the same times) and construct density matrices in the ground state
    Kohn-Sham basis for each time. The different ranks are reading different chunks of
    the density matrices. The density matrices are accumulated in a buffer and yielded
    when all times have been read.

    Parameters
    ----------
    rho_reader
        Density matrices reader
    comm
        Communicator
    log
        Logger
    """

    def __init__(self,
                 rho_reader: KohnShamRhoWfsReader,
                 parameters: RhoParameters | None = None,
                 comm: Communicator | None = None):
        if rho_reader.comm.size > 1:
            raise ValueError('Serial TimeDistributor must have serial reader.')

        super().__init__(rho_reader, parameters, comm=comm)

    @property
    def dtype(self):
        return np.float64

    @property
    def xshape(self):
        return (self.nt, )

    @property
    def dt(self):
        return self.rho_wfs_reader.dt

    @property
    def nt(self):
        return self.rho_wfs_reader.nt

    @property
    def time_t(self):
        return self.rho_wfs_reader.time_t

    def __str__(self) -> str:
        lines = []
        lines.append('Density matrices reader')
        lines.append('  Receiving density matrices in continuous chunks.')
        lines.append(f'    shape {self._parameters.nnshape}')
        lines.append(f'    received by {self.maxntimes} ranks')
        lines.append(f'  {self.niters} iterations to process all chunks')

        return '\n'.join(lines)

    def get_memory_estimate(self) -> MemoryEstimate:
        narrays = (2 if self.yield_re and self.yield_im else 1) * len(self.derivative_order_s)
        shape = self._parameters.nnshape + (self.nt, narrays)

        comment = f'Buffers hold {narrays} arrays ({self.describe_reim()})'
        memory_estimate = MemoryEstimate(comment=comment)
        memory_estimate.add_key('Density matrix buffers', shape, float,
                                on_num_ranks=self.comm.size)

        return memory_estimate

    def __iter__(self) -> Generator[DensityMatrixBuffer, None, None]:
        """ Yield density matrices for all times, chunk by chunk

        The wave function file is read in chunks, time by time, with
        the reading of times in the inner loop.

        Yields
        ------
        Chunks of the density matrix
        """
        read_dm = DensityMatrixBuffer(self._parameters.nnshape,
                                      (self.nt, ),
                                      np.float64)
        if self.yield_re:
            read_dm.zeros(True, 0)
        if self.yield_im:
            read_dm.zeros(False, 0)

        self.rho_wfs_reader.parallel_prepare()

        # Loop over the chunks this rank should gather
        for indices in self.work_loop(self.comm.rank):
            if indices is None:
                continue
            # Convert to reading indices
            n1 = slice(self._parameters.n1min + indices.n1.start, self._parameters.n1min + indices.n1.stop)
            n2 = slice(self._parameters.n2min + indices.n2.start, self._parameters.n2min + indices.n2.stop)
            gen = self.rho_wfs_reader.iread(indices.s, indices.k, n1, n2)
            for t in self.rho_wfs_reader.work_loop(self.rho_wfs_reader.comm.rank):
                if t is None:
                    continue
                dm_buffer = next(gen)
                for source_nn, dest_nn in zip(dm_buffer._iter_buffers(), read_dm[t]._iter_buffers()):
                    dest_nn[:] = source_nn

            yield read_dm

    @classmethod
    def from_reader(cls,
                    rho_nn_reader: KohnShamRhoWfsReader,
                    parameters: RhoParameters,
                    **kwargs) -> TimeDistributor:
        return cls(rho_nn_reader, parameters, **kwargs)


class AlltoallvTimeDistributor(TimeDistributor):

    """ Iteratively read density matrices in the time domain

    This class uses the KohnShamRhoWfsReader to iteratively read wave functions
    (one time per rank) and construct density matrices in the ground state Kohn-Sham
    basis for each time. When all ranks have read one time each, this class
    performs a redistribution of data, such that each rank only gets one chunk of the
    density matrices, but for all times. The density matrices are accumulated in a
    buffer and yielded when all times have been read.

    Parameters
    ----------
    rho_reader
        Density matrices reader
    """

    def __init__(self,
                 rho_reader: KohnShamRhoWfsReader,
                 parameters: RhoParameters | None = None):
        if rho_reader.lcao_rho_reader.striden != 0:
            raise ValueError('n stride must be 0 (index all) for alltoallv parallelized method')

        BaseDistributor.__init__(self, rho_reader, parameters, comm=rho_reader.comm)

    def __str__(self) -> str:
        nnshape = self.rho_wfs_reader.nnshape(*self.first_indices())

        lines = []
        lines.append('Parallel density matrices reader')
        lines.append('  Receiving density matrices in continuous chunks.')
        lines.append(f'    densiy matrix continous chunk {nnshape}')
        lines.append(f'    split into smaller chunks {self._parameters.nnshape}')
        lines.append(f'    received by {self.maxntimes} ranks')
        lines.append('  Redistributing into continuous time form.')
        lines.append(f'    sent to {self.maxnchunks} ranks')
        lines.append(f'  {self.niters} iterations to process all chunks')

        return '\n'.join(lines)

    def get_memory_estimate(self) -> MemoryEstimate:
        narrays = (2 if self.yield_re and self.yield_im else 1) * len(self.derivative_order_s)

        nnshape = self.rho_wfs_reader.nnshape(*self.first_indices())

        before_shape = self._parameters.nnshape + (self.maxnchunks, narrays)
        after_shape = self._parameters.nnshape + (self.nt, narrays)
        total_after_size = np.prod(self._parameters.nnshape + (self.nt, )) * self.maxnchunks * narrays

        shape = nnshape + (narrays, )

        comment = f'Buffers hold {narrays} arrays ({self.describe_reim()})'
        memory_estimate = MemoryEstimate(comment=comment)
        memory_estimate.add_key('Density matrix chunks', shape, float,
                                on_num_ranks=self.maxntimes)
        memory_estimate.add_key('Before parallel redistribution', before_shape, float,
                                on_num_ranks=self.maxntimes)
        memory_estimate.add_key('After parallel redistribution', after_shape, float,
                                total_size=total_after_size,
                                on_num_ranks=self.maxnchunks)

        return memory_estimate

    def first_indices(self):
        for first_indices_r in self.work_loop_by_ranks():
            break

        indices_by_rank = [chunk for chunk in first_indices_r if chunk is not None]
        indices_concat, _ = RhoIndices.concatenate_indices(indices_by_rank)
        return indices_concat

    def __iter__(self) -> Generator[DensityMatrixBuffer, None, None]:
        """ Yield density matrices for all times, chunk by chunk

        The wave function file is read in chunks, time by time. However,
        chunks are grouped together so that the density matrix at each
        time is read in large chunks. Each rank reads the same chunk for
        a different time. Then, the chunks and times are redistributed,
        so that each rank now holds a small chunk, but for many times.
        The same chunk is read for all times before it is yielded.

        Yields
        ------
        Chunks of the density matrix
        """
        log = self.log

        self.rho_wfs_reader.parallel_prepare()

        # Here x is a compound index for a slice of both n and M
        for chunki, chunks_r in enumerate(self.work_loop_by_ranks()):
            log.start('read_alltoallv')

            # The work this rank is supposed to read
            indices = chunks_r[self.comm.rank]
            indices_by_rank = [chunk for chunk in chunks_r if chunk is not None]

            # Number of chunks of nn-indices being read
            nchunks = len(indices_by_rank)
            assert nchunks > 0

            # Find out how much of the total density matrix need to be read to get only
            # the required chunks
            indices_concat, reduced_indices_by_rank = RhoIndices.concatenate_indices(indices_by_rank)

            if indices is None:
                # This rank does not want any slices of n1 and n2.
                # It will still potentially participate in the parallel reading of times
                assert self.comm.rank >= nchunks

            n1 = slice(self._parameters.n1min + indices_concat.n1.start,
                       self._parameters.n1min + indices_concat.n1.stop)
            n2 = slice(self._parameters.n2min + indices_concat.n2.start,
                       self._parameters.n2min + indices_concat.n2.stop)

            if self.comm.rank < self.maxntimes:
                # This rank will read
                contiguous_chunks_buffer = DensityMatrixBuffer(self._parameters.nnshape,
                                                               (nchunks, ),
                                                               np.float64)
            else:
                # This rank does not read any times
                contiguous_chunks_buffer = DensityMatrixBuffer(self._parameters.nnshape,
                                                               (0, ),
                                                               np.float64)
            if self.comm.rank < nchunks:
                # This rank will get a chunk of the density matrices after redistribution
                contiguous_time_buffer = DensityMatrixBuffer(self._parameters.nnshape,
                                                             (self.nt, ),
                                                             np.float64)
            else:
                contiguous_time_buffer = DensityMatrixBuffer(self._parameters.nnshape,
                                                             (0, ),
                                                             np.float64)
            if self.yield_re:
                contiguous_chunks_buffer.zeros(True, 0)
                contiguous_time_buffer.zeros(True, 0)
            if self.yield_im:
                contiguous_chunks_buffer.zeros(False, 0)
                contiguous_time_buffer.zeros(False, 0)

            gen = self.rho_wfs_reader.iread(indices_concat.s, indices_concat.k, n1, n2)

            for t_r in self.rho_wfs_reader.work_loop_by_ranks():
                # Number of times being read
                ntimes = sum(1 for t in t_r if t is not None)
                # Time index this rank is reading, or None if not reading
                globalt = t_r[self.comm.rank]

                # Read the density matrices for one time per rank,
                # with each rank reading a large chunk of the density matrix
                if globalt is not None:
                    read_dm = next(gen)

                    for recvrank, readindices in enumerate(reduced_indices_by_rank):
                        for source_nn, dest_nn in zip(read_dm._iter_buffers(),
                                                      contiguous_chunks_buffer[recvrank]._iter_buffers()):
                            safe_fill(dest_nn, source_nn[readindices.n1, readindices.n2])
                else:
                    # This rank actually has no time to read (number of times
                    # is not evenly divisible by number of ranks, and this rank
                    # is trying to read past the end)
                    # This rank will still participate in the alltoallv operation
                    assert self.comm.rank >= ntimes

                # Perform the redistributions, so that each rank now holds
                # a smaller chunk of the density matrix, but for many times.
                contiguous_chunks_buffer.redistribute(
                        contiguous_time_buffer, comm=self.comm,
                        source_indices_r=[(r, ) if r < nchunks else None for r in range(self.comm.size)],
                        target_indices_r=[None if t is None else (t, ) for t in t_r],
                        log=log if 0 in t_r else None)

            if self.comm.rank == 0:
                log(f'Chunk {chunki+1}/{self.niters}: Read and distributed density matrices in '
                    f'{log.elapsed("read_alltoallv"):.1f}s', who='Response', flush=True)

            if indices is not None:
                yield contiguous_time_buffer
