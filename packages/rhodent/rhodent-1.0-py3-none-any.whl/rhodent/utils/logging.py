from __future__ import annotations

import os
import sys
import time

import numpy as np

import ase
import gpaw
from gpaw.mpi import world
from gpaw.tddft.units import au_to_eV, au_to_as

from .. import __version__
from ..typing import Communicator

ascii_icon = r"""
                ###     #####
               ###############
         ########  #####     ##
     ###########            ###
  #######                  ###
 ####                      ##
 #                          ##
 #                           ##
 #                            ##
 #                             ##
 ##                             ###
  ####                           ###
   ##########                     ##
      ########                   ###
            ###                ####
            ##               ####
            ##           ######
            #################
"""


ascii_logo = r"""
      _               _            _
 _ __| |__   ___   __| | ___ _ __ | |_
| '__| '_ \ / _ \ / _` |/ _ \ '_ \| __|
| |  | | | | (_) | (_| |  __/ | | | |_
|_|  |_| |_|\___/ \__,_|\___|_| |_|\__|
"""


class Logger:

    """ Logger

    Parameters
    ----------
    t0
        Start time (default is current time).
    """
    _t0: float
    _starttimes: dict[str, float]

    def __init__(self,
                 t0: float | None = None):
        self._starttimes = dict()
        if t0 is None:
            self._t0 = time.time()
        else:
            assert isinstance(t0, float)
            self._t0 = t0
        self._time_of_last_log = self._t0

    @property
    def t0(self) -> float:
        return self._t0

    @t0.setter
    def t0(self,
           value: float | None):
        if value is None:
            self._t0 = time.time()
            return
        assert isinstance(value, float)
        self._t0 = value

    def __getitem__(self, key) -> float:
        return self._starttimes.get(key, self.t0)

    def __call__(self,
                 *args,
                 who: str | None = None,
                 rank: int | None = None,
                 if_elapsed: float = 0,
                 comm: Communicator | None = None,
                 **kwargs):
        """ Log message.

        Parameters
        ----------
        rank
            Only log if rank is :attr:`rank`. ``None`` to always log.
        who
            Sender of the message.
        comm
            Communicator. If included, rank and size is included in the message.
        if_elapsed
            Only log if :attr:`if_elapsed` seconds have passed since last logged message.
        """

        myrank = world.rank if comm is None else comm.rank
        if rank is not None and myrank != rank:
            return
        if time.time() < self._time_of_last_log + if_elapsed:
            return
        if comm is not None and comm.size > 1:
            commstr = f'{comm.rank:04.0f}/{comm.size:04.0f}'
            who = commstr if who is None else f'{who} {commstr}'
        _args = list(args)
        if who is not None:
            _args.insert(0, f'[{who}]')
        return self.log(*_args, **kwargs)

    def __str__(self) -> str:
        s = f'{self.__class__.__name__} t0: {self.t0}'
        return s

    def log(self, *args, **kwargs):
        """ Log message, prepending a timestamp. """
        self._time_of_last_log = time.time()
        hh, rem = divmod(self._time_of_last_log - self.t0, 3600)
        mm, ss = divmod(rem, 60)
        timestr = f'[{hh:02.0f}:{mm:02.0f}:{ss:04.1f}]'
        print(f'{timestr}', *args, **kwargs)

    def start(self, key):
        self._starttimes[key] = time.time()

    def elapsed(self, key) -> float:
        return time.time() - self[key]

    def startup_message(self):
        """ Print a start up message. """
        if world.rank != 0:
            return

        # Piece together logotype and version number
        logo_lines = ascii_logo.split('\n')
        width = max(len(line) for line in logo_lines) + 2
        i = -2
        logo_lines[i] += (width - len(logo_lines[i])) * ' '  # Pad to width
        logo_lines[i] += __version__

        # Piece together icon and logotype
        lines = ascii_icon.split('\n')
        width = max(len(line) for line in lines)

        for i, logoline in enumerate(logo_lines, start=3):
            line = lines[i]
            line += (width - len(line)) * ' '  # Pad to same length
            lines[i] = line + logoline

        print('\n'.join(lines))
        print('Date:  ', time.asctime())
        print('CWD:   ', os.getcwd())
        print('cores: ', world.size)
        print('Python: {}.{}.{}'.format(*sys.version_info[:3]))
        print(f'numpy:  {os.path.dirname(np.__file__)} (version {np.version.version})')
        print(f'ASE:    {os.path.dirname(ase.__file__)} (version {ase.__version__})')
        print(f'GPAW:   {os.path.dirname(gpaw.__file__)} (version {gpaw.__version__})')
        print(flush=True)


class NoLogger(Logger):

    def __str__(self) -> str:
        return self.__class__.__name__

    def log(self, *args, **kwargs):
        pass


def format_times(times: np.typing.ArrayLike,
                 units: str = 'as') -> str:
    """ Write a short list of times for pretty priting.

    Parameters
    ----------
    times
        List of times in units of :attr:`units`.
    units
        Units of the supplied times.

         * ``au`` - atomic units
         * ``as`` - attoseconds

    Returns
    -------
    Formatted list of times in units of as.
    """
    times = np.array(times)
    if units == 'au':
        times *= au_to_as
    elif units != 'as':
        raise ValueError(f'Unknown units {units}. Must be "au" or "as".')
    if len(times) < 5:
        # Print all times
        timesstrings = [f'{time:.1f}' for time in times]
    else:
        timesstrings = [f'{time:.1f}' for time in times[[0, 1, 2, -1]]]
        timesstrings.insert(-1, '...')
    timesstrings[-1] += ' as'
    return ', '.join(timesstrings)


def format_frequencies(frequencies: np.typing.ArrayLike,
                       units: str = 'eV') -> str:
    """ Write a short list of frequencies for pretty priting.

    Parameters
    ----------
    frequencies
        List of frequencies in units of :attr:`units`.
    units
        Units of the supplied frequencies.

         * ``au`` - atomic units
         * ``eV`` - electron volts

    Returns
    -------
    Formatted list of times in units of as.
    """
    frequencies = np.array(frequencies)
    if units == 'au':
        frequencies *= au_to_eV
    elif units != 'eV':
        raise ValueError(f'Unknown units {units}. Must be "au" or "eV".')

    if len(frequencies) < 5:
        # Print all frequencies
        freqsstrings = [f'{freq:.1f}' for freq in frequencies]
    else:
        freqsstrings = [f'{freq:.1f}' for freq in frequencies[[0, 1, 2, -1]]]
        freqsstrings.insert(-1, '...')
    freqsstrings[-1] += ' eV'
    return ', '.join(freqsstrings)
