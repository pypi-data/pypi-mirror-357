from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, Generator

import numpy as np
from numpy.typing import NDArray
from itertools import zip_longest

from ase.units import Bohr
from ase.io.ulm import Reader

from gpaw.mpi import broadcast, world
from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition
from gpaw.lcaotddft.wfwriter import WaveFunctionReader

from ..buffer import DensityMatrixBuffer
from ...utils import Logger, add_fake_kpts, get_array_filter
from ...utils.logging import format_times
from ...utils.memory import HasMemoryEstimate, MemoryEstimate
from ...typing import Array1D, Communicator


class BaseWfsReader(ABC):

    """ Read wave functions or density matrices from the time-dependent wave functions file.

    Parameters
    ----------
    wfs_fname
        File name of the time-dependent wave functions file written by GPAW.
    comm
        MPI communicator.
    yield_re
        Whether to read and yield the real part of wave functions/density matrices.
    yield_im
        Whether to read and yield the imaginary part of wave functions/density matrices.
    stridet
        Skip this many steps when reading.
    tmax
        Last time index to read.
    filter_times
        A list of times to read in atomic units. The closest times in the time-dependent
        wave functions file will be read. Applied after skipping the stridet steps to tmax.
    log
        Logger object.
    """

    def __init__(self,
                 wfs_fname: str,
                 comm=world,
                 yield_re: bool = True,
                 yield_im: bool = True,
                 stridet: int = 1,
                 tmax: int = -1,
                 filter_times: list[float] | Array1D[np.float64] | None = None,
                 log: Logger | None = None):
        self._comm = comm
        self._yield_re = yield_re
        self._yield_im = yield_im
        if log is None:
            log = Logger()
        self._log = log

        # The main reader is closed when it is garbage collected
        # Hence, we need to keep it in the scope
        self.mainreader = WaveFunctionReader(wfs_fname)
        self._time_t, self.initreader, self._full_reader_t = prepare_wave_function_readers(
            self.mainreader, comm, self.log, stridet=stridet, tmax=tmax)
        self._flt_t = get_array_filter(self._time_t, filter_times)
        self.reader_t = [self._full_reader_t[r]
                         for r in np.arange(len(self._full_reader_t), dtype=int)[self._flt_t]]

    @property
    def comm(self) -> Communicator:
        """ MPI communicator. """
        return self._comm

    @property
    def yield_re(self) -> bool:
        """ Whether this object should read real parts. """
        return self._yield_re

    @property
    def yield_im(self) -> bool:
        """ Whether this object should read imaginary parts. """
        return self._yield_im

    @property
    def log(self) -> Logger:
        """ Logger object. """
        return self._log

    @property
    def time_t(self) -> Array1D[np.float64]:
        """ Array of times to read; in atomic units. """
        return self._time_t[self._flt_t]  # type: ignore

    @property
    def nt(self) -> int:
        """ Number of times to read. """
        return len(self.time_t)

    @property
    def dt(self) -> float:
        """ Time step in atomic units. """
        time_t = self.time_t
        dt = time_t[1] - time_t[0]
        if not np.allclose(time_t[1:] - dt, time_t[:-1]):
            fname = self.mainreader.filename
            raise ValueError(f'Unable to get a time step. Variable time step in {fname}.')

        return dt

    def work_loop(self,
                  rank: int) -> Generator[int | None, None, None]:
        """ Yield the time indices that this rank will read.

        New indices are yielded until the end of self.reader_t is reached
        (across all ranks).

        Yields
        ------
        Time index between 0 and len(self.reader_t) - 1 corresponding to
        the time being read by this rank. Or None if this rank has nothing
        to read.
        """
        for t_r in self.work_loop_by_ranks():
            yield t_r[rank]

    def work_loop_by_ranks(self) -> Generator[list[int], None, None]:
        nt = self.nt
        ntperrank = (nt + self.comm.size - 1) // self.comm.size

        for localt in range(ntperrank):
            globalt_r = [rank + localt * self.comm.size for rank in range(self.comm.size)]
            globalt_r = [globalt if globalt < nt else None for globalt in globalt_r]
            yield globalt_r

    def global_work_loop(self) -> Generator[int, None, None]:
        for chunks_r in self.work_loop_by_ranks():
            for chunk in chunks_r:
                if chunk is None:
                    continue
                yield chunk

    @abstractmethod
    def iread(self, *args, **kwargs) -> Generator[DensityMatrixBuffer, None, None]:
        """ Iteratively read wave functions or density matrices time by time. """
        raise NotImplementedError

    @abstractmethod
    def nnshape(self, *args, **kwargs) -> tuple[int, int]:
        """ Shape of the density matrices or wave functions. """
        raise NotImplementedError

    def gather_on_root(self, *args, **kwargs) -> Generator[DensityMatrixBuffer | None, None, None]:
        for indices_r, dm_buffer in zip_longest(self.work_loop_by_ranks(),
                                                self.iread(*args, **kwargs), fillvalue=None):
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

    def collect_on_root(self, *args, **kwargs) -> DensityMatrixBuffer | None:
        nnshape = self.nnshape(*args, **kwargs)
        full_dm = DensityMatrixBuffer(nnshape, (self.nt, ), np.float64)
        if self.yield_re:
            full_dm.zeros(True, 0)
        if self.yield_im:
            full_dm.zeros(False, 0)

        for t, dm_buffer in zip_longest(self.global_work_loop(),
                                        self.gather_on_root(*args, **kwargs), fillvalue=None):
            if self.comm.rank != 0:
                continue

            assert t is not None, 'Iterators must be same length'
            assert dm_buffer is not None, 'Iterators must be same length'

            for partial_data_nn, full_data_nn in zip(dm_buffer._iter_buffers(),
                                                     full_dm[t]._iter_buffers()):
                full_data_nn[:] += partial_data_nn

        if self.comm.rank != 0:
            return None

        return full_dm


