from __future__ import annotations

from typing import Generator, Generic, Sequence
import numpy as np
from numpy.typing import NDArray
from numpy._typing import _DTypeLike as DTypeLike  # parametrizable wrt generic

from ..utils import DTypeT, Logger, env
from ..typing import ArrayIndex


class DensityMatrixBuffer(Generic[DTypeT]):

    """ Buffer for the density matrix.

    Objects of this class can hold buffers for real and imaginary parts
    and various derivatives at the same time.

    Each buffer has two dimensions corresponding to (part of) the
    density matrix, and optionally additional dimensions for e.g. time.

    Parameters
    ----------
    nnshape
        Shape of the dimension corresponding to the density matrix. Must
        have dimension 2.
    xshape
        Shape of the additional dimension corresponding to, e.g., time.
    dtype
        Data type of the density matrices.
    re_buffers
        Buffers for the different derivatives of the real part of the
        density matrix as dictionaries, where the keys is the derivative
        order (0, 1, 2, etc.) and the value is a numpy array of shape
        ``(nnshape, xshape)``.
    im_buffers
        Same as :attr:`re_buffers` but for imaginary part.
    """

    def __init__(self,
                 nnshape: tuple[int, int],
                 xshape: tuple[int, ...],
                 dtype: DTypeLike[DTypeT],
                 re_buffers: dict[int, NDArray[DTypeT]] = dict(),
                 im_buffers: dict[int, NDArray[DTypeT]] = dict()):
        assert len(nnshape) == 2
        assert all(isinstance(dim, (int, np.integer)) and dim >= 0 for dim in nnshape)
        assert all(isinstance(dim, (int, np.integer)) and dim >= 0 for dim in xshape)
        assert isinstance(np.dtype(dtype), np.dtype)
        self._nnshape = nnshape
        self._xshape = xshape
        self._dtype = np.dtype(dtype)
        self._re_buffers: dict[int, NDArray[DTypeT]] = dict()
        self._im_buffers: dict[int, NDArray[DTypeT]] = dict()

        for derivative, buffer_nnx in re_buffers.items():
            self.store(True, derivative, buffer_nnx)

        for derivative, buffer_nnx in im_buffers.items():
            self.store(False, derivative, buffer_nnx)

    @property
    def real(self) -> NDArray[DTypeT]:
        """ Buffer of shape nnshape + xshape corresponding to real data. """
        return self._get_real(0)

    @property
    def real1(self) -> NDArray[DTypeT]:
        """ Buffer of shape nnshape + xshape corresponding to real part of first derivative. """
        return self._get_real(1)

    @property
    def real2(self) -> NDArray[DTypeT]:
        """ Buffer of shape nnshape + xshape corresponding to real part of second derivative. """
        return self._get_real(2)

    @property
    def imag(self) -> NDArray[DTypeT]:
        """ Buffer of shape nnshape + xshape corresponding to imaginary data. """
        return self._get_imag(0)

    @property
    def imag1(self) -> NDArray[DTypeT]:
        """ Buffer of shape nnshape + xshape corresponding to imaginary part of first derivative. """
        return self._get_imag(1)

    @property
    def imag2(self) -> NDArray[DTypeT]:
        """ Buffer of shape nnshape + xshape corresponding to imaginary part of second derivative. """
        return self._get_imag(2)

    def _get_real(self,
                  derivative: int) -> NDArray[DTypeT]:
        """ Fetch density matrix buffer for real data.

        Parameters
        ----------
        derivative
            Derivative order.
        """
        return self._re_buffers[derivative]

    def _get_imag(self,
                  derivative: int) -> NDArray[DTypeT]:
        """ Fetch density matrix buffer for imaginary data.

        Parameters
        ----------
        derivative
            Derivative order.
        """
        return self._im_buffers[derivative]

    def _get_data(self,
                  real: bool,
                  derivative: int) -> NDArray[DTypeT]:
        """ Fetch density matrix buffer.

        Parameters
        ----------
        real
            ``True`` if real, ``False`` if imaginary.
        derivative
            Derivative order.
        """
        return self._get_real(derivative) if real else self._get_imag(derivative)

    def copy(self) -> DensityMatrixBuffer:
        """ Return a deep copy of this object (buffers are copied). """
        re_buffers = {derivative: np.array(buffer_nnx)
                      for derivative, buffer_nnx in self._re_buffers.items()}
        im_buffers = {derivative: np.array(buffer_nnx)
                      for derivative, buffer_nnx in self._im_buffers.items()}

        dm_buffer = DensityMatrixBuffer(self.nnshape, self.xshape,
                                        dtype=self.dtype,
                                        re_buffers=re_buffers,
                                        im_buffers=im_buffers)
        return dm_buffer

    def new(self) -> DensityMatrixBuffer:
        """ Return a new buffer with the same shape. """
        dm_buffer = DensityMatrixBuffer(self.nnshape, self.xshape,
                                        dtype=self.dtype)
        return dm_buffer

    def __getitem__(self,
                    value) -> DensityMatrixBuffer:
        """ Index the buffers and return a new DensityMatrixBuffer
        with buffers that are views of the buffers of this DensityMatrixBuffer.
        """
        if len(self._im_buffers) == 0 and len(self._re_buffers) == 0:
            # This case needs some special handing to get the dimension of
            # the output
            raise NotImplementedError

        # Wrap in a tuple
        if not isinstance(value, tuple):
            value = (value, )
        s = (slice(None), slice(None)) + value
        re_buffers = {derivative: buffer_nnx[s]
                      for derivative, buffer_nnx in self._re_buffers.items()}
        im_buffers = {derivative: buffer_nnx[s]
                      for derivative, buffer_nnx in self._im_buffers.items()}

        # Ugly hack. Get any of the buffers
        xshape = (list(re_buffers.values()) + list(im_buffers.values()))[0].shape[2:]
        return DensityMatrixBuffer(self.nnshape, xshape, dtype=self.dtype,
                                   re_buffers=re_buffers, im_buffers=im_buffers)

    @property
    def narrays(self) -> int:
        """ Number of arrays stored in this object. """
        return len(self.derivatives_imag) + len(self.derivatives_real)

    @property
    def nnshape(self) -> tuple[int, int]:
        """ Shape of the part of the density matrix. """
        return self._nnshape

    @property
    def xshape(self) -> tuple[int, ...]:
        """ Shape of the additional dimension of the buffers. """
        return self._xshape

    @property
    def shape(self) -> tuple[int, ...]:
        """ Shape of the buffers. """
        return self.nnshape + self.xshape

    @property
    def dtype(self) -> np.dtype[DTypeT]:
        """ Dtype of the buffers. """
        return self._dtype

    def store(self,
              real: bool,
              derivative: int,
              buffer_nnx: NDArray[DTypeT]):
        """ Store buffer for part of density matrix.

        Parameters
        ----------
        real
            ``True`` if real, ``False`` if imaginary.
        derivative
            Derivative order.
        buffer_nnx
            Buffer of shape ``(nnshape, xshape)``.
        """
        assert isinstance(derivative, int) and derivative >= 0, derivative
        assert isinstance(buffer_nnx, np.ndarray)
        assert buffer_nnx.shape == self.shape, f'{buffer_nnx.shape} != {self.shape}'
        assert buffer_nnx.dtype == self.dtype
        if real:
            self._re_buffers[derivative] = buffer_nnx
        else:
            self._im_buffers[derivative] = buffer_nnx

    def zero_buffers(self,
                     real: bool,
                     imag: bool,
                     derivative_order_s: list[int]):
        """ Initialize many buffers at once to and write zeros.

        Parameters
        ----------
        real
            Initialize buffers for real parts.
        imag
            Initialize buffers for imaginary parts.
        derivative_order_s
            Initialize buffers for these derivative orders.
        """
        for derivative in derivative_order_s:
            if real:
                self.zeros(True, derivative)
            if imag:
                self.zeros(False, derivative)

    def zeros(self,
              real: bool,
              derivative: int):
        """ Initialize buffer with zeros for part of density matrix.

        Parameters
        ----------
        real
            ``True`` if real, ``False`` if imaginary.
        derivative
            Derivative order.
        """
        self.store(real, derivative, np.zeros(self.shape, dtype=self.dtype))

    def broadcast_x(self,
                    data_nnx: NDArray[DTypeT]) -> NDArray[DTypeT]:
        """ Broadcast the x dimensions of data_nnx. """
        nnshape = data_nnx.shape[:2]
        data_xnn = np.moveaxis(np.moveaxis(data_nnx, 0, -1), 0, -1)
        data_xnn = np.broadcast_to(data_xnn, self.xshape + nnshape)
        data_nnx = np.moveaxis(np.moveaxis(data_xnn, -1, 0), -1, 0)
        return data_nnx

    @property
    def nnellipsis(self) -> tuple[slice, slice]:
        return (slice(None), slice(None))

    @property
    def xellipsis(self) -> tuple[slice, ...]:
        return tuple(len(self.xshape) * [slice(None)])

    def safe_fill(self,
                  real: bool,
                  derivative: int,
                  data_nnx: NDArray[DTypeT]):
        """ Write data_nnx to the corrsponding buffer, if the dimensions of data_nnx
        are equal to or smaller than the buffer.

        If the dimensions of data_nnx are smaller than or equal to the dimensions
        of the buffer, write to the first elements of the buffer.
        Otherwise raise and error.

        Parameters
        ----------
        real
            ``True`` if real, ``False`` if imaginary.
        derivative
            Derivative order.
        buffer_nnx
            Data of shape ``(nnshape, xshape)``.
        """
        assert len(data_nnx.shape) <= len(self.shape), f'{data_nnx.shape} > {self.shape}'
        assert all([dima >= dimb for dima, dimb in zip(self.nnshape, data_nnx.shape[:2])]), \
            f'{self.nnshape} < {data_nnx.shape[:2]}'
        data_nnx = self.broadcast_x(data_nnx)  # Broadcast the last dimensions
        assert data_nnx.shape[2:] == self.xshape, f'{data_nnx.shape[2:]} != {self.xshape}'
        s = tuple([slice(dim) for dim in data_nnx.shape[:2]]) + self.xellipsis
        buffer_nnx = self._get_data(real, derivative)
        buffer_nnx[s] = data_nnx

    def safe_add(self,
                 real: bool,
                 derivative: int,
                 data_nnx: NDArray[DTypeT]):
        """ Add data_nnx to the corrsponding buffer, if the dimensions of data_nnx
        are equal to or smaller than the buffer

        If the dimensions of data_nnx are smaller than or equal to the dimensions
        of the buffer, add to the first elements of the buffer.
        Otherwise raise and error.

        Parameters
        ----------
        real
            ``True`` if real, ``False`` if imaginary.
        derivative
            Derivative order.
        buffer_nnx
            Data of shape ``(nnshape, xshape)``.
        """
        assert len(data_nnx.shape) <= len(self.shape), f'{data_nnx.shape} > {self.shape}'
        assert all([dima >= dimb for dima, dimb in zip(self.nnshape, data_nnx.shape[:2])]), \
            f'{self.nnshape} < {data_nnx.shape[:2]}'
        data_nnx = self.broadcast_x(data_nnx)  # Broadcast the last dimensions
        assert data_nnx.shape[2:] == self.xshape, f'{data_nnx.shape[2:]} != {self.xshape}'
        s = tuple([slice(dim) for dim in data_nnx.shape[:2]]) + self.xellipsis
        buffer_nnx = self._get_data(real, derivative)
        # Regarding ignore:
        # https://stackoverflow.com/questions/74633074/how-to-type-hint-a-generic-numpy-array/74634650#74634650
        buffer_nnx[s] += data_nnx  # type: ignore

    @property
    def derivatives_real(self) -> list[int]:
        """ Stored derivative order of real density matrices in sorted order """
        return list(sorted(self._re_buffers.keys()))

    @property
    def derivatives_imag(self) -> list[int]:
        """ Stored derivative order of real density matrices in sorted order """
        return list(sorted(self._im_buffers.keys()))

    def _iter_buffers(self) -> Generator[NDArray[DTypeT], None, None]:
        """ Loop over all real imaginary buffers in a sorted order """
        for derivative in self.derivatives_real:
            yield self._re_buffers[derivative]
        for derivative in self.derivatives_imag:
            yield self._im_buffers[derivative]

    def _iter_reim_derivatives(self) -> Generator[tuple[bool, int], None, None]:
        """ Loop over tuples (real, derivative) in sorted order.

        The parameter real is ``True`` for real buffers and the parameter derivative denotes the
        derivative order of the buffer.
        """
        for derivative in self.derivatives_real:
            yield (True, derivative)
        for derivative in self.derivatives_imag:
            yield (False, derivative)

    def ensure_contiguous_buffers(self):
        """ Make the buffers contiguous if they are not already. """
        for derivative in self.derivatives_real:
            self._re_buffers[derivative] = np.ascontiguousarray(self._re_buffers[derivative])
        for derivative in self.derivatives_imag:
            self._im_buffers[derivative] = np.ascontiguousarray(self._im_buffers[derivative])

    def send_arrays(self,
                    comm,
                    rank: int,
                    log: Logger | None = None):
        """ Send data to another MPI rank.

        Parameters
        ----------
        comm
            Communicator.
        rank
            Send to this rank.
        log
            Optional logger.
        """
        if comm.rank == rank:
            # Sending to send
            return

        if log is not None:
            log.start('send_to_root')

        requests = []
        for mpitag, buffer_nnx in enumerate(self._iter_buffers(), start=987):
            buffer_nnx = np.ascontiguousarray(buffer_nnx)
            requests.append(comm.send(buffer_nnx, 0, tag=mpitag, block=False))
        comm.waitall(requests)

        if log is not None:
            log(f'Sending to root {log.elapsed("send_to_root"):.1f}s', who='Response', flush=True)

    def recv_arrays(self,
                    comm,
                    rank: int,
                    log: Logger | None = None):
        """ Receive data to another MPI rank.

        Parameters
        ----------
        comm
            Communicator.
        rank
            Send to this rank.
        log
            Optional logger.
        """
        if comm.rank == rank:
            # Receiving from self
            return

        if log is not None:
            log.start('root_recv')

        requests = []
        for mpitag, buffer_nnx in enumerate(self._iter_buffers(), start=987):
            requests.append(comm.receive(buffer_nnx, rank, tag=mpitag, block=False))
        comm.waitall(requests)

        if log is not None:
            log(f'Root received {log.elapsed("root_recv"):.1f}s from {rank}', who='Response', flush=True)

    def redistribute(self,
                     target: DensityMatrixBuffer,
                     comm,
                     source_indices_r: Sequence[tuple[ArrayIndex, ...] | ArrayIndex | None],
                     target_indices_r: Sequence[tuple[ArrayIndex, ...] | ArrayIndex | None],
                     log: Logger | None = None,
                     ):
        """ Redistribute this DensityMatrixBuffer to another according to user specified options.

        The nn dimensions of the self and target buffers should be the same,
        but the x dimensions can be different. However, self need to have the same shape on all ranks
        and target needs to have the same shape on all ranks.

        Parameters
        ----------
        target
            Target :class:`DensityMatrixBuffer`.
        comm
            MPI communicator.
        source_indices_r
            List of x-indices. The length of the list must equal to the communicator size.
            The x-index that is element r of the list corresponds
            to the data from the source that will be sent to rank r.
            If the x-index is None, then the rank corresponding to that element will not be
            receiving data.  This argument must be the same on all ranks
        recv_indices_r
            List of x-indices. The length of the list must equal to the communicator size.
            The x-index that is element r of the list corresponds
            to the data in the target that will be received from rank r.
            If the x-index is None, then the rank corresponding to that element will not be
            sending data.  This argument must be the same on all ranks
        log
            Optional logger.
        """
        # Size of each density matrix (the nn-dimensions)
        nnsize = int(np.prod(self.nnshape))
        # Convert maxsize to maximum number of elements
        maxsize = env.get_float('REDISTRIBUTE_MAXSIZE')
        maxtotalelems = int(np.ceil(maxsize / self.dtype.itemsize))

        assert len(source_indices_r) == comm.size, len(source_indices_r)
        assert len(target_indices_r) == comm.size, len(target_indices_r)

        # Extract source and target indices that are not None and make sure they are tuples
        source_indices_by_rank = {rank: x_indices if isinstance(x_indices, tuple) else (x_indices, )
                                  for rank, x_indices in enumerate(source_indices_r)
                                  if x_indices is not None}
        target_indices_by_rank = {rank: x_indices if isinstance(x_indices, tuple) else (x_indices, )
                                  for rank, x_indices in enumerate(target_indices_r)
                                  if x_indices is not None}
        assert len(source_indices_by_rank) > 0
        assert len(target_indices_by_rank) > 0

        # Make sure that same derivatives and real/imaginary parts are stored and that dtypes are same
        assert tuple(self.derivatives_real) == tuple(target.derivatives_real)
        assert tuple(self.derivatives_imag) == tuple(target.derivatives_imag)
        assert self.dtype == target.dtype, f'{self.dtype} != {target.dtype}'

        # Get the xshapes of all sources
        source_xshape_by_rank: dict[int, tuple[int, ...]] = dict()
        if comm.rank in target_indices_by_rank.keys():
            for buf_nnx in self._iter_buffers():
                source_xshape_by_rank = {rank: buf_nnx[self.nnellipsis + x_indices].shape[2:]
                                         for rank, x_indices in source_indices_by_rank.items()}
                break

        # Get the xshapes of the targets by an alltoall operation with the sources
        # -2 means nothing, -1 in first field means empty tuple
        xdims = max(len(self.xshape), len(target.xshape))
        pad_target_xshape_r = -2 * np.ones((comm.size, xdims), dtype=int)
        pad_source_xshape_r = -2 * np.ones((comm.size, xdims), dtype=int)
        for rank, xshape in source_xshape_by_rank.items():
            pad_source_xshape_r[rank, :len(xshape)] = xshape
            if xshape == ():
                pad_source_xshape_r[rank, 0] = -1
        comm.alltoallv(pad_source_xshape_r,
                       xdims * np.ones(comm.size, dtype=int),
                       xdims * np.arange(comm.size, dtype=int),
                       pad_target_xshape_r,
                       xdims * np.ones(comm.size, dtype=int),
                       xdims * np.arange(comm.size, dtype=int))
        target_xshape_by_rank = {rank: tuple(xshape[xshape > -1])
                                 for rank, xshape in enumerate(pad_target_xshape_r) if xshape[0] > -2}
        # Check that target sizes supplied by the user are shorter than
        # or equal to the sizes from the alltoall operation
        if comm.rank in source_indices_by_rank.keys():
            for buf_nnx in target._iter_buffers():
                for rank, x_indices in target_indices_by_rank.items():
                    target_xshape = target_xshape_by_rank[rank]
                    xshape = buf_nnx[self.nnellipsis + x_indices].shape[2:]
                    assert all(np.less_equal(target_xshape, xshape))
                break

        # Get the total number of density matrices that this rank sends/receives
        source_xsize_by_rank = {rank: np.prod(xshape, dtype=int)
                                for rank, xshape in source_xshape_by_rank.items()}
        target_xsize_by_rank = {rank: np.prod(xshape, dtype=int)
                                for rank, xshape in target_xshape_by_rank.items()}
        my_sourcexsize = sum(source_xsize_by_rank.values())
        my_targetxsize = sum(target_xsize_by_rank.values())
        # Get the total number of array elements to be sent across all ranks
        sizes = np.array([my_sourcexsize, my_targetxsize], dtype=int)
        comm.sum(sizes, root=-1)
        total_sourcexsize, total_targetxsize = sizes
        totalsize = max(total_sourcexsize, total_targetxsize) * nnsize

        # Split the data across the nn-dimensions since they are always the same; how many times?
        factortoolarge = totalsize / maxtotalelems
        nnstride = int(np.ceil(nnsize / factortoolarge))
        nnstride = min(nnsize, nnstride)
        nsplits = int(np.ceil(nnsize / nnstride))
        if log is not None and comm.rank == 0:
            total_MiB = totalsize * self.dtype.itemsize / (1024 ** 2)
            buftotal_MiB = totalsize / nsplits * self.dtype.itemsize / (1024 ** 2)

            log(f'Redistribute: {len(target_indices_by_rank)} sending '
                f'and {len(source_indices_by_rank)} receiving. '
                f'Total size on all ranks ({total_MiB:.1f} MiB) '
                f'splitting in {nsplits} parts ({buftotal_MiB:.1f} MiB on all ranks)',
                who='Response', flush=True)

        # Perpare buffers for sending and receiving
        # counts - Number of elements to send to (s) or receive from (r) each rank
        # displs - Position of data to send to (s) or receive from (r) each rank
        sendbuf = np.zeros(my_sourcexsize * nnstride, dtype=self.dtype)
        recvbuf = np.zeros(my_targetxsize * nnstride, dtype=self.dtype)
        scounts_r = np.zeros(comm.size, dtype=int)
        sdispls_r = np.zeros(comm.size, dtype=int)
        rcounts_r = np.zeros(comm.size, dtype=int)
        rdispls_r = np.zeros(comm.size, dtype=int)

        displ = 0
        if comm.rank in target_indices_by_rank.keys():
            # This rank has some data to send. It will send to the ranks that are among the source keys
            sendbuf_by_rank = dict()
            for buf_nnx in self._iter_buffers():
                for destrank, xsize in source_xsize_by_rank.items():
                    size = xsize * nnstride
                    sendbuf_by_rank[destrank] = sendbuf[displ:displ+size]
                    scounts_r[destrank] = size
                    if size > 0:
                        sdispls_r[destrank] = displ
                    displ += size
                break
        displ = 0
        if comm.rank in source_indices_by_rank.keys():
            # This rank has some data to receive. It will receive from the ranks that are among the target keys
            recvbuf_by_rank = dict()
            for buf_nnx in self._iter_buffers():
                for destrank, xsize in target_xsize_by_rank.items():
                    size = xsize * nnstride
                    recvbuf_by_rank[destrank] = recvbuf[displ:displ+size]
                    rcounts_r[destrank] = size
                    if size > 0:
                        rdispls_r[destrank] = displ
                    displ += size
                break

        # Flattened nn-dimensions for splitting
        flatslices = [slice(start, start + nnstride, 1) for start in range(0, nnsize, nnstride)]
        grid = np.mgrid[:self.nnshape[0], :self.nnshape[1]]

        # Loop over real and imaginary parts and derivatives
        for (real, derivative), sendbuf_nnx, recvbuf_nnx in zip(
                self._iter_reim_derivatives(), self._iter_buffers(), target._iter_buffers()):

            # List of data to send and list of buffers where data should be received
            if comm.rank in target_indices_by_rank.keys():
                senddata_by_rank = {rank: sendbuf_nnx[self.nnellipsis + x_indices]
                                    for rank, x_indices in source_indices_by_rank.items()}
            if comm.rank in source_indices_by_rank.keys():
                recvdata_by_rank = {rank: recvbuf_nnx[self.nnellipsis + x_indices]
                                    for rank, x_indices in target_indices_by_rank.items()}
                # The target data may be smaller than what is given by the user
                recvdata_by_rank = {rank: recvdata_by_rank[rank][
                                        self.nnellipsis + tuple([slice(dim) for dim in xshape])]
                                    for rank, xshape in target_xshape_by_rank.items()}
                for data, xshape in zip(recvdata_by_rank.values(), target_xshape_by_rank.values()):
                    assert data.shape[2:] == xshape, str(data.shape[2:]) + ' != ' + str(xshape)

            # Loop over the data in splits
            for flatslice in flatslices:
                # Slices of nn
                nnslices = (grid[0].ravel()[flatslice], grid[1].ravel()[flatslice])

                # Copy data to the contiguous send buffer
                if comm.rank in target_indices_by_rank.keys():
                    for destrank, buf in sendbuf_by_rank.items():
                        data = senddata_by_rank[destrank][nnslices].ravel()
                        buf[:len(data)] = data

                # Send the data
                comm.alltoallv(sendbuf, scounts_r, sdispls_r,
                               recvbuf, rcounts_r, rdispls_r)

                # Copy data from the contiguous receive buffer
                if comm.rank in source_indices_by_rank.keys():
                    for destrank, buf in recvbuf_by_rank.items():
                        # Copy the first elements of the receive buffer to the data position
                        datashape = recvdata_by_rank[destrank][nnslices].shape
                        datalen = np.prod(datashape, dtype=int)
                        buf = buf[:datalen]
                        recvdata_by_rank[destrank][nnslices] = buf.reshape(datashape)
