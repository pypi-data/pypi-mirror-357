from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Union
from numbers import Number
import numpy as np
from numpy.typing import NDArray

from gpaw.lcaotddft.laser import Laser, create_laser


def create_perturbation(perturbation: PerturbationLike):
    if isinstance(perturbation, Perturbation):
        return perturbation
    if perturbation is None:
        return NoPerturbation()
    if isinstance(perturbation, Laser):
        return PulsePerturbation(perturbation)

    assert isinstance(perturbation, dict)
    if perturbation['name'] == 'none':
        return NoPerturbation
    if perturbation['name'] == 'deltakick':
        return DeltaKick(strength=perturbation['strength'])
    pulse = create_laser(perturbation)
    return PulsePerturbation(pulse)


class Perturbation(ABC):

    """ Perturbation. """

    def timestep(self,
                 times: NDArray[np.float64]):
        if len(times) < 2:
            raise ValueError('At least two times must be given to get a timestep.')
        dt = times[1] - times[0]
        if not np.allclose(times[1:] - dt, times[:-1]):
            raise ValueError('The time step may not vary.')
        return dt

    def frequencies(self,
                    times: NDArray[np.float64],
                    padnt: int | None = None) -> NDArray[np.float64]:
        """ Get the frequencies grid.

        Parameters
        ----------
        times
            Time grid in atomic units.
        padnt
            Length of data, including zero padding. Default is not zero padding.

        Returns
        -------
        Frequencies grid in atomic units.
        """
        timestep = self.timestep(times)
        if padnt is None:
            padnt = len(times)
        return 2 * np.pi * np.fft.rfftfreq(padnt, timestep)

    @abstractmethod
    def normalize_frequency_response(self,
                                     data: NDArray[np.float64],
                                     times: NDArray[np.float64],
                                     padnt: int,
                                     axis: int = -1) -> NDArray[np.complex128]:
        """
        Calculate a normalized response in the frequency domain, i.e., the
        response to a unity strength delta kick. For example, polarizability.

        Parameters
        ----------
        data
            Real valued response in the time domain to this perturbation.
        times
            Time grid in atomic units.
        axis
            Axis corresponding to time dimension.
        padnt
            Length of data, including zero padding.

        Returns
        -------
        Normalized response in the frequency domain.
        """
        raise NotImplementedError

    def normalize_time_response(self,
                                data: NDArray[np.float64],
                                times: NDArray[np.float64],
                                axis: int = -1) -> NDArray[np.float64]:
        """
        Transform response in the time domain to a "normalized response",
        which is the response to a unity strength delta kick.

        Parameters
        ----------
        data
            Real valued response in the time domain to this perturbation.
        times
            Time grid in atomic units.
        axis
            Axis corresponding to time dimension.

        Returns
        -------
        Normalized response in the time domain.
        """
        from .utils import fast_pad

        dt = times[1] - times[0]
        nt = len(times)
        padnt = fast_pad(nt)

        data = data.swapaxes(axis, -1)  # Put the time dimension last

        # Calculate the normalized response in the frequency domain
        data_w = self.normalize_frequency_response(data, times, padnt, axis=-1)

        # Fourier transform back to time tomain
        data_t = np.fft.irfft(data_w, n=padnt, axis=-1)[..., :nt] / dt

        data_t = data_t.swapaxes(axis, -1)
        return data_t

    @abstractmethod
    def amplitude(self,
                  times: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        Perturbation amplitudes in time domain.

        Parameters
        ----------
        times
            Time grid in atomic units.

        Returns
        -------
        Perturbation at the given times.
        """
        raise NotImplementedError

    @abstractmethod
    def fourier(self,
                times: NDArray[np.float64],
                padnt: int | None = None) -> NDArray[np.complex128]:
        """
        Fourier transform of perturbation.

        Parameters
        ----------
        times
            Time grid in atomic units.
        padnt
            Length of data, including zero padding. Default is no added zero padding.

        Returns
        -------
        Fourier transform of the perturbation at the frequency grid \
        given by :func:`frequencies`.
        """
        raise NotImplementedError

    @abstractmethod
    def todict(self) -> dict[str, Any]:
        raise NotImplementedError

    def __eq__(self, other) -> bool:
        """ Equal if dicts are identical (up to numerical tolerance).
        """
        try:
            d1 = self.todict()
            d2 = other.todict()
        except AttributeError:
            return False

        if d1.keys() != d2.keys():
            return False

        for key in d1.keys():
            if isinstance(d1[key], Number) and isinstance(d2[key], Number):
                if not np.isclose(d1[key], d2[key]):
                    return False
            else:
                if not d1[key] == d2[key]:
                    return False

        return True


PerturbationLike = Union[Perturbation, Laser, dict, None]


class NoPerturbation(Perturbation):

    """ No perturbation

    Used to indicate that we do not know the perturbation,
    and that it should not matter.
    """

    def __init__(self):
        pass

    def amplitude(self,
                  times: NDArray[np.float64]) -> NDArray[np.float64]:
        raise RuntimeError('Not possible for no perturbation.')

    def fourier(self,
                times: NDArray[np.float64],
                padnt: int | None = None) -> NDArray[np.complex128]:
        raise RuntimeError('Not possible for no perturbation')

    def normalize_frequency_response(self,
                                     data: NDArray[np.float64],
                                     times: NDArray[np.float64],
                                     padnt: int,
                                     axis: int = -1) -> NDArray[np.complex128]:
        raise RuntimeError('Not possible for no perturbation')

    def __str__(self) -> str:
        return 'No perturbation'

    def todict(self) -> dict[str, Any]:
        return {'name': 'none'}


class DeltaKick(Perturbation):

    """ Delta-kick perturbation.

    Parameters
    ----------
    strength
        Strength of the perturbation in the frequency domain.
    """

    def __init__(self,
                 strength: float):
        self.strength = strength

    def amplitude(self,
                  times: NDArray[np.float64]) -> NDArray[np.float64]:
        dt = self.timestep(times)
        amplitudes = np.abs(times) < 1e-3 * dt   # 1 if zero, else 0

        return self.strength / dt * amplitudes

    def fourier(self,
                times: NDArray[np.float64],
                padnt: int | None = None) -> NDArray[np.complex128]:
        nw = len(self.frequencies(times, padnt))  # Length of frequencies grid
        return self.strength * np.ones(nw)  # type: ignore

    def normalize_frequency_response(self,
                                     data: NDArray[np.float64],
                                     times: NDArray[np.float64],
                                     padnt: int,
                                     axis: int = -1) -> NDArray[np.complex128]:
        data_w = np.fft.rfft(data, n=padnt) * self.timestep(times)
        # The strength is specified in the frequency domain, so the timestep is included in strength
        return data_w / self.strength

    def normalize_time_response(self,
                                data: NDArray[np.float64],
                                times: NDArray[np.float64],
                                axis: int = -1) -> NDArray[np.float64]:
        # The strength is specified in the frequency domain, hence no multiplication by timestep
        return data / self.strength  # type: ignore

    def todict(self) -> dict[str, Any]:
        return {'name': 'deltakick', 'strength': self.strength}

    def __str__(self) -> str:
        return f'Delta-kick perturbation (strength {self.strength:.1e})'


class PulsePerturbation(Perturbation):

    """ Perturbation as a time-dependent function.

    Parameters
    ----------
    pulse
        Object representing the pulse.
    """

    def __init__(self,
                 pulse: Laser | dict):
        self.pulse = create_laser(pulse)

    def amplitude(self,
                  times: NDArray[np.float64]) -> NDArray[np.float64]:
        return self.pulse.strength(times)

    def fourier(self,
                times: NDArray[np.float64],
                padnt: int | None = None) -> NDArray[np.complex128]:
        pulse_t = self.amplitude(times)
        if padnt is None:
            padnt = len(times)
        return np.fft.rfft(pulse_t, n=padnt) * self.timestep(times)

    def normalize_frequency_response(self,
                                     data: NDArray[np.float64],
                                     times: NDArray[np.float64],
                                     padnt: int,
                                     axis: int = -1) -> NDArray[np.complex128]:
        data = data.swapaxes(axis, -1)  # Put the time dimension last
        thresh = 0.005  # Threshold for filtering where perturbation is zero

        # Fourier transform of perturbation
        perturb_t = self.pulse.strength(times)
        perturb_w = np.fft.rfft(perturb_t, n=padnt)

        # Fourier transform of data
        data_w = np.fft.rfft(data, n=padnt)

        # Mask where perturbation is below threshold
        flt_w = np.abs(perturb_w) > thresh * np.abs(perturb_w).max()
        data_w[..., ~flt_w] = 0

        # Divide by the perturbation
        data_w[..., flt_w] /= perturb_w[flt_w]

        # Move back the time/frequency dimension
        data_w = data_w.swapaxes(axis, -1)

        return data_w

    def todict(self) -> dict[str, Any]:
        try:
            return self.pulse.todict()
        except AttributeError:
            return {'name': self.pulse.__class__.__name__}

    def __str__(self) -> str:
        lines: list[str] = []
        width = 50
        for key, value in self.todict().items():
            line = f'{key}: {value}'
            if len(lines) == 0:
                lines.append(line)
                continue
            if len(lines[-1]) + len(line) + 2 < width:
                lines[-1] = lines[-1] + ', ' + line
            else:
                lines.append(line)
        return '\n'.join(lines)