class KohnShamRhoWfsReader(HasMemoryEstimate, BaseWfsReader):

    """ Read density matrices from the time-dependent wave functions file.

    Yield density matrices time by time.

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
        Skip this many steps when reading.
    tmax
        Last time index to read.
    filter_times
        A list of times to read in atomic units. The closest times in the time-dependent wave functions file
        will be read.
    striden
        Option passed through to the LCAORhoWfsReader.
    log
        Logger object.
    """

    def __init__(self,
                 wfs_fname: str,
                 ksd: str | KohnShamDecomposition,
                 comm=world,
                 yield_re: bool = True,
                 yield_im: bool = True,
                 stridet: int = 1,
                 tmax: int = -1,
                 filter_times: list[float] | Array1D[np.float64] | None = None,
                 log: Logger | None = None,
                 striden: int = 0):
        # Set up an internal LCAO density matrix reader
        self.lcao_rho_reader = LCAORhoWfsReader(
            wfs_fname=wfs_fname, comm=comm,
            yield_re=yield_re, yield_im=yield_im, log=log,
            stridet=stridet, tmax=tmax,
            filter_times=filter_times, striden=striden)

        # And copy its attributes to self
        self._yield_re = yield_re
        self._yield_im = yield_im
        self._comm = self.lcao_rho_reader.comm
        self._log = self.lcao_rho_reader.log
        self.mainreader = self.lcao_rho_reader.mainreader
        self.initreader = self.lcao_rho_reader.initreader
        self._full_reader_t = self.lcao_rho_reader._full_reader_t
        self.reader_t = self.lcao_rho_reader.reader_t
        self._flt_t = self.lcao_rho_reader._flt_t
        self._time_t = self.lcao_rho_reader._time_t

        # Set up ksd
        if isinstance(ksd, KohnShamDecomposition):
            self._ksd = ksd
        else:
            self._ksd = KohnShamDecomposition(filename=ksd)
            add_fake_kpts(self._ksd)

        self._C0S_sknM: NDArray[np.float64] | None = None
        self._rho0_sknn: NDArray[np.float64] | None = None

    def __str__(self) -> str:
        nn, nM = proxy_coefficients(self.initreader).shape[2:]
        ntperrank = (self.nt + self.comm.size - 1) // self.comm.size

        lines = []
        lines.append('Time-dependent wave functions reader')
        lines.append('  Constructing density matrices in basis of ground state orbitals.')
        lines.append('')
        lines.append(f'  file: {self.mainreader.filename}')
        lines.append(f'    wave function dimensions {(nn, nM)}')
        lines.append(f'    {self.nt} times')
        lines.append(f'      {format_times(self.time_t, units="au")}')
        lines.append(f'  {self.comm.size} ranks reading in {ntperrank} iterations')

        return '\n'.join(lines)

    def get_memory_estimate(self) -> MemoryEstimate:
        nn, nM = proxy_coefficients(self.initreader).shape[2:]

        memory_estimate = MemoryEstimate()
        memory_estimate.add_key('C0S_nM', (nn, nM), float,
                                on_num_ranks=self.comm.size)
        memory_estimate.add_key('rho0_MM', (nM, nM), float,
                                on_num_ranks=self.comm.size)

        return memory_estimate

    @property
    def ksd(self) -> KohnShamDecomposition:
        """ Kohn-Sham decomposition object. """
        return self._ksd

    @property
    def C0S_sknM(self) -> NDArray[np.float64]:
        if self._C0S_sknM is None:
            self.log(f'Constructing C0_sknM on {self.comm.size} ranks',
                     who='Reader', rank=0, flush=True)
            self._C0S_sknM = read_C0S_parallel(self.ksd.reader, comm=self.comm)
            self.log('Constructed C0_sknM',
                     who='Reader', rank=0, flush=True)
            assert self._C0S_sknM is not None
        return self._C0S_sknM

    @property
    def rho0_sknn(self) -> NDArray[np.float64]:
        if self._rho0_sknn is None:
            f_skn = self.ksd.reader.occ_un[:]
            nn = f_skn.shape[2]
            rho0_sknn = np.zeros(f_skn.shape[:2] + (nn, nn))
            diag_nn = np.eye(nn, dtype=bool)
            rho0_sknn[..., diag_nn] = f_skn
            self._rho0_sknn = rho0_sknn
        return self._rho0_sknn

    def nnshape(self,
                s: int,
                k: int,
                n1: slice,
                n2: slice) -> tuple[int, int]:
        n1size = n1.stop - n1.start
        n2size = n2.stop - n2.start
        nnshape = (n1size, n2size)
        return nnshape

    def parallel_prepare(self):
        """ Read everything necessary synchronously on all ranks. """
        self.C0S_sknM
        self.lcao_rho_reader.rho0_skMM

    def iread(self,
              s: int,
              k: int,
              n1: slice,
              n2: slice) -> Generator[DensityMatrixBuffer, None, None]:
        """ Read the density matrices time by time.

        Parameters
        ----------
        s, k, n1, n2
            Read these indices.
        """
        dm_buffer = DensityMatrixBuffer(self.nnshape(s, k, n1, n2), (), np.float64)
        if self.yield_re:
            dm_buffer.zeros(True, 0)
        if self.yield_im:
            dm_buffer.zeros(False, 0)

        einsumstr = 'nN,mM,NM->nm'
        self.C0S_sknM  # Read this on all ranks

        nM = self.C0S_sknM.shape[3]
        sliceM = slice(0, nM)

        for lcao_dm in self.lcao_rho_reader.iread(s, k, sliceM, sliceM):
            C0S_nM1 = self.C0S_sknM[s, k, n1, :]  # Here n is full KS basis
            C0S_nM2 = self.C0S_sknM[s, k, n2, :]

            self.log.start('read')

            # Conjugate C_nM2
            if self.yield_re:
                Rerho_MM = lcao_dm.real
                Rerho_x = np.einsum(einsumstr, C0S_nM1, C0S_nM2, Rerho_MM, optimize=True)
                dm_buffer.safe_fill(True, 0, Rerho_x)
            if self.yield_im:
                Imrho_MM = lcao_dm.imag
                Imrho_x = np.einsum(einsumstr, C0S_nM1, C0S_nM2, Imrho_MM, optimize=True)
                dm_buffer.safe_fill(False, 0, Imrho_x)

            yield dm_buffer


