from __future__ import annotations

from typing import Collection
import numpy as np
from numpy.typing import ArrayLike, NDArray

from gpaw.mpi import world
from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition

from ...perturbation import Perturbation, PerturbationLike, create_perturbation
from ...typing import Array1D, Communicator
from ...utils import Logger, add_fake_kpts, find_files, partial_format, get_gaussian_pulse_values, filter_array
from ...utils.logging import format_times, format_frequencies


class TimeDensityMatrixReader:

    """ Finds density matrices in the time domain saved to disk and reads them.

    Parameters
    ----------
    pulserho_fmt
        Formatting string for the density matrices saved to disk.

        The formatting string should be a plain string containing variable
        placeholders within curly brackets ``{}``. It should not be confused with
        a formatted string literal (f-string).

        Example:

         * pulserho_fmt =  ``pulserho/t{time:09.1f}{tag}.npy``.

        Accepts variables

         * ``{time}`` - Time in units of as.
         * ``{tag}`` - Derivative tag, ``''``, ``'-Iomega'``, or ``'-omega2'``.
         * ``{pulsefreq}`` - Pulse frequency in units of eV.
         * ``{pulsefwhm}`` - Pulse FWHM in units of fs.
    ksd
        KohnShamDecomposition object or file name to the ksd file.
    filter_times
        Look for these times (or as close to them as possible). In units of as.
    pulses
        Density matrices in response to these pulses. By default, no information about the
        pulse.
    derivative_order_s
        List of derivative orders.
    log
        Logger object.
    """

    def __init__(self,
                 pulserho_fmt: str,
                 ksd: str | KohnShamDecomposition,
                 filter_times: Array1D[np.float64] | list[float] | None = None,
                 pulses: Collection[PerturbationLike] = [None],
                 derivative_order_s: list[int] = [0],
                 log: Logger | None = None,
                 comm: Communicator | None = None):
        if log is None:
            log = Logger()
        self._log = log
        self._comm = world if comm is None else comm

        if isinstance(ksd, KohnShamDecomposition):
            self._ksd = ksd
        else:
            self._ksd = KohnShamDecomposition(filename=ksd)
            add_fake_kpts(self._ksd)

        self._pulses = [create_perturbation(pulse) for pulse in pulses]
        self.derivative_order_s = derivative_order_s
        self.pulserho_fmt = pulserho_fmt
        tag_s = ['', '-Iomega', '-omega2']

        if self.comm.rank == 0:
            # Look for files on the root rank

            nested_times: list[Array1D[np.float64]] = []
            for pulse in self.pulses:
                for derivative in self.derivative_order_s:
                    # Partially format the format string, i.e. fill out the pulsefreq,
                    # pulsefwhm, and tag fields
                    tag = tag_s[derivative]
                    fmt = partial_format(pulserho_fmt, tag=tag, **get_gaussian_pulse_values(pulse))

                    # Search the file tree for files
                    f = find_files(fmt, expected_keys=['time'])
                    nested_times.append(f['time'])

        self._time_t, self._part_time_t = extract_common(nested_times if self.comm.rank == 0 else None,
                                                         filter_times,
                                                         self.comm)

    @property
    def ksd(self) -> KohnShamDecomposition:
        """ Kohn-Sham decomposition object. """
        return self._ksd

    @property
    def comm(self) -> Communicator:
        """ MPI communicator. """
        return self._comm

    @property
    def log(self) -> Logger:
        """ Logger object. """
        return self._log

    @property
    def times(self) -> Array1D[np.float64]:
        """ Simulation time in units of as. """
        return self._time_t

    @property
    def nt(self) -> int:
        """ Number of times. """
        return len(self.times)

    @property
    def pulses(self) -> list[Perturbation]:
        """ Pulses with which density matrices are convoluted. """
        return self._pulses

    def __str__(self) -> str:
        lines = ['Response from density matrices on disk']

        lines.append('')
        lines.append(f'Format string: {self.pulserho_fmt}')
        lines.append(f'Calculating response for {self.nt} times and {len(self.pulses)} pulses')
        lines.append(f'  times: {format_times(self.times)}')
        npartt = len(self._part_time_t)
        if npartt > 0:
            lines.append(f'Additionally {npartt} times are available for some '
                         'pulses/derivatives only')
            lines.append(f'  times: {format_times(self._part_time_t)}')

        return '\n'.join(lines)

    def read(self,
             time: float,
             pulse: Perturbation,
             derivative: int) -> NDArray[np.complex128]:
        r""" Read single density matrix from disk.

        Parameters
        ----------
        time
            Simulation time in units of as.
        pulse
            Pulse which this density matrix is in response to.
        derivative
            Read derivative of this order.

        Returns
        -------
        Density matrix :math:`\rho_ia`.
        """

        tag_s = ['', '-Iomega', '-omega2']

        fname_kw = dict(time=time, tag=tag_s[derivative],
                        **get_gaussian_pulse_values(pulse))
        fname = self.pulserho_fmt.format(**fname_kw)

        rho = read_numpy(fname)
        if len(rho.shape) == 1:
            # Transform from ravelled form
            rho_ia = self.ksd.M_ia_from_M_p(rho)
        else:
            rho_ia = rho

        return rho_ia


