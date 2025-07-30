from __future__ import annotations

import re
from contextlib import nullcontext
from operator import itemgetter
from pathlib import Path
from typing import Any, Callable, Generic, Iterable, NamedTuple, TypeVar
import numpy as np
from numpy.typing import NDArray
from numpy._typing import _DTypeLike as DTypeLike  # parametrizable wrt generic

from ase.io.ulm import open
from ase.parallel import parprint
from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition
from gpaw.lcaotddft.laser import GaussianPulse
from gpaw.mpi import SerialCommunicator, world
from gpaw.tddft.units import fs_to_au, au_to_eV

from .logging import Logger, NoLogger
from .result import Result, ResultKeys
from ..perturbation import Perturbation
from ..typing import Array1D, Communicator

__all__ = [
    'Logger',
    'Result',
    'ResultKeys',
]


DTypeT = TypeVar('DTypeT', bound=np.generic, covariant=True)


class ParallelMatrix(Generic[DTypeT]):

    """ Distributed array, with data on the root rank.

    Parameters
    ----------
    shape
        Shape of array.
    dtype
        Dtype of array.
    comm
        MPI communicator.
    array
        Array on root rank of the communicator. Must be ``None`` on other ranks.
    """

    def __init__(self,
                 shape: tuple[int, ...],
                 dtype: DTypeLike[DTypeT],
                 comm: Communicator | None = None,
                 array: NDArray[DTypeT] | None = None):
        if comm is None:
            comm = world
        self.comm = comm
        self.shape = shape
        self.dtype = np.dtype(dtype)

        self._array: NDArray[DTypeT] | None
        if self.root:
            assert array is not None
            assert array.shape == shape
            assert array.dtype == np.dtype(dtype)
            self._array = array
        else:
            assert array is None
            self._array = None

    @property
    def array(self) -> NDArray[DTypeT]:
        """ Array with data. May only be called on the root rank. """
        if not self.root:
            raise RuntimeError('May only be called on root')
        assert self._array is not None
        return self._array

    @property
    def root(self) -> bool:
        """ Whether this rank is the root rank. """
        return self.comm.rank == 0

    @property
    def T(self) -> ParallelMatrix:
        shape = self.shape[:-2] + self.shape[-2:][::-1]
        return ParallelMatrix(shape=shape, dtype=self.dtype, comm=self.comm,
                              array=self.array.T if self.root else None)

    def broadcast(self) -> NDArray[DTypeT]:
        """ Broadcasted data. """
        if self.root:
            A = np.ascontiguousarray(self.array)
        else:
            A = np.zeros(self.shape, self.dtype)

        self.comm.broadcast(A, 0)

        return A

    def __matmul__(self, other) -> ParallelMatrix[DTypeT]:
        """ Perform matrix multiplication in parallel. """
        if not isinstance(other, ParallelMatrix):
            raise NotImplementedError

        assert self.dtype == other.dtype

        A = self.broadcast()
        B = other.broadcast()

        # Allocate array for result
        ni, nj = A.shape[-2:]
        nk = B.shape[-1]
        C_shape = np.broadcast_shapes(A.shape[:-2], B.shape[:-2]) + (ni, nk)
        C = np.zeros(C_shape, self.dtype)

        # Determine slice for ranks
        stridek = (nk + self.comm.size - 1) // self.comm.size
        slicek = slice(stridek * self.comm.rank, stridek * (self.comm.rank + 1))

        # Perform the matrix multiplication
        C[..., :, slicek] = A @ B[..., :, slicek]

        # Sum to root rank
        self.comm.sum(C, 0)

        result = ParallelMatrix(C_shape, self.dtype, comm=self.comm,
                                array=C if self.root else None)
        return result