class LCAORhoWfsReader(BaseWfsReader):

    """ Read density matrices in the LCAO basis from the time-dependent wave functions file.

    Yield density matrices time by time.
    """

    def __init__(self,
                 wfs_fname: str,
                 comm=world,
                 yield_re: bool = True,
                 yield_im: bool = True,
                 stridet: int = 1,
                 tmax: int = -1,
                 filter_times: list[float] | Array1D[np.float64] | None = None,
                 log: Logger | None = None,
                 striden: int = 4):

        super().__init__(wfs_fname=wfs_fname, comm=comm,
                         yield_re=yield_re, yield_im=yield_im, log=log,
                         stridet=stridet, tmax=tmax,
                         filter_times=filter_times)
        self._f_skn: NDArray[np.float64] | None = None
        self._C0_sknM: NDArray[np.float64] | None = None
        self._rho0_skMM: NDArray[np.float64] | None = None
        self._striden = striden

    @property
    def nn(self) -> int:
        return self.f_skn.shape[2]

    @property
    def striden(self) -> int:
        return self._striden

    @property
    def true_striden(self) -> int:
        if self.striden == 0:
            return self.nn
        return self.striden

    @property
    def f_skn(self) -> NDArray[np.float64]:
        """ Occupations numbers. """
        if self._f_skn is None:
            self._f_skn = proxy_occupations(self.initreader)[:]
        return self._f_skn

    @property
    def C0_sknM(self) -> NDArray[np.float64]:
        if self._C0_sknM is None:
            C0_sknM = proxy_coefficients(self.initreader)[:]
            assert np.max(np.abs(C0_sknM.imag)) < 1e-20
            self._C0_sknM = C0_sknM.real
        return self._C0_sknM

    @property
    def rho0_skMM(self) -> NDArray[np.float64]:
        if self._rho0_skMM is None:
            self.log(f'Constructing rho0_skMM on {self.comm.size} ranks',
                     who='Reader', rank=0, flush=True)
            self._rho0_skMM = calculate_rho0_parallel(self.f_skn, self.C0_sknM, comm=self.comm)
            self.log('Constructed rho0_skMM',
                     who='Reader', rank=0, flush=True)
            assert self._rho0_skMM is not None
        return self._rho0_skMM

    def inner_work_loop(self) -> Generator[slice, None, None]:
        for n in range(0, self.nn, self.true_striden):
            yield slice(n, n + self.true_striden)

    def subtract_ground_state(self,
                              dm_buffer: DensityMatrixBuffer,
                              s: int,
                              k: int,
                              M1: slice,
                              M2: slice):
        rhs = -self.rho0_skMM[s, k, M1, M2]
        dm_buffer.safe_add(True, 0, rhs)

    def nnshape(self,
                s: int,
                k: int,
                M1: slice,
                M2: slice) -> tuple[int, int]:
        M1size = M1.stop - M1.start
        M2size = M2.stop - M2.start
        MMshape = (M1size, M2size)
        return MMshape

    def iread(self,
              s: int,
              k: int,
              M1: slice,
              M2: slice) -> Generator[DensityMatrixBuffer, None, None]:
        """ Read the density matrices time by time.

        Parameters
        ----------
        s, k, M1, M2
            Read these indices.
        """
        dm_buffer = DensityMatrixBuffer(self.nnshape(s, k, M1, M2), (), np.float64)

        einsumstr = 'n,nM,nO->MO'

        self.rho0_skMM  # Construct synchronously on all ranks
        for globalt in self.work_loop(self.comm.rank):
            if globalt is None:
                continue

            if self.yield_re:
                dm_buffer.zeros(True, 0)
            if self.yield_im:
                dm_buffer.zeros(False, 0)

            reader = self.reader_t[globalt]
            for n in self.inner_work_loop():
                C_nM1 = proxy_C_nM(reader, s, k, n, M1)  # Here n is occupied states only
                C_nM2 = proxy_C_nM(reader, s, k, n, M2)
                f_n = proxy_occupations(reader, s, k)[n]
                path = np.einsum_path(einsumstr, f_n, C_nM1.real, C_nM2.real, optimize='optimal')[0]

                # Conjugate C_nM2
                if self.yield_re:
                    Rerho_x = np.einsum(einsumstr, f_n, C_nM1.real, C_nM2.real, optimize=path)
                    Rerho_x += np.einsum(einsumstr, f_n, C_nM1.imag, C_nM2.imag, optimize=path)
                    dm_buffer.safe_add(True, 0, Rerho_x)
                if self.yield_im:
                    Imrho_x = np.einsum(einsumstr, f_n, C_nM1.imag, C_nM2.real, optimize=path)
                    Imrho_x -= np.einsum(einsumstr, f_n, C_nM1.real, C_nM2.imag, optimize=path)
                    dm_buffer.safe_add(False, 0, Imrho_x)

            self.subtract_ground_state(dm_buffer, s, k, M1, M2)

            yield dm_buffer


