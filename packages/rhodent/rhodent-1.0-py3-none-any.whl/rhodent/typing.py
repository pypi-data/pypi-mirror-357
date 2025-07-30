from __future__ import annotations
from typing import Union, TypeVar

import numpy as np
from numpy.typing import NDArray

from gpaw import mpi
from gpaw.calculator import GPAW

GPAWCalculator = GPAW
Communicator = mpi._Communicator
ArrayIndex = Union[NDArray[np.int_], list[int], int, slice]


DTypeT = TypeVar('DTypeT', bound=np.generic, covariant=True)


class ArrayIsOnRootRank(NDArray[DTypeT]):
    def __new__(cls):
        """ Instances will act as empty numpy arrays """
        return NDArray.__new__(cls, (0, ))


DistributedArray = Union[NDArray[DTypeT], ArrayIsOnRootRank]
Array1D = np.ndarray[tuple[int], np.dtype[DTypeT]]
Array2D = np.ndarray[tuple[int, int], np.dtype[DTypeT]]
Array3D = np.ndarray[tuple[int, int, int], np.dtype[DTypeT]]
