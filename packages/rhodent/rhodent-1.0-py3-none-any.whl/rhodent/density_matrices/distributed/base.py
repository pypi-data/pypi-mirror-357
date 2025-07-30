from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generator, Generic, NamedTuple, Iterable
from itertools import product, zip_longest

import numpy as np

from gpaw.mpi import world
from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition

from ..buffer import DensityMatrixBuffer
from ..readers.gpaw import KohnShamRhoWfsReader
from ...utils import DTypeT, Logger, concatenate_indices, env
from ...typing import Communicator
from ...utils.memory import HasMemoryEstimate


class BaseDistributor(HasMemoryEstimate, ABC, Generic[DTypeT]):

    """ Distribute density matrices over time, frequency or other dimensions across MPI ranks
    """

    def __init__(self,
                 rho_reader: KohnShamRhoWfsReader,
                 parameters: RhoParameters | None = None,
                 comm: Communicator | None = None):
        self.rho_wfs_reader = rho_reader

        self._comm = world if comm is None else comm
        if parameters is None:
            parameters = RhoParameters.from_ksd(self.ksd, self.comm)
        self._parameters = parameters

        self.derivative_order_s = [0]

    @property
    @abstractmethod
    def dtype(self) -> np.dtype[DTypeT]:
        """ Dtype of buffers. """
        raise NotImplementedError

    @property
    @abstractmethod
    def xshape(self) -> tuple[int, ...]:
        """ Shape of x-dimension in buffers. """
        raise NotImplementedError

    @property
    def ksd(self) -> KohnShamDecomposition:
        """ Kohn-Sham decomposition object. """
        return self.rho_wfs_reader.ksd

    @property
    def comm(self) -> Communicator:
        """ MPI communicator. """
        return self._comm

    @property
    def yield_re(self) -> bool:
        """ Whether real part of density matrices is calculated. """
        return self.rho_wfs_reader.yield_re

    @property
    def yield_im(self) -> bool:
        """ Whether imaginary part of density matrices is calculated. """
        return self.rho_wfs_reader.yield_im

    @property
    def log(self) -> Logger:
        """ Logger object. """
        return self.rho_wfs_reader.log

    @abstractmethod
    def __iter__(self) -> Generator[DensityMatrixBuffer, None, None]:
        """ Yield density matrices in parts. Different data is
        yielded on different ranks

        Yields
        ------
        Part of the density matrix
        """
        raise NotImplementedError

    def work_loop(self,
                  rank: int) -> Generator[RhoIndices | None, None, None]:
        """ Like work_loop_by_rank but for one particular rank
        """
        for chunks_r in self.work_loop_by_ranks():
            yield chunks_r[rank]

    @property
    def niters(self) -> int:
        """ Number of iterations needed to read all chunks. """
        return len(list(self.work_loop_by_ranks()))

    @property
    def maxntimes(self) -> int:
        """ Maximum number of ranks participating in reading of times. """
        for t_r in self.rho_wfs_reader.work_loop_by_ranks():
            return sum(1 for t in t_r if t is not None)

        raise RuntimeError

    @property
    def maxnchunks(self) -> int:
        """ Maximum number of ranks participating in reading of chunks. """
        for chunks_r in self.work_loop_by_ranks():
            return sum(1 for chunk in chunks_r if chunk is not None)

        raise RuntimeError

    def describe_reim(self) -> str:
        if self.yield_re and self.yield_im:
            return 'Real and imaginary parts'
        elif self.yield_re:
            return 'Real part'
        else:
            return 'Imaginary part'

    def describe_derivatives(self) -> str:
        return 'derivative orders: ' + ', '.join([str(d) for d in self.derivative_order_s])

    def work_loop_by_ranks(self) -> Generator[list[RhoIndices | None], None, None]:
        """ Yield slice objects corresponding to the chunk of the density matrix
        that is gathered on each rank.

        New indices are yielded until the entire density matrix is processed
        (across all ranks).

        Yields
        ------
        List of slice objects corresponding to part of the density matrix
        yielded on each ranks.  None in place of the slice object if there is
        nothing yielded for that rank.
        """
        gen = self._parameters.iterate_indices()

        while True:
            chunks_r: list[RhoIndices | None] = [indices for _, indices
                                                 in zip(range(self.comm.size), gen)]

            remaining = self.comm.size - len(chunks_r)
            if remaining == 0:
                yield chunks_r
            elif remaining == self.comm.size:
                # There is nothing left to do for any rank
                break
            else:
                # Append Nones for the ranks that are not doing anything
                chunks_r += remaining * [None]
                yield chunks_r
                break

    def gather_on_root(self) -> Generator[DensityMatrixBuffer | None, None, None]:
        self.rho_wfs_reader.C0S_sknM   # Make sure to read this synchronously

        for indices_r, dm_buffer in zip_longest(self.work_loop_by_ranks(),
                                                self, fillvalue=None):
            assert indices_r is not None, 'Work loop shorter than work'

            # Yield root's own work
            if self.comm.rank == 0:
                assert indices_r[0] is not None
                assert dm_buffer is not None
                dm_buffer.ensure_contiguous_buffers()

                yield dm_buffer.copy()
            else:
                yield None

            # Yield the work of non-root
            for recvrank, recvindices in enumerate(indices_r[1:], start=1):
                if recvindices is None:
                    # No work on this recvrank
                    continue

                if self.comm.rank == 0:
                    # Receive work
                    assert dm_buffer is not None
                    dm_buffer.recv_arrays(self.comm, recvrank, log=self.log)
                    yield dm_buffer.copy()
                else:
                    # Send work to root if there is any
                    if self.comm.rank == recvrank:
                        assert dm_buffer is not None
                        dm_buffer.send_arrays(self.comm, 0, log=self.log)
                    yield None

    def collect_on_root(self) -> DensityMatrixBuffer | None:
        gen = self._parameters.iterate_indices()

        nnshape = (self._parameters.n1size, self._parameters.n2size)
        full_dm = DensityMatrixBuffer(nnshape, self.xshape, dtype=self.dtype)
        full_dm.zero_buffers(real=self.yield_re, imag=self.yield_im, derivative_order_s=self.derivative_order_s)

        for indices, dm_buffer in zip_longest(gen,
                                              self.gather_on_root(), fillvalue=None):
            if self.comm.rank != 0:
                continue

            assert indices is not None, 'Iterators must be same length'
            assert dm_buffer is not None, 'Iterators must be same length'

            s, k, n1, n2 = indices
            assert s == 0
            assert k == 0

            for partial_data, full_data in zip(dm_buffer._iter_buffers(), full_dm._iter_buffers()):
                _nn1, _nn2 = full_data[n1, n2].shape[:2]
                # Numpy struggles with the static type below
                full_data[n1, n2, :] += partial_data[:_nn1, :_nn2:]  # type: ignore
            self.log(f'Collected on root: density matrix slice [s={s}, k={k}, n1={n1}, n2={n2}].',
                     flush=True, who='Response')

        if self.comm.rank != 0:
            return None

        return full_dm

    @classmethod
    @abstractmethod
    def from_reader(cls,
                    rho_nn_reader: KohnShamRhoWfsReader,
                    parameters: RhoParameters,
                    **kwargs) -> BaseDistributor:
        """ Set up this class from a density matrix reader and parameters object

        """
        raise NotImplementedError

    @classmethod
    def from_parameters(cls,
                        wfs_fname: str,
                        ksd: KohnShamDecomposition | str,
                        comm=world,
                        yield_re: bool = True,
                        yield_im: bool = True,
                        stridet: int = 1,
                        log: Logger | None = None,
                        verbose: bool = False,
                        **kwargs):
        """ Set up this class, trying to enforce memory limit.

        Parameters
        ----------
        wfs_fname
            File name of the time-dependent wave functions file.
        ksd
            KohnShamDecomposition object or file name to the ksd file.
        comm
            MPI communicator.
        yield_re
            Whether to read and yield the real part of wave functions/density matrices.
        yield_im
            Whether to read and yield the imaginary part of wave functions/density matrices.
        stridet
            Skip this many steps when reading the time-dependent wave functions file.
        log
            Logger object.
        verbose
            Be verbose in the attempts to satisfy memory requirement.
        kwargs
            Options passed through to :func:`from_reader`.
        """
        # Set up the time-dependent wave functions reader which is always needed
        rho_reader = KohnShamRhoWfsReader(
            wfs_fname=wfs_fname, ksd=ksd, comm=comm,
            yield_re=yield_re, yield_im=yield_im, log=log, stridet=stridet)

        log = rho_reader.log

        # Get the target memory limit
        to_MiB = 1024 ** -2
        mem_limit = env.get_response_max_mem(comm.size) / to_MiB
        log('Attempting to set up response calculation with memory limit of '
            f'{mem_limit * to_MiB:.1f} MiB across all ranks.', who='Setup', rank=0)

        totals = []
        for iterations in range(1, 100):
            # Try setting up the distributor such that `iterations` iterations are
            # needed to process all chunks
            parameters = RhoParameters.from_ksd(rho_reader.ksd, comm, chunk_iterations=iterations)
            distributor = cls.from_reader(rho_reader, parameters, **kwargs)
            total = distributor.get_memory_estimate().grand_total
            totals.append(total)
            compare = totals[:-5:-1]  # Last 4 totals in reverse order
            last_changes = [tot_new / tot_old for tot_new, tot_old in zip(compare, compare[1:])]
            if len(last_changes) == 0:
                improvement = ''
            else:
                s = ', '.join([f'{(1 - change)*100:.1f}%' for change in last_changes])
                improvement = f'Last improvements {s}'

            if verbose:
                log(f'Trying splitting in {distributor.niters:3} chunks -- estimate {total * to_MiB:.1f} MiB. '
                    f'{improvement}', who='Setup', rank=0)
            if total < mem_limit:
                log(f'Found suitable set of parameters limiting the memory to {total * to_MiB:.1f} MiB.',
                    who='Setup', rank=0)
                return distributor
            if len(last_changes) == 3 and sum(last_changes) / 3 > 0.98:
                break

        parameters = RhoParameters.from_ksd(rho_reader.ksd, comm, chunk_iterations=iterations)
        distributor = cls.from_reader(rho_reader, parameters, **kwargs)
        total = distributor.get_memory_estimate().grand_total

        log(f'Cannot satisfy memory limit. Estimate is {total * to_MiB:.1f} MiB.',
            who='Setup', rank=0)

        return distributor


