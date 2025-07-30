from __future__ import annotations

from typing import Any
from pathlib import Path
import numpy as np
from numpy.typing import NDArray

from ase.parallel import parprint
from gpaw.mpi import world
from gpaw.tddft.units import as_to_au, au_to_as, eV_to_au, au_to_eV, eA_to_au, au_to_eA
from gpaw.tddft.spectrum import read_dipole_moment_file

from .perturbation import create_perturbation, Perturbation, PerturbationLike, NoPerturbation


class SpectrumCalculator:

    r""" Spectrum calculator.

    Calculates the dynamic polarizability and dipole strength function (the spectrum).

    The polarizability :math:`\alpha(\omega)` is related to the perturbation
    :math:`\mathcal{E}(\omega)` and the Fouier transform of the dipole moment
    :math:`\boldsymbol\mu(t)` as

    .. math::

        \boldsymbol\alpha(\omega) \mathcal{E}(\omega) = \mathcal{F}[\boldsymbol\mu(t)](\omega).

    The dipole strength function is

    .. math::

        \boldsymbol{S}(\omega) = \frac{2}{\pi} \omega\:\mathrm{Im}[\boldsymbol\alpha(\omega)].

    Both quantities can be broadened by supplying a non-zero value :math:`\sigma`. Then the
    convolution

    .. math::

        \frac{1}{\sqrt{2\pi/\sigma^2}}
        \int_{-\infty}^{\infty} \boldsymbol\alpha(\omega')
        \exp\left(- \frac{(\omega - \omega')^2}{2\sigma^2}\right) \mathrm{d}\omega'

    is computed. When the perturbation is a delta-kick, this can efficiently be computed
    by multiplying the dipole moment by a Gaussian envelope before Fourier transformation

    .. math::

        \boldsymbol\mu(t) \exp(-\sigma^2 t^2 / 2).

    For other perturbations, a :term:`FFT` and :term:`IFFT` is first
    performed to obtain the delta-kick response.


    Parameters
    ----------
    times
        Array (length T) of times in units of as.
    dipole_moments
        Array (shape (T, 3)) of dipole moments in units of eÅ.
    perturbation
        The perturbation that was applied in the :term:`TDDFT` calculation.
    """

    def __init__(self,
                 times: NDArray[np.float64],
                 dipole_moments: NDArray[np.float64],
                 perturbation: PerturbationLike):
        time_t = np.array(times) * as_to_au
        dm_tv = np.array(dipole_moments) * eA_to_au
        dm_tv -= dm_tv[0]  # Remove static dipole

        # Remove duplicates due to stopped and restarted calculations, and delta kick
        flt_t = np.ones_like(time_t, dtype=bool)
        maxtime = time_t[0]
        for t in range(1, len(time_t)):
            if time_t[t] > maxtime:
                maxtime = time_t[t]
            else:
                flt_t[t] = False
        time_t = time_t[flt_t]
        dm_tv = dm_tv[flt_t]
        ndup = len(flt_t) - flt_t.sum()
        if ndup > 0:
            parprint(f'Removed {ndup} duplicates')

        # check time step
        dt_t = time_t[1:] - time_t[:-1]
        dt = dt_t[0]
        if not np.allclose(dt_t, dt, rtol=1e-6, atol=0):
            raise ValueError('Time grid must be equally spaced.')

        self._time_t = time_t
        self._dm_tv = dm_tv
        self._perturbation = create_perturbation(perturbation)

        if isinstance(self.perturbation, NoPerturbation):
            raise ValueError('A perturbation must be given')

    @property
    def times(self) -> NDArray[np.float64]:
        """ Array of times corresponding to dipole moments, in units of as. """
        return self._time_t * au_to_as

    @property
    def dipole_moments(self) -> NDArray[np.float64]:
        """ Array of dipole moments, in units of eÅ. """
        return self._dm_tv * au_to_eA

    @property
    def perturbation(self) -> Perturbation:
        """ The perturbation that was applied in the :term:`TDDFT` calculation. """
        return self._perturbation

    def _get_dynamic_polarizability(self,
                                    frequencies: list[float] | NDArray[np.float64],
                                    frequency_broadening: float = 0):
        """ Calculate the dynamic polarizability in atomic units.

        Parameters
        ----------
        frequencies
            Array of frequencies for which to calculate the polarizability; in atomic units.
        frequency_broadening
            Gaussian broadening width in atomic units. Default (0) is no broadening.

        Returns
        -------
        Array of dynamic polarizabilities in atomic units. \
        The array has shape (N, 3), where N is the length of :attr:`frequencies`.
        """
        dt = self._time_t[1] - self._time_t[0]
        nt = len(self._time_t)

        # Get a response equivalent to a unity-strength delta-kick
        dm_tv = self.perturbation.normalize_time_response(self._dm_tv, self._time_t, axis=0)

        if frequency_broadening == 0:
            # No broadening
            weight_t = np.ones_like(self._time_t)
        else:
            # Gaussian broadening
            weight_t = np.exp(-0.5 * frequency_broadening ** 2 * self._time_t**2)

        # integration weights from Simpson's integration rule
        weight_t *= dt / 3 * np.array([1] + [4, 2] * int((nt - 2) / 2)
                                      + [4] * (nt % 2) + [1])

        # transform
        exp_tw = np.exp(np.outer(1.0j * self._time_t, frequencies))
        dm_wv = np.einsum('t...,tw,t->w...', dm_tv, exp_tw, weight_t, optimize=True)

        return dm_wv

    def get_dynamic_polarizability(self,
                                   frequencies: list[float] | NDArray[np.float64],
                                   frequency_broadening: float = 0):
        """ Calculate the dynamic polarizability.

        Parameters
        ----------
        frequencies
            Array of frequencies for which to calculate the polarizability; in units of eV.
        frequency_broadening
            Gaussian broadening width in atomic units. Default (0) is no broadening.

        Returns
        -------
        Array of dynamic polarizabilities in (eÅ)**2/eV. \
        The array has shape (N, 3), where N is the length of :attr:`frequencies`.
        """

        dm_wv = self._get_dynamic_polarizability(np.array(frequencies) * eV_to_au,
                                                 frequency_broadening * eV_to_au)
        dm_wv = dm_wv * au_to_eA**2 / au_to_eV
        return dm_wv

    def _get_dipole_strength_function(self,
                                      frequencies: list[float] | NDArray[np.float64],
                                      frequency_broadening: float = 0):
        """ Calculate the dipole strength function (spectrum) in atomic units.

        Parameters
        ----------
        frequencies
            Array of frequencies for which to calculate the spectrum; in atomic units.
        frequency_broadening
            Gaussian broadening width in atomic units. Default (0) is no broadening.

        Returns
        -------
        Array of dipole strength function in atomic units. \
        The array has shape (N, 3), where N is length of frequencies.
        """
        freq_w = np.array(frequencies)
        pol_wv = self._get_dynamic_polarizability(frequencies, frequency_broadening)
        osc_wv = 2 / np.pi * freq_w[:, np.newaxis] * pol_wv.imag
        return osc_wv  # type: ignore

    def get_dipole_strength_function(self,
                                     frequencies: list[float] | NDArray[np.float64],
                                     frequency_broadening: float = 0):
        """ Calculate the dipole strength function (spectrum) in units of 1/eV.

        Parameters
        ----------
        frequencies
            Array of frequencies for which to calculate the spectrum; in units of eV.
        frequency_broadening
            Gaussian broadening width in units of eV. Default (0) is no broadening.

        Returns
        -------
        Array of dipole strength function in units of 1/eV. \
        The array has shape (N, 3), where N is length of frequencies.
        """
        osc_wv = self._get_dipole_strength_function(np.array(frequencies) * eV_to_au,
                                                    frequency_broadening * eV_to_au)
        osc_wv = osc_wv / au_to_eV
        return osc_wv

    @classmethod
    def from_file(cls,
                  dipolefile: str | Path,
                  perturbation: PerturbationLike) -> SpectrumCalculator:
        _, time_t, _, dm_tv = read_dipole_moment_file(str(dipolefile))
        return cls(time_t * au_to_as, dm_tv * au_to_eA, perturbation)

    def calculate_spectrum_and_write(self,
                                     out_fname: Path | str,
                                     frequencies: list[float] | NDArray[np.float64],
                                     frequency_broadening: float = 0,
                                     write_extra: dict[str, Any] = dict()):
        """ Calculate the dipole strength function (spectrum) and write to file.

        The spectrum is saved in a numpy archive if the file extension is ``.npz``
        or in a comma separated file if the file extension is ``.dat``.

        Parameters
        ----------
        out_fname
            File name of the resulting data file.
        frequencies
            Array of frequencies for which to calculate the spectrum; in units of eV.
        frequency_broadening
            Gaussian broadening width in units of eV. Default (0) is no broadening.
        write_extra
            Dictionary of additional data written to numpy archive (ignored for ``.dat``) files.
        """
        from .writers.spectrum import write_spectrum

        out_fname = str(out_fname)
        if world.rank > 0:
            world.barrier()
            return

        osc_wv = self.get_dipole_strength_function(frequencies, frequency_broadening)
        if out_fname[-4:] == '.npz':
            d = dict(freq_w=frequencies,
                     osc_wv=osc_wv,
                     frequency_broadening=frequency_broadening)
            d.update({f'perturbation_{key}': value
                      for key, value in self.perturbation.todict().items()})
            d.update(write_extra)
            np.savez_compressed(str(out_fname), **d)
        elif out_fname[-4:] == '.dat':
            write_spectrum(out_fname,
                           frequencies=frequencies,
                           spectrum=osc_wv,
                           frequency_broadening=frequency_broadening,
                           total_time=self.times[-1] - self.times[0],
                           timestep=self.times[1] - self.times[0],
                           perturbation=self.perturbation)
        else:
            raise ValueError(f'output-file must have ending .npz or .dat, is {out_fname}')

        print(f'Written {out_fname}', flush=True)
        world.barrier()