class FrequencyDensityMatrixReader:

    """ Finds density matrices in the frequency domain saved to disk and reads them.

    Parameters
    ----------
    frho_fmt
        Formatting string for the density matrices
        in frequency space saved to disk.

        The formatting string should be a plain string containing variable
        placeholders within curly brackets ``{}``. It should not be confused with
        a formatted string literal (f-string).

        Example:

         * frho_fmt = ``frho/w{freq:05.2f}-{reim}.npy``.

        Accepts variables:

         * ``{freq}`` - Frequency in units of eV.
         * ``{reim}`` - ``'Re'`` or ``'Im'`` for Fourier transform of real/imaginary
           part of density matrix.
    ksd
        KohnShamDecomposition object or file name to the ksd file.
    filter_frequencies
        Look for these frequencies (or as close to them as possible). In units of eV.
    log
        Logger object.
    """

    def __init__(self,
                 frho_fmt: str,
                 ksd: str | KohnShamDecomposition,
                 filter_frequencies: ArrayLike | None = None,
                 real: bool = True,
                 imag: bool = True,
                 log: Logger | None = None,
                 comm: Communicator | None = None):
        if log is None:
            log = Logger()
        self._log = log
        if isinstance(ksd, KohnShamDecomposition):
            self._ksd = ksd
        else:
            self._ksd = KohnShamDecomposition(filename=ksd)
            add_fake_kpts(self._ksd)

        self._comm = world if comm is None else comm
        self.frho_fmt = frho_fmt
        if not real and not imag:
            raise ValueError('At least one of real or imag must be true')
        reim_r = ['Re'] if real else []
        reim_r += ['Im'] if imag else []

        if self.comm.rank == 0:
            # Look for files on the root rank

            nested_freqs: list[Array1D[np.float64]] = []
            for reim in reim_r:
                # Partially format the format string, i.e. fill out the pulsefreq,
                # pulsefwhm, and tag fields
                fmt = partial_format(frho_fmt, reim=reim)

                # Search the file tree for files
                f = find_files(fmt, expected_keys=['freq'])
                nested_freqs.append(f['freq'])

        self._freq_w, self._part_freq_w = extract_common(nested_freqs if self.comm.rank == 0 else None,
                                                         filter_frequencies,
                                                         self.comm)

    @property
    def ksd(self) -> KohnShamDecomposition:
        """ Kohn-Sham decomposition object. """
        return self._ksd

    @property
    def comm(self) -> Communicator:
        """ MPI communicator. """
        return self._comm

    @property
    def log(self) -> Logger:
        """ Logger object. """
        return self._log

    @property
    def frequencies(self) -> Array1D[np.float64]:
        """ Frequencies in units of eV. """
        return self._freq_w

    @property
    def nw(self) -> int:
        """ Number of frequencies. """
        return len(self.frequencies)

    def __str__(self) -> str:
        lines = ['Response from Fourier transform of density matrices on disk']

        lines.append('')
        lines.append(f'Format string: {self.frho_fmt}')
        lines.append(f'Calculating response for {self.nw} frequencies')
        lines.append(f'  frequencies: {format_frequencies(self.frequencies)}')
        npartw = len(self._part_freq_w)
        if npartw > 0:
            lines.append(f'Additionally {npartw} frequencies are available for real '
                         'or imaginary parts but not both')
            lines.append(f'  frequencies: {format_frequencies(self._part_freq_w)}')

        return '\n'.join(lines)

    def read(self,
             frequency: float,
             real: bool) -> NDArray[np.complex128]:
        fname_kw = dict(freq=frequency, reim='Re' if real else 'Im')
        fname = self.frho_fmt.format(**fname_kw)

        rho = read_numpy(fname)

        if len(rho.shape) == 1 and self.ksd.only_ia:
            # Twice the rho is saved by the KohnShamDecomposition transform
            rho /= 2

        if len(rho.shape) == 1:
            # Transform from ravelled form
            rho_ia = self.ksd.M_ia_from_M_p(rho)
        else:
            rho_ia = rho

        return rho_ia


