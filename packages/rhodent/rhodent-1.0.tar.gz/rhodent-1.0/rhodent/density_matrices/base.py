from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Generator, NamedTuple, TypeVar

from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition

from .density_matrix import DensityMatrix
from ..utils import Logger, add_fake_kpts, two_communicators
from ..utils.memory import HasMemoryEstimate, MemoryEstimate
from ..typing import Communicator


class WorkMetadata(NamedTuple):
    """ Metadata to the density matrices """
    density_matrices: BaseDensityMatrices

    @property
    def global_indices(self) -> tuple[int, ...]:
        """ Unique index for this work. """
        raise NotImplementedError

    @property
    @abstractmethod
    def desc(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return f'{self.__class__.__name__}{self.global_indices}'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{self.global_indices}'


WorkMetadataT = TypeVar('WorkMetadataT', bound=WorkMetadata)


class BaseDensityMatrices(HasMemoryEstimate, ABC, Generic[WorkMetadataT]):

    _log: Logger
    _ksd: KohnShamDecomposition

    """
    Collection of density matrices in the Kohn-Sham basis for different times
    or frequencies, possibly after convolution with various pulses.

    Plain density matrices and/or derivatives thereof may be represented.

    Parameters
    ----------
    ksd
        KohnShamDecomposition object or file name.
    real
        Calculate the real part of density matrices.
    imag
        Calculate the imaginary part of density matrices.
    calc_size
        Size of the calculation communicator.
    """

    def __init__(self,
                 ksd: KohnShamDecomposition | str,
                 real: bool = True,
                 imag: bool = True,
                 calc_size: int = 1,
                 log: Logger | None = None):
        assert real or imag
        self._reim_r: list[str] = []
        if real:
            self._reim_r.append('Re')
        if imag:
            self._reim_r.append('Im')

        if log is None:
            self._log = Logger()
        else:
            self._log = log

        self._loop_comm, self._calc_comm = two_communicators(-1, calc_size)
        if isinstance(ksd, KohnShamDecomposition):
            self._ksd = ksd
        else:
            self._ksd = KohnShamDecomposition(filename=ksd)
        add_fake_kpts(self._ksd)

        # Do a quick sanity check at runtime
        self._runtime_verify_work_loop()

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError

    def get_memory_estimate(self) -> MemoryEstimate:
        memory_estimate = MemoryEstimate(comment='Unknown')

        return memory_estimate

    def parallel_prepare(self):
        """ Read everything necessary synchronously on all ranks. """

    @abstractmethod
    def __iter__(self) -> Generator[tuple[WorkMetadataT, DensityMatrix], None, None]:
        """ Obtain density matrices for various times, pulses or frequencies.

        Yields
        ------
        Tuple (work, dm) on the root rank of the calculation communicator:

            work
                An object representing the metadata (time, frequency or pulse) for the work done.
            dm
                Density matrix for this time, frequency or pulse.
        """
        raise NotImplementedError

    def iread_gather_on_root(self) -> Generator[tuple[WorkMetadataT, DensityMatrix], None, None]:
        """ Obtain density matrices for various times, pulses or frequencies and gather to the root rank.

        Yields
        ------
        Tuple (work, dm) on the root rank of the loop and calculation communicators:

            work
                An object representing the metadata (time, frequency or pulse) for the work done.
            dm
                Density matrix for this time, frequency or pulse.
        """
        work: WorkMetadataT | None
        gen = iter(self)

        # Loop over the work to be done, and the ranks that are supposed to do it
        self.parallel_prepare()
        for rank, work in self.global_work_loop_with_idle():
            if work is None:
                # Rank rank will not do any work at this point
                continue

            if rank == self.loop_comm.rank:
                mywork, mydm = next(gen)
                if self.calc_comm.rank == 0:
                    self.log(f'Read {mywork.desc} in {self.log.elapsed("read"):.1f}s',
                             who='Response', if_elapsed=5)
                assert work.global_indices == mywork.global_indices, f'{work.desc} != {mywork.desc}'

            dm = DensityMatrix.broadcast(
                mydm if self.loop_comm.rank == rank else None,
                ksd=self.ksd,
                root=rank, dm_comm=self.calc_comm, comm=self.loop_comm)

            yield work, dm

        _exhausted = object()
        rem = next(gen, _exhausted)
        assert rem is _exhausted, rem

    @property
    def ksd(self) -> KohnShamDecomposition:
        """ Kohn-Sham decomposition object. """
        return self._ksd

    @property
    def log(self) -> Logger:
        """ Logger. """
        return self._log

    def log_parallel(self, *args, **kwargs) -> Logger:
        """ Log message with communicator information. """
        return self._log(*args, **kwargs, comm=self.loop_comm, who='Response')

    @property
    def reim(self) -> list[str]:
        """ List of strings ``'Re'`` and ``'Im'``, depending on whether real, and/or imaginary parts are computed. """
        return self._reim_r

    @abstractmethod
    def work_loop(self,
                  rank: int) -> Generator[WorkMetadataT | None, None, None]:
        """ The work to be done by a certain rank of the loop communicator.

        Parameters
        ----------
        rank
            Rank of the loop communicator.

        Yields
        ------
        Objects representing the time, frequency or pulse to be computed by rank ``rank``.
        None is yielded when `rank` does not do any work while other ranks are doing work.
        """
        raise NotImplementedError

    def _runtime_verify_work_loop(self):
        """ Verify that the description of work to be done is consistent across ranks. """
        local_work_r = [list(self.work_loop(rank)) for rank in range(self.loop_comm.size)]
        work_lengths = [len(local_work) for local_work in local_work_r]
        assert all([work_lengths[0] == work_length for work_length in work_lengths]), \
            f'The work loop has different length across the different ranks. {work_lengths}'
        concat_work_list = [work.global_indices for local_work in local_work_r for work in local_work
                            if work is not None]
        assert len(concat_work_list) == len(set(concat_work_list)), \
            f'Different ranks do duplicate work {concat_work_list}'

    @property
    def local_work_plan(self) -> tuple[WorkMetadataT, ...]:
        """ The work to be done by a this rank of the loop communicator.

        Yields
        ------
        Objects representing the time, frequency or pulse to be computed by this rank.
        """
        local_work_plan = tuple(work for work in self.work_loop(self.loop_comm.rank)
                                if work is not None)
        return local_work_plan

    @property
    def local_work_plan_with_idle(self) -> tuple[WorkMetadataT | None, ...]:
        """ The work to be done by a this rank of the loop communicator.

        This function includes None values for when this rank does not do any work
        in order to synchronize the execution.

        Yields
        ------
        Objects representing the time, frequency or pulse to be computed by this rank.
        None is yielded when this rank does not do any work while other ranks are doing work.
        """
        local_work_plan = tuple(self.work_loop(self.loop_comm.rank))

        return local_work_plan

    def global_work_loop_with_idle(self) -> Generator[tuple[int, WorkMetadataT | None], None, None]:
        """ The work to be done by a all ranks of the loop communicator.

        This function includes None values for when ranks do not do any work
        in order to synchronize the execution.

        Yields
        ------
        Lists of length equal to the loop communicator size. Each element in the list represents
        the work to be done. See `local_work_plan_with_idle`.
        """
        work_loop_r = [self.work_loop(rank) for rank in range(self.loop_comm.size)]
        while True:
            for rank in range(self.loop_comm.size):
                try:
                    work = next(work_loop_r[rank])
                    yield rank, work
                except StopIteration:
                    if rank == 0:
                        # No more work to do
                        return
                    else:
                        raise RuntimeError(f'Ranks have different amount of work. Exited on {rank}')

    def global_work_loop(self) -> Generator[tuple[int, WorkMetadataT | None], None, None]:
        """ The work to be done by a all ranks of the loop communicator.

        Yields
        ------
        Lists of length equal to the loop communicator size. Each element in the list represents
        the work to be done. See :func:`local_work_plan`.
        """
        for rank, work in self.global_work_loop_with_idle():
            if work is None:
                continue
            yield rank, work

    @property
    def localn(self) -> int:
        """ Total number of density matrices this rank will work with. """
        return len(self.local_work_plan)

    @property
    def globaln(self) -> int:
        """ Total number of density matrices to work with across all ranks. """
        local_work_r = [list(self.work_loop(rank)) for rank in range(self.loop_comm.size)]
        concat_work_list = [work for local_work in local_work_r for work in local_work
                            if work is not None]
        return len(concat_work_list)

    @property
    def calc_comm(self) -> Communicator:
        """ Calculation communicator.

        Each rank of this communicator calculates the observables corresponding to
        a part (in electron-hole space) of the density matrices. """
        return self._calc_comm

    @calc_comm.setter
    def calc_comm(self, value: Communicator):
        from gpaw.mpi import world
        if value is None:
            self.calc_comm = world
            return

        assert hasattr(value, 'rank')
        assert hasattr(value, 'size')
        self._calc_comm = value

    @property
    def loop_comm(self) -> Communicator:
        """ Loop communicator.

        Each rank of this communicator calculates the density matrices corresponding to
        different times, frequencies or after convolution with a different pulse. """
        return self._loop_comm

    @loop_comm.setter
    def loop_comm(self, value: Communicator):
        from gpaw.mpi import world
        if value is None:
            self.loop_comm = world
            return

        assert hasattr(value, 'rank')
        assert hasattr(value, 'size')
        self._loop_comm = value
        raise NotImplementedError

    @abstractmethod
    def write_to_disk(self,
                      fmt: str):
        """ Calculate the density matrices amd save to disk.

        Parameters
        ----------
        fmt
            Formatting string.
        """
        raise NotImplementedError
