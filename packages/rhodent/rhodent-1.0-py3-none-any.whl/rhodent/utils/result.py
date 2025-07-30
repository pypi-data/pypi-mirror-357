from __future__ import annotations

import numpy as np
from numpy.typing import NDArray, DTypeLike

from typing import Iterator


class ResultKeys():

    """ List of result keys.

    """

    _keys_dimensions_dtypes: dict[str, tuple[tuple[int, ...], np.dtype]]

    def __init__(self,
                 *scalar_keys):
        self._keys_dimensions_dtypes = dict()

        for key in scalar_keys:
            self.add_key(key, (), float)

    def add_key(self,
                key: str,
                shape: tuple[int, ...] | int = (),
                dtype: DTypeLike = float):
        """ Add a new result key.

        Parameters
        ----------
        key
            Name of result.
        shape
            Shape of result (at one time or frequency instance). Default is scalar.
        dtype
            Result dtype.
        """

        assert isinstance(key, str)
        if isinstance(shape, int):
            shape = (shape, )
        assert all([isinstance(d, int) for d in shape])
        dtype = np.dtype(dtype)
        self._keys_dimensions_dtypes[key] = (shape, dtype)

    def remove(self,
               key: str):
        assert key in self
        self._keys_dimensions_dtypes.pop(key)

    def __contains__(self,
                     key: str) -> bool:
        return key in self._keys_dimensions_dtypes.keys()

    def __iter__(self) -> Iterator[tuple[str, tuple[int, ...], np.dtype]]:
        for key, (shape, dtype) in self._keys_dimensions_dtypes.items():
            yield key, shape, dtype

    def __getitem__(self,
                    key: str) -> tuple[tuple[int, ...], np.typing.DTypeLike]:
        assert key in self._keys_dimensions_dtypes, f'Key {key} not among keys'
        return self._keys_dimensions_dtypes[key]

    def __copy__(self):
        cpy = ResultKeys()
        cpy._keys_dimensions_dtypes.update(self._keys_dimensions_dtypes)
        return cpy


class Result:

    """ Class holding results.

    """

    _data: dict[str, NDArray[np.float64]]

    def __init__(self,
                 mutable: bool = False):
        self._data = dict()
        self._mutable = mutable

    def __contains__(self,
                     key: str) -> bool:
        return key in self._data

    def __setitem__(self,
                    key: str,
                    value: np.typing.ArrayLike | int):
        if not self._mutable:
            assert key not in self._data, f'Key {key} is already among results'
        if np.ndim(value) == 0:
            value = np.array([value])
        self._data[key] = np.ascontiguousarray(value)

    def __getitem__(self,
                    key: str) -> NDArray[np.float64]:
        assert key in self._data, f'Key {key} not among results'
        return self._data[key]

    def __str__(self) -> str:
        lines = [f'{self.__class__.__name__} with arrays (dimensions)']

        for key, data in self._data.items():
            lines.append(f'  {key} {data.shape}')

        return '\n'.join(lines)

    def set_to(self,
               key: str,
               idx,
               value: np.typing.ArrayLike | int | float):
        if np.ndim(self._data[key][idx]) == 0:
            assert np.size(value) == 1
            value = np.atleast_1d(value)[0]
        self._data[key][idx] = value

    def add_to(self,
               key: str,
               idx,
               value: np.typing.ArrayLike | int | float):
        if np.ndim(self._data[key][idx]) == 0:
            assert np.size(value) == 1
            value = np.atleast_1d(value)[0]
        self._data[key][idx] += value

    def create_all_empty(self,
                         keys: ResultKeys):
        for key, shape, dtype in keys:
            if key in self:
                continue
            self[key] = np.empty(shape, dtype=dtype)

    def create_all_zeros(self,
                         keys: ResultKeys):
        for key, shape, dtype in keys:
            if key in self:
                continue
            self[key] = np.zeros(shape, dtype=dtype)

    def remove(self,
               key: str):
        assert key in self._data
        self._data.pop(key)

    def empty(self,
              key: str,
              keys: ResultKeys):
        shape, dtype = keys[key]
        self[key] = np.empty(shape, dtype=dtype)

    def assert_keys(self,
                    keys: ResultKeys):
        copy = dict(self._data)
        try:
            for key, shape, dtype in keys:
                array = copy.pop(key)
                if len(shape) == 0:
                    assert array.shape == (1, ), f'{array.shape} != (1,)'
                else:
                    assert array.shape == shape, f'{array.shape} != {shape}'
                assert array.dtype == dtype, f'{array.dtype} != {dtype}'
        except KeyError:
            raise AssertionError(f'Key {key} missing from Result')
        assert len(copy) == 0, f'Result has additional keys {copy.keys()}'

    def send(self,
             keys: ResultKeys,
             rank,
             comm):
        self.assert_keys(keys)
        for vi, (key, _, _) in enumerate(keys):
            value = self._data[key]
            comm.send(value, rank, tag=100 + vi)

    def inplace_receive(self,
                        keys: ResultKeys,
                        rank: int,
                        comm):
        self.assert_keys(keys)
        for vi, (key, _, _) in enumerate(keys):
            value = self._data[key]
            comm.receive(value, rank, tag=100 + vi)