class WfsReader(BaseWfsReader):

    """ Read wave function LCAO coefficients from the time-dependent wave functions file.

    Yield wave functions time by time.
    """

    def __init__(self,
                 wfs_fname: str,
                 comm=world,
                 yield_re: bool = True,
                 yield_im: bool = True,
                 stridet: int = 1,
                 tmax: int = -1,
                 filter_times: list[float] | Array1D[np.float64] | None = None,
                 log: Logger | None = None):
        super().__init__(wfs_fname=wfs_fname, comm=comm,
                         yield_re=yield_re, yield_im=yield_im, log=log,
                         stridet=stridet, tmax=tmax,
                         filter_times=filter_times)
        self._f_skn: NDArray[np.float64] | None = None
        self._C0_sknM: NDArray[np.float64] | None = None

    @property
    def nn(self) -> int:
        return self.C0_sknM.shape[2]

    @property
    def nM(self) -> int:
        return self.C0_sknM.shape[3]

    @property
    def f_skn(self) -> NDArray[np.float64]:
        """ Occupations """
        if self._f_skn is None:
            self._f_skn = proxy_occupations(self.initreader)[:]
        return self._f_skn

    @property
    def C0_sknM(self) -> NDArray[np.float64]:
        if self._C0_sknM is None:
            C0_sknM = proxy_coefficients(self.initreader)[:]
            assert np.max(np.abs(C0_sknM.imag)) < 1e-20
            self._C0_sknM = C0_sknM.real
        return self._C0_sknM

    def nnshape(self,
                s: int,
                k: int,
                n: slice,
                M: slice) -> tuple[int, int]:
        nsize = n.stop - n.start
        Msize = M.stop - M.start
        nMshape = (nsize, Msize)
        return nMshape

    def iread(self,
              s: int,
              k: int,
              n: slice,
              M: slice) -> Generator[DensityMatrixBuffer, None, None]:
        """ Read the density matrices time by time.

        Parameters
        ----------
        s, k, n, M
            Read these indices.
        """
        dm_buffer = DensityMatrixBuffer(self.nnshape(s, k, n, M), (), np.float64)

        for globalt in self.work_loop(self.comm.rank):
            if globalt is None:
                continue

            if self.yield_re:
                dm_buffer.zeros(True, 0)
            if self.yield_im:
                dm_buffer.zeros(False, 0)

            reader = self.reader_t[globalt]
            C_nM = proxy_C_nM(reader, s, k, n, M)
            if self.yield_re:
                dm_buffer.safe_fill(True, 0, C_nM.real)
            if self.yield_im:
                dm_buffer.safe_fill(False, 0, C_nM.imag)

            yield dm_buffer