class RhoIndices(NamedTuple):

    s: int
    k: int
    n1: slice
    n2: slice

    @staticmethod
    def concatenate_indices(indices_list: Iterable[RhoIndices],
                            ) -> tuple[RhoIndices, list[RhoIndices]]:
        indices_list = list(indices_list)
        assert len(indices_list) > 0
        s, k = indices_list[0][:2]
        assert all(indices.s == s for indices in indices_list), f'All s must be identical {indices_list}'
        assert all(indices.k == k for indices in indices_list), f'All k must be identical {indices_list}'

        _indices_concat, _reduced_indices_list = concatenate_indices(
            [(indices.n1, indices.n2) for indices in indices_list])
        indices_concat = RhoIndices(s, k, *_indices_concat)
        reduced_indices_list = [RhoIndices(s, k, *indices) for indices in _reduced_indices_list]

        return indices_concat, reduced_indices_list


class RhoParameters(NamedTuple):

    """ Utility class to describe density matrix indices.

    Parameters
    ----------
    ns
        Number of spins.
    nk
        Number of kpoints.
    n1min
        Smallest index of row to read.
    n1max
        Largest index of row to read.
    n2min
        Smallest index of column to read.
    n2max
        Largest index of column to read.
    striden1
        Stride for reading rows. Each chunk will be this size in the first dimension.
    striden2
        Stride for reading columns. Each chunk will be this size in the second dimension.
    """

    ns: int
    nk: int
    n1min: int
    n1max: int
    n2min: int
    n2max: int
    striden1: int = 4
    striden2: int = 4

    def __post_init__(self):
        self.striden1 = min(self.striden1, self.n1size)
        self.striden2 = min(self.striden2, self.n2size)

    @property
    def full_nnshape(self) -> tuple[int, int]:
        """ Shape of the full density matrix to be read. """
        return (self.n1size, self.n2size)

    @property
    def nnshape(self) -> tuple[int, int]:
        """ Shape of each density matrix chunk. """
        return (self.striden1, self.striden2)

    @property
    def n1size(self) -> int:
        """ Size of full density matrix in the first dimension. """
        return self.n1max + 1 - self.n1min

    @property
    def n2size(self) -> int:
        """ Size of full density matrix in the first dimension. """
        return self.n2max + 1 - self.n2min

    def iterate_indices(self) -> Generator[RhoIndices, None, None]:
        """ Iteratively yield indices slicing chunks of the density matrix. """
        for s, k, n1, n2 in product(range(self.ns), range(self.nk),
                                    range(0, self.n1size, self.striden1),
                                    range(0, self.n2size, self.striden2)):
            indices = RhoIndices(s=0, k=0,
                                 n1=slice(n1, n1 + self.striden1),
                                 n2=slice(n2, n2 + self.striden2))
            yield indices

    @classmethod
    def from_ksd(cls,
                 ksd: KohnShamDecomposition,
                 comm: Communicator | None = None,
                 only_ia: bool = True,
                 chunk_iterations: int = 1,
                 **kwargs) -> RhoParameters:
        """ Initialize from KohnShamDecomposition.

        Parameters
        ----------
        ksd
            KohnShamDecomposition.
        comm
            MPI Communicator.
        only_ia
            ``True`` if the parameters should be set up such that
            the electron-hole part of the density matrix is read,
            otherwise full density matrix.
        chunk_iterations
            Attempt to set up the strides so that the total number of
            chunks is as close as possible but not more than the number
            of MPI ranks times :attr:`chunk_iterations`.
        kwargs
            Options passed through to the constructor.
        """
        if comm is None:
            comm = world

        # Number of spins, kpoints and states
        ns, nk, nn, _ = ksd.reader.proxy('C0_unM', 0).shape

        params = dict()
        if only_ia:
            # Dimensions of electron-hole part
            imin, imax, amin, amax = [int(i) for i in ksd.ialims()]

            params['n1min'], params['n2min'] = imin, amin
            params['n1max'], params['n2max'] = imax, amax
        else:
            params['n1min'], params['n2min'] = 0, 0
            params['n1max'], params['n2max'] = nn - 1, nn - 1

        # Set up a helper object get the size
        helper = cls(ns, nk, **params)

        # We want this many chunks in total
        target_nchunks = chunk_iterations * comm.size
        ar = helper.n2size / helper.n1size  # Aspect ratio of density matrix

        nsplits1 = max(int(np.floor(np.sqrt(target_nchunks / ar))), 1)
        nsplits2 = (target_nchunks + nsplits1 - 1) // nsplits1

        # Defaults
        params['striden1'] = (helper.n1size + nsplits1 - 1) // nsplits1
        params['striden2'] = (helper.n2size + nsplits2 - 1) // nsplits2

        # Overwrite the default options in params with explicitly set options
        params.update(**kwargs)

        return cls(ns, nk, **params)