def gauss_ij_with_filter(energy_i: np.typing.ArrayLike,
                         energy_j: np.typing.ArrayLike,
                         sigma: float,
                         fltthresh: float | None = None,
                         ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    r""" Computes the matrix

    .. math::

        M_{ij}
        = \frac{1}{\sqrt{2 \pi \sigma^2}}
        \exp\left(-\frac{
            \left(\varepsilon_i - \varepsilon_j\right)^2
        }{
            2 \sigma^2
        }\right)

    Useful for Gaussian broadening. Optionally only computes the exponent
    above a certain threshold, and returns the filter.

    Parameters
    ----------
    energy_i
        Energies :math:`\varepsilon_i`.
    energy_j
        Energies :math:`\varepsilon_j`.
    sigma
        Gaussian broadening width :math:`\sigma`.
    fltthresh
        Filtering threshold.

    Returns
    -------
        Matrix :math:`M_{ij}`, filter.
    """
    energy_i = np.asarray(energy_i)
    energy_j = np.asarray(energy_j)

    norm = 1.0 / (sigma * np.sqrt(2 * np.pi))

    denergy_ij = energy_i[:, np.newaxis] - energy_j[np.newaxis, :]
    exponent_ij = -0.5 * (denergy_ij / sigma) ** 2

    if fltthresh is not None:
        flt_i = np.any(exponent_ij > fltthresh, axis=1)
        M_ij = np.zeros_like(exponent_ij)
        M_ij[flt_i] = norm * np.exp(exponent_ij[flt_i])
    else:
        flt_i = np.ones(energy_i.shape, dtype=bool)
        M_ij = norm * np.exp(exponent_ij)

    return M_ij, flt_i  # type: ignore


def gauss_ij(energy_i: np.typing.ArrayLike,
             energy_j: np.typing.ArrayLike,
             sigma: float) -> NDArray[np.float64]:
    r""" Computes the matrix

    .. math::

        M_{ij}
        = \frac{1}{\sqrt{2 \pi \sigma^2}}
        \exp\left(-\frac{
            \left(\varepsilon_i - \varepsilon_j\right)^2
        }{
            2 \sigma^2
        }\right),

    which is useful for Gaussian broadening.

    Parameters
    ----------
    energy_i
        Energies :math:`\varepsilon_i`.
    energy_j
        Energies :math:`\varepsilon_j`.
    sigma
        Gaussian broadening width :math:`\sigma`.

    Returns
    -------
        Matrix :math:`M_{ij}`.
    """
    M_ij, _ = gauss_ij_with_filter(energy_i, energy_j, sigma)
    return M_ij


def broaden_n2e(M_n: np.typing.ArrayLike,
                energy_n: np.typing.ArrayLike,
                energy_e: np.typing.ArrayLike,
                sigma: float) -> NDArray[np.float64]:
    r""" Broaden matrix onto energy grids

    .. math::

        M(\varepsilon_e)
        = \sum_n M_n \frac{1}{\sqrt{2 \pi \sigma^2}}
        \exp\left(-\frac{
            \left(\varepsilon_n - \varepsilon_e\right)^2
        }{
            2 \sigma^2
        }\right),

    Returns
    -------
        :math:`M(\varepsilon_0)`
    """
    M_n = np.asarray(M_n)
    gauss_ne, flt_n = gauss_ij_with_filter(energy_n, energy_e, sigma)

    M_e = np.einsum('n,ne->e', M_n[flt_n], gauss_ne[flt_n], optimize=True)

    return M_e


def broaden_xn2e(M_xn: np.typing.ArrayLike,
                 energy_n: np.typing.ArrayLike,
                 energy_e: np.typing.ArrayLike,
                 sigma: float) -> NDArray[np.float64]:
    r""" Broaden matrix onto energy grids

    .. math::

        M(\varepsilon_e)
        = \sum_n M_n \frac{1}{\sqrt{2 \pi \sigma^2}}
        \exp\left(-\frac{
            \left(\varepsilon_n - \varepsilon_e\right)^2
        }{
            2 \sigma^2
        }\right).

    Returns
    -------
        :math:`M(\varepsilon_0)`.
    """
    M_xn = np.asarray(M_xn)
    gauss_ne, flt_n = gauss_ij_with_filter(energy_n, energy_e, sigma)

    M_xe = np.einsum('xn,ne->xe',
                     M_xn.reshape((-1, len(flt_n)))[:, flt_n],
                     gauss_ne[flt_n],
                     optimize=True).reshape(M_xn.shape[:-1] + (-1, ))

    return M_xe


def broaden_ia2ou(M_ia: np.typing.ArrayLike,
                  energy_i: np.typing.ArrayLike,
                  energy_a: np.typing.ArrayLike,
                  energy_o: np.typing.ArrayLike,
                  energy_u: np.typing.ArrayLike,
                  sigma: float) -> NDArray[np.float64]:
    r""" Broaden matrix onto energy grids.

    .. math::

        M(\varepsilon_o, \varepsilon_u)
        = \sum_{ia} M_{ia} \frac{1}{\sqrt{2 \pi \sigma^2}}
        \exp\left(-\frac{
            (\varepsilon_i - \varepsilon_o)^2
        }{
            2 \sigma^2
        }\right)
        \exp\left(-\frac{
            (\varepsilon_a - \varepsilon_u)^2
        }{
            2 \sigma^2
        }\right)

    Returns
    -------
        :math:`M(\varepsilon_o, \varepsilon_u)`.
    """
    M_ia = np.asarray(M_ia)
    ia_shape = M_ia.shape[:2]
    x_shape = M_ia.shape[2:]
    M_iax = M_ia.reshape(ia_shape + (-1, ))
    gauss_io, flt_i = gauss_ij_with_filter(energy_i, energy_o, sigma)
    gauss_au, flt_a = gauss_ij_with_filter(energy_a, energy_u, sigma)

    M_oux = np.einsum('iax,io,au->oux', M_iax[flt_i, :][:, flt_a],
                      gauss_io[flt_i], gauss_au[flt_a],
                      optimize=True, order='C')

    return M_oux.reshape(M_oux.shape[:2] + x_shape)


def get_array_filter(values: Array1D[np.float64] | list[float],
                     filter_values: Array1D[np.float64] | list[float] | None,
                     ) -> slice | Array1D[np.bool_]:
    """ Get array filter that can be used to filter out data.

    Parameters
    ----------
    values
        Array of values, e.g. linspace of times or frequencies.
    filter_values
        List of values that one wishes to extract. The closes values from values
        will be selected as filter.

    Returns
    -------
    Object that can be used to index values and arrays with the same shape as values.
    """
    _values = np.array(values)
    flt_x: slice | NDArray[np.bool_]
    if len(values) == 0:
        # Empty list of arrays
        return slice(None)

    if filter_values is None or len(filter_values) == 0:
        # No filter
        return slice(None)

    flt_x = np.zeros(len(values), dtype=bool)
    for filter_value in filter_values:
        # Search for closest value
        idx = np.argmin(np.abs(_values - filter_value))
        flt_x[idx] = True

    return flt_x


def filter_array(values: Array1D[np.float64] | list[float],
                 filter_values: Array1D[np.float64] | list[float] | None,
                 ) -> Array1D[np.float64]:
    """ Filter array, picking values closest to :attr:`filter_values`.

    Parameters
    ----------
    values
        Array of values, e.g. linspace of times or frequencies.
    filter_values
        List of values that one wishes to extract. The closes values from values
        will be selected as filter.

    Returns
    -------
    Filtered array.
    """
    array = np.array(values)
    return array[get_array_filter(array, filter_values)]  # type: ignore


def two_communicator_sizes(*comm_sizes) -> tuple[int, int]:
    assert len(comm_sizes) == 2
    comm_size_c: list[int] = [world.size if size == 'world' else size for size in comm_sizes]
    if comm_size_c[0] == -1:
        comm_size_c[0] = world.size // comm_size_c[1]
    elif comm_size_c[1] == -1:
        comm_size_c[1] = world.size // comm_size_c[0]

    assert np.prod(comm_size_c) == world.size, \
        f'Communicator sizes must factorize world size {world.size} '\
        'but they are ' + ' and '.join([str(s) for s in comm_size_c]) + '.'
    return comm_size_c[0], comm_size_c[1]


def two_communicators(*comm_sizes) -> tuple[Communicator, Communicator]:
    """ Create two MPI communicators.

    Must satisfy ``comm_sizes[0] * comm_sizes[1] = world.size``.

    The second communicator has the ranks in sequence.

    Example
    -------

    >>> world.size == 8
    >>> two_communicators(2, 4)

    This gives::

        [0, 4]
        [1, 5]
        [2, 6]
        [3, 7]

    and::

        [0, 1, 2, 3]
        [4, 5, 6, 7]
    """
    comm_size_c = two_communicator_sizes(*comm_sizes)

    # Create communicators
    if comm_size_c[0] == 1:
        return (SerialCommunicator(), world)  # type: ignore
    elif comm_size_c[0] == world.size:
        return (world, SerialCommunicator())  # type: ignore
    else:
        assert world.size % comm_size_c[0] == 0, world.size
        # Comm 2, ranks in sequence. Comm 1, ranks skip by size of comm 2
        first_rank_in_comm_c = [world.rank % comm_size_c[1],
                                world.rank - world.rank % comm_size_c[1]]
        step_c = [comm_size_c[1], 1]
        comm_ranks_cr = [list(range(start, start + size*step, step))
                         for start, size, step in zip(first_rank_in_comm_c, comm_size_c, step_c)]
        comm_c = [world.new_communicator(comm_ranks_r) for comm_ranks_r in comm_ranks_cr]
        return comm_c[0], comm_c[1]


def detect_repeatrange(n: int,
                       stride: int,
                       verbose: bool = True) -> slice | None:
    """ If an array of length :attr:`n` is not divisible by the stride :attr:`stride`
    then some work will have to be repeated
    """
    final_start = (n // stride) * stride
    repeatrange = slice(final_start, n)
    if repeatrange.start == repeatrange.stop:
        return None
    else:
        print(f'Detected repeatrange {repeatrange}', flush=True)
        return repeatrange

    return None


def safe_fill(a: NDArray[DTypeT],
              b: NDArray[DTypeT]):
    """ Perform the operation ``a[:] = b``, checking if the dimensions match.

    If the dimensions of :attr:`b` are larger than the dimensions of :attr:`a`, raise an error.

    If the dimensions of :attr:`b` are smaller than the dimensions of :attr:`a`, write to
    the first elements of :attr:`a`.
    """
    assert len(a.shape) == len(b.shape), f'{a.shape} != {b.shape}'
    assert all([dima >= dimb for dima, dimb in zip(a.shape, b.shape)]), f'{a.shape} < {b.shape}'
    s = tuple([slice(dim) for dim in b.shape])
    a[s] = b


def safe_fill_larger(a: NDArray[DTypeT],
                     b: NDArray[DTypeT]):
    """ Perform the operation ``a[:] = b``, checking if the dimensions match.

    If the dimensions of :attr:`b` are smaller than the dimensions of :attr:`a`, raise an error.

    If the dimensions of :attr:`b` are larger than the dimensions of :attr:`a`, write the first
    elements of :attr:`b` to :attr:`a`.
    """
    assert len(a.shape) == len(b.shape), f'{a.shape} != {b.shape}'
    assert all([dimb >= dima for dima, dimb in zip(a.shape, b.shape)]), f'{a.shape} > {b.shape}'
    s = tuple([slice(dim) for dim in a.shape])
    a[:] = b[s]


IND = TypeVar('IND', slice, tuple[slice, ...])


def concatenate_indices(indices_list: Iterable[IND],
                        ) -> tuple[IND, list[IND]]:
    """ Concatenate indices.

    Given an array A and a list of incides indices_list such that A can be indexed

    >>> for indices in indices_list:
    >>>     A[indices]

    this function shall concatenate the indices into indices_concat so that the array
    can be indexed in one go. This function will also give a new list of indices
    new_indices_list that can be used to index the ``A[indices_concat]``. The following
    snippet shall be equivalent to the previous snipped.

    >>> B = A[indices_concat]
    >>> for indices in new_indices_list:
    >>>     B[indices]

    Note that the indices need not be ordered, nor contigous, but the returned
    indices_concat will be a list of slices, and thus contiguous.

    Example
    -------

    >>> A = np.random.rand(100)
    >>> value = 0
    >>> new_value = 0
    >>>
    >>> indices_list = [slice(10, 12), slice(12, 19)]
    >>> for indices in indices_list:
    >>>     value += np.sum(A[indices])
    >>>
    >>> indices_concat, new_indices_list = concatenate_indices(indices_list)
    >>> new_value = np.sum(A[indices_concat])
    >>>
    >>> assert abs(value - new_value) < 1e-10
    >>>
    >>> B = A[indices_concat]
    >>> assert B.shape == (9, )
    >>> new_value = 0
    >>> for indices in new_indices_list:
    >>>     new_value += np.sum(B[indices])
    >>>
    >>> assert abs(value - new_value) < 1e-10

    Returns
    -------
        ``(indices_concat, new_indices_list)``
    """
    indices_list = list(indices_list)
    if len(indices_list) == 0:
        return slice(0), []  # type: ignore

    if not isinstance(indices_list[0], tuple):
        # If indices are not tuples, then wrap everything in tuples and recurse
        assert all([not isinstance(indices, tuple) for indices in indices_list])
        _indices_concat, _new_indices_list = _concatenate_indices([(indices, ) for indices in indices_list])
        return _indices_concat[0], [indices[0] for indices in _new_indices_list]

    # All indices are wrapped in tuples
    assert all([isinstance(indices, tuple) for indices in indices_list])
    return _concatenate_indices(indices_list)  # type: ignore


def _concatenate_indices(indices_list: Iterable[tuple[slice, ...]],
                         ) -> tuple[tuple[slice, ...], list[tuple[slice, ...]]]:
    """ See :func:`concatenate_indices`
    """
    limits_jis = np.array([[(index.start, index.stop, index.step) for index in indices]
                           for indices in indices_list])

    start_i = np.min(limits_jis[..., 0], axis=0)
    stop_i = np.max(limits_jis[..., 1], axis=0)

    indices_concat = tuple([slice(start, stop) for start, stop in zip(start_i, stop_i)])
    new_indices_list = [tuple([slice(start - startcat, stop - startcat, step)
                               for (startcat, (start, stop, step)) in zip(start_i, limits_is)])
                        for limits_is in limits_jis]

    return indices_concat, new_indices_list


def parulmopen(fname: str, comm: Communicator, *args, **kwargs):
    if comm.rank == 0:
        return open(fname, *args, **kwargs)
    else:
        return nullcontext()


def proxy_sknX_slicen(reader, *args, comm: Communicator) -> NDArray[np.complex128]:
    if len(args) == 0:
        A_sknX = reader
    else:
        A_sknX = reader.proxy(*args)
    nn = A_sknX.shape[2]
    nlocaln = (nn + comm.size - 1) // comm.size
    myslicen = slice(comm.rank * nlocaln, (comm.rank + 1) * nlocaln)
    my_A_sknX = np.array([[A_nX[myslicen] for A_nX in A_knX] for A_knX in A_sknX])

    return my_A_sknX


def add_fake_kpts(ksd: KohnShamDecomposition):
    """This function is necessary to read some fields without having a
    calculator attached.
    """

    class FakeKpt(NamedTuple):
        s: int
        k: int

    class FakeKsl(NamedTuple):
        using_blacs: bool = False

    # Figure out
    ksdreader = ksd.reader
    skshape = ksdreader.eig_un.shape[:2]
    kpt_u = [FakeKpt(s=s, k=k)
             for s in range(skshape[0])
             for k in range(skshape[1])]
    ksd.kpt_u = kpt_u
    ksd.ksl = FakeKsl()


def create_pulse(frequency: float,
                 fwhm: float = 5.0,
                 t0: float = 10.0,
                 print: Callable | None = None) -> GaussianPulse:
    """ Create Gaussian laser pulse.

    frequency
        Pulse frequncy in units of eV.
    fwhm
        Full width at half maximum in time domain in units of fs.
    t0
        Maximum of pulse envelope in units of fs.
    print
        Printing function to control verbosity.
    """
    if print is None:
        print = parprint

    # Pulse
    fwhm_eV = 8 * np.log(2) / (fwhm * fs_to_au) * au_to_eV
    tau = fwhm / (2 * np.sqrt(2 * np.log(2)))
    sigma = 1 / (tau * fs_to_au) * au_to_eV  # eV
    strength = 1e-6
    t0 = t0 * 1e3
    sincos = 'cos'
    print(f'Creating pulse at {frequency:.3f}eV with FWHM {fwhm:.2f}fs '
          f'({fwhm_eV:.2f}eV) t0 {t0:.1f}fs', flush=True)

    return GaussianPulse(strength, t0, frequency, sigma, sincos)


def get_gaussian_pulse_values(pulse: Perturbation) -> dict[str, float]:
    """ Get pulse frequency and FWHM of Gaussian pulse.

    Returns
    -------
    Empty dictionary if pulse is not `GaussianPulse`, otherwise dictionary with keys:

        ``pulsefreq`` - pulse frequency in units of eV.
        ``pulsefwhm`` - pulse full width at half-maximum in time domain in units of fs.
    """
    from gpaw.tddft.units import eV_to_au, au_to_fs

    d = pulse.todict()
    ret: dict[str, float] = dict()
    if d['name'] == 'GaussianPulse':
        ret['pulsefreq'] = d['frequency']
        ret['pulsefwhm'] = (1 / (d['sigma'] * eV_to_au) * au_to_fs *
                            (2 * np.sqrt(2 * np.log(2))))
    return ret


fast_pad_nice_factors = np.array([4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 8096])


def fast_pad(nt: int) -> int:
    """ Return a length that is at least twice as large as the given input,
    and the FFT of data of such length is fast.
    """
    padnt = 2 * nt
    insert = np.searchsorted(fast_pad_nice_factors, padnt)
    if insert <= len(fast_pad_nice_factors):
        padnt = fast_pad_nice_factors[insert]
    assert padnt >= 2 * nt
    return padnt


def format_string_to_glob(fmt: str) -> str:
    """ Convert a format string to a glob-type expression.

    Replaces all the replacement fields ``{...}`` in the format string
    with a glob ``*``.

    Example
    -------
    >>> format_string_to_glob('pulserho_pf{pulsefreq:.2f}/t{time:09.1f}{tag}.npy')
    pulserho_pf*/t*.npy

    Parameters
    ---------
    fmt
        Format string.

    Returns
    -------
    Glob-type expression.
    """
    # Replace replacement fields by *
    # Note how several replacement fields next to each other are
    # replaced by only one * thanks to the (...)+
    glob_expr = re.sub(r'({[^{}]*})+', '*', fmt)
    return glob_expr


def format_string_to_regex(fmt: str) -> re.Pattern:
    r""" Convert a format string to a regex expression.

    Replaces all the replacement fields ``{...}`` in the format string
    with a regular expression and escapes all special characters outside
    the replacement fields.

    Replacement fields for variables ``time``, ``freq``, ``pulsefreq``
    and ``pulsefwhm`` are replaced by regex matching floating point numbers.
    Replacement fields for variables ``reim`` and ``tag`` are replaced by
    regex matching alphabetic characters and dashes.
    Remaining replacement fields are replaced by regex matching alphabetic
    characters.

    This can be used to parse a formatted string in order to get back the original
    values.

    Example
    -------
    >>> fmt = 'pulserho_pf{pulsefreq:.2f}/t{time:09.1f}{tag}.npy'
    >>> s = fmt.format(pulsefreq=3.8, time=30000, tag='-Iomega')
    pulserho_pf3.80/t0030000.0-Iomega.npy
    >>> regex = format_string_to_regex(fmt)
    re.compile('pulserho_pf(?P<pulsefreq>[-+]?[\d.]+)/t(?P<time>[-+]?[\d.]+)(?P<tag>[-A-za-z]*)\.npy')
    >>> regex.fullmatch(s).groupdict()
    {'pulsefreq': '3.80', 'time': '0030000.0', 'tag': '-Iomega'}

    Parameters
    ---------
    fmt
        Format string.

    Returns
    -------
    Compiled regex pattern.

    Notes
    -----
    Replacement fields should be named and not contain any attributes or indexing.
    """
    regex_expr = str(fmt)

    # Split the expression by parts separated by replacement fields
    split = re.split(r'({[^{}]+})', regex_expr)
    # Every other element is guaranteed to be a replacement field
    # Escape everything that is not a replacement field
    split[::2] = [re.escape(s) for s in split[::2]]
    # Join the expression back together
    regex_expr = ''.join(split)

    # Replace float variables
    regex_expr = re.sub(r'{(time|freq|pulsefreq|pulsefwhm)[-:.\w]+}',
                        r'(?P<\1>[-+]?[\\d.]+)',
                        regex_expr)

    # Replace reim and tag
    regex_expr = re.sub(r'{(reim)}', r'(?P<\1>[A-za-z]+)', regex_expr)
    regex_expr = re.sub(r'{(tag)}', r'(?P<\1>[-A-za-z]*)', regex_expr)

    # Replace other
    regex_expr = re.sub(r'{(\w*)}', r'(?P<\1>[A-za-z]*)', regex_expr)

    compiled = re.compile(regex_expr)

    return compiled


def partial_format(fmt, **kwargs) -> str:
    """ Partially format the format string.

    Equivalent to calling ``fmt.format(**kwargs)`` but replacement fields
    that are not present in the ``**kwargs`` will be left in the format string.

    Parameters
    ----------
    fmt
        Format string.
    **kwargs
        Passed to the :py:meth:`str.format` call.

    Returns
    -------
    Partially formatted string.

    Example
    -------
    >>> fmt = 'pulserho_pf{pulsefreq:.2f}/t{time:09.1f}{tag}.npy'
    >>> partial_format(fmt, pulsefreq=3.8)
    pulserho_pf3.80/t{time:09.1f}{tag}.npy
    """
    def partial_format_single(s):
        try:
            # Try to format
            return s.format(**kwargs)
        except KeyError:
            # If the replacement field is not among the kwargs, return unchanged
            return s

    # Split the expression by parts separated by replacement fields
    split = re.split(r'({[^{}]+})', fmt)
    # Every other element is guaranteed to be a replacement field
    # Try to format each field separately
    split[1::2] = [partial_format_single(s) for s in split[1::2]]
    # Join the expression back together
    fmt = ''.join(split)

    return fmt


def find_files(fmt: str,
               log: Logger | None = None,
               *,
               expected_keys: list[str]):
    """ Find files in file system matching the format string :attr:`fmt`.

    This function walks the file tree and looks for file names matching the
    format string :attr:`fmt`.

    Parameters
    ----------
    fmt
        Format string.
    log
        Optional logger object.
    expected_keys
        List of replacement fields ``{...}`` that are expected to be parsed from
        the file names. Unexpected fields raise :py:exc:`ValueError`.

    Returns
    -------
    Dictionary with keys, sorted by the parsed values matching :attr:`expected_keys`:

        ``filename`` - List of filenames found.
        **key** - List of parsed value for each key in :attr:`expected_keys`.

    Example
    -------
    >>> fmt = 'pulserho_pf3.80/t{time:09.1f}{tag}.npy'
    >>> find_files(fmt, expected_keys=['time', 'tag'])
    {'filename': ['pulserho_pf3.80/t0000010.0.npy',
                  'pulserho_pf3.80/t0000010.0-Iomega.npy',
                  'pulserho_pf3.80/t0000060.0.npy',
                  'pulserho_pf3.80/t0000060.0-Iomega.npy'],
     'time': [10.0, 10.0, 60.0, 60.0],
     'tag': ['', '-Iomega', '', '-Iomega']}
    """
    if log is None:
        log = NoLogger()

    # Find base (containing no format string replacement fields)
    non_format_parents = [parent for parent in Path(fmt).parents
                          if '{' not in parent.name]
    base = non_format_parents[0] if len(non_format_parents) > 0 else Path('.')
    log(str(base), who='Find files', rank=0)

    # Express the format string relative to the base
    rel_pulserho_fmt = str(Path(fmt).relative_to(base))
    log(rel_pulserho_fmt, who='Find files', rank=0)

    # Convert format specifier to glob, and to regex
    pulserho_glob = format_string_to_glob(rel_pulserho_fmt)
    pulserho_regex = format_string_to_regex(rel_pulserho_fmt)
    log(pulserho_glob, who='Find files', rank=0)
    log(pulserho_regex.pattern, who='Find files', rank=0)

    matching = base.glob(pulserho_glob)

    found: list[dict[str, Any]] = []

    # Loop over the matching files
    for match in matching:
        relmatch = match.relative_to(base)
        m = pulserho_regex.fullmatch(str(relmatch))
        if m is None:
            continue
        metadata = {key: float(value) if key not in ['tag', 'reim'] else value
                    for key, value in m.groupdict().items()}
        fname = str(base / relmatch)
        test = fmt.format(**metadata)
        assert fname == test, fname + ' != ' + test
        if set(metadata.keys()) > set(expected_keys):
            raise ValueError(f'Found unexpected key in file name {base / relmatch}:\n'
                             f'Found {metadata}\nExpected {expected_keys}')
        log(relmatch, metadata, who='Find files', rank=0)
        metadata['filename'] = fname
        found.append(metadata)

    # Sort list of found files by expected_keys
    found = sorted(found, key=itemgetter(*expected_keys))

    # Unwrap so that we return one dictionary of lists
    ret = {key: [f.get(key, None) for f in found]
           for key in ['filename'] + expected_keys}

    return ret