def prepare_wave_function_readers(mainreader,
                                  comm,
                                  log: Callable = print,
                                  stridet: int = 1,
                                  tmax: int = -1,
                                  parallel: bool = True,
                                  ) -> tuple[Array1D[np.float64], WaveFunctionReader, list[WaveFunctionReader]]:
    readerlen = len(mainreader)
    log(f'Opening time-dependent wave functions file {mainreader.filename}', who='Reader', rank=0, flush=True)

    # Encode the action as int according to the following list
    int2action = [None, 'init', 'kick', 'propagate']
    action2int = {a: i for i, a in enumerate(int2action)}

    if parallel:
        # Read in parallel
        readrange = range(0, readerlen, comm.size)
    else:
        # Read everything on root
        readrange = range(readerlen) if comm.rank == 0 else range(0)

    if comm.rank == 0 or parallel:
        # Buffers to read to on all ranks when parallel
        time_1 = np.array([0], dtype=float)
        action_1 = np.array([0], dtype=int)

    def round_up(val):
        v = (val + comm.size - 1)
        v = v // comm.size
        return v * comm.size

    if comm.rank == 0:
        # Buffers for gathering
        time_t = np.zeros(round_up(readerlen), dtype=time_1.dtype)
        action_t = np.zeros(round_up(readerlen), dtype=action_1.dtype)

    # Read all times in parallel, gather on root
    for roott in readrange:
        t = roott + comm.rank
        if t < readerlen:
            log(f'Opened item #{t}', who='Reader', comm=comm, if_elapsed=5, flush=True)

            reader = mainreader[t]
            action = getattr(reader, 'action', None)
            action_1[:] = action2int[action]
            try:
                time_1[:] = getattr(reader, 'time')
            except AttributeError:
                # Depending on the action these might not be set
                time_1[:] = np.nan

        if parallel:
            comm.gather(time_1, 0, time_t[roott:roott + comm.size] if comm.rank == 0 else None)
            comm.gather(action_1, 0, action_t[roott:roott + comm.size] if comm.rank == 0 else None)
        else:
            time_t[t] = time_1[0]
            action_t[t] = action_1[0]

    if comm.rank == 0:
        # The root rank must count the number of time entries
        nreadt = 0
        lasttime = -np.inf

        readtimes = []
        timereadert = []
        initreadert = None
        for t in range(readerlen):
            action = int2action[action_t[t]]
            curtime = time_t[t]

            if curtime <= lasttime:
                log(f'Negative time difference at #{t} '
                    f'({curtime:.1f} <= {lasttime:.1f}). Skipping',
                    who='Reader', comm=comm, flush=True)
                continue

            if action is None:
                # This is just some dummy entry
                continue

            # Find the first 'init' entry
            if action == 'init':
                assert curtime >= lasttime, f'Times not matching {t}:{curtime} !>= {lasttime}'
                if initreadert is None:
                    initreadert = t
                continue

            assert action in ['kick', 'propagate']
            assert curtime != np.nan
            if nreadt % stridet == 0:
                # Save multiples of stridet
                # Note that 0 will always be saved. That contains the kick
                readtimes.append(curtime)
                timereadert.append(t)
            nreadt += 1
            if tmax > 0 and nreadt >= tmax:
                break
            lasttime = curtime

        assert initreadert is not None
        broadcast_obj = (initreadert, timereadert, np.array(readtimes))
    else:
        broadcast_obj = None

    # Distribute
    (initreadert, timereadert, time_t) = broadcast(broadcast_obj, comm=comm, root=0)
    initreader = mainreader[initreadert]
    timereader_t = [mainreader[t] for t in timereadert]

    log(f'Opened time-dependent wave functions file with {len(timereader_t)} times',
        who='Reader', rank=0, flush=True)

    return time_t, initreader, timereader_t