def read_numpy(fname: str) -> NDArray[np.complex128]:
    r""" Read density matrix from numpy binary file or archive.

    Supports data stored in non-ravelled form (preferred; indices :math:`ia`
    for electron-hole pairs) and in ravelled form (legacy; single index :math:`p`
    for electron-hole pairs).

    Parameters
    ----------
    fname
        File name.

    Returns
    -------
    Density matrix :math:`\rho_ia` or :math:`\rho_p`.
    """

    f = np.load(fname)
    if isinstance(f, np.lib.npyio.NpzFile):
        # Read npz file
        if 'rho_p' in f.files:
            rho = f['rho_p']
            if len(rho.shape) != 1:
                raise RuntimeError(f'Expected 1D array, got shape {rho.shape}.')
        elif 'rho_ia' in f.files:
            rho = f['rho_ia']
            if len(rho.shape) != 2:
                raise RuntimeError(f'Expected 2D array, got shape {rho.shape}.')
        else:
            raise RuntimeError("Expected file 'rho_p', or 'rho_ia' in file")
        f.close()
    else:
        # Read npy file
        assert isinstance(f, np.ndarray)
        rho = f
        if len(rho.shape) not in [1, 2]:
            raise RuntimeError(f'Expected 1D or 2D array, got shape {rho.shape}.')

    return rho


def extract_common(nested_values: list[Array1D[np.float64]] | None,
                   filter_values: ArrayLike | None,
                   comm: Communicator) -> tuple[Array1D[np.float64], Array1D[np.float64]]:
    """ From a list of arrays, extract array elements that are present in all arrays.

    Parameters
    ----------
    nested_values
        List of arrays on root rank, ``None`` on other ranks.
    filter_values
        Filter the values, keeping only the values closest to these.
    comm
        MPI communicator.

    Returns
    -------
    Tuple of values present in all arrays, and values present in at least one array. \
    Broadcast to all ranks.
    """
    if comm.rank == 0:
        assert nested_values is not None
        # Values present in all arrays
        values_any: set[float] = set(nested_values[0])
        # Values present in any array
        values_all: set[float] = set(values_any)

        for values in nested_values[1:]:
            values_any |= set(values)
            values_all &= set(values)

        # Filter the values
        values_any = set(filter_array(sorted(values_any), filter_values))  # type: ignore
        values_all = set(filter_array(sorted(values_all), filter_values))  # type: ignore

        # Values present in some arrays only
        values_some = values_any - values_all

        # Broadcast to all ranks
        shapes = np.array([len(values_all), len(values_some)], dtype=int)
    else:
        assert nested_values is None
        shapes = np.array([0, 0], dtype=int)

    comm.broadcast(shapes, 0)

    # Values in all arrays: as array
    array_all = np.zeros(shapes[0], dtype=float)
    # Values in some arrays: as array
    array_some = np.zeros(shapes[1], dtype=float)

    if comm.rank == 0:
        array_all[:] = sorted(values_all)
        array_some[:] = sorted(values_some)

    comm.broadcast(array_all, 0)
    if array_some.size > 0:
        comm.broadcast(array_some, 0)

    return array_all, array_some