def read_C0S_parallel(ksdreader: Reader,
                      comm=None) -> NDArray[np.float64]:
    if comm is None:
        comm = world

    # Compute C0S in parallel
    C0_sknM = ksdreader.proxy('C0_unM', 0)
    S_skMM = ksdreader.proxy('S_uMM', 0)
    nM = C0_sknM.shape[3]

    # Rank local contributions
    strideM = (nM + comm.size - 1) // comm.size
    sliceM = slice(strideM * comm.rank, strideM * (comm.rank + 1))
    C0_sknM = C0_sknM[:][..., sliceM]
    S_skMM = S_skMM[:][..., sliceM, :]

    # Compute C0S
    C0S_sknM = np.einsum('sknO,skOM->sknM', C0_sknM, S_skMM, optimize=True)

    # Sum and distribute
    comm.sum(C0S_sknM)

    return C0S_sknM


def calculate_rho0_parallel(f_skn: NDArray[np.float64],
                            C0_sknM: NDArray[np.float64],
                            comm=None) -> NDArray[np.float64]:
    if comm is None:
        comm = world

    nn = f_skn.shape[2]
    striden = (nn + comm.size - 1) // comm.size
    slicen = slice(striden * comm.rank, striden * (comm.rank + 1))
    f_skn = f_skn[:][..., slicen]
    C0_sknM = C0_sknM[:][..., slicen, :]

    # Compute density matrix
    rho0_skMM = np.einsum('skn,sknM,sknO->skMO',
                          f_skn, C0_sknM, C0_sknM,
                          optimize=True)

    # Sum and distribute
    comm.sum(rho0_skMM)

    return rho0_skMM


def proxy_coefficients(reader, *indices):
    """ Proxy the wave function coefficients, with the correct units."""
    coefficients = reader.wave_functions.proxy('coefficients', *indices)
    coefficients.scale = Bohr ** 1.5

    return coefficients


def proxy_occupations(reader, *indices):
    """ Proxy the wave function occupations with the correct scale."""
    occupations = reader.wave_functions.proxy('occupations', *indices)
    occupations.scale = 2 / reader.wave_functions.occupations.shape[0]

    return occupations


def proxy_C_nM(reader,
               *indices):
    """ Proxy the wave function coefficients, with the correct units.

    Make sure that the proxied array has at least two dimensions"""
    x = indices[:-2]
    n = indices[-2]
    M = indices[-1]

    C_nM = proxy_coefficients(reader, *x)
    if isinstance(n, slice):
        C_x = C_nM[n][:, M]
    else:
        C_M = C_nM.proxy(n)
        C_x = np.atleast_2d(C_M[M])
    assert len(C_x.shape) == 2
    return C_x
