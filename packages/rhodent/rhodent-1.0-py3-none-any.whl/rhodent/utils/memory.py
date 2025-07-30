from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np
from numpy._typing import _DTypeLike as DTypeLike


@dataclass
class MemoryEntry:

    shape: tuple[int, ...]
    dtype: np.dtype
    on_num_ranks: int = 1
    total_size: int | None = None

    def get_total_size(self) -> int:
        """ Get the total number of elements on all ranks. """
        if self.total_size is not None:
            return self.total_size
        return int(np.prod(self.shape)) * self.on_num_ranks


@dataclass
class MemoryEstimate:

    comment: str = ''
    children: dict[str, MemoryEstimate] = field(default_factory=dict)
    arrays: dict[str, MemoryEntry] = field(default_factory=dict)

    def __str__(self) -> str:
        if len(self.children) == 0 and len(self.arrays) == 0:
            return 'Unknown'
        to_MiB = 1024 ** -2
        totalstr = f'{self.grand_total * to_MiB:.1f} MiB'

        lines = []
        if self.comment != '':
            lines += ['Note: ' + line for line in self.comment.split('\n')]
            lines.append('')

        for key, entry in self.arrays.items():
            size_per_rank_MiB = int(np.prod(entry.shape)) * entry.dtype.itemsize * to_MiB
            size_total_MiB = entry.get_total_size() * entry.dtype.itemsize * to_MiB

            lines.append(f'{key}: {entry.shape} {entry.dtype}')
            lines.append(f'. {size_per_rank_MiB:.1f} MiB '
                         f'per rank on {entry.on_num_ranks} ranks')
            lines.append(f'. {size_total_MiB:.1f} MiB in total on all ranks')
            lines.append('')

        for name, child in self.children.items():
            lines.append(f'{name}:')
            lines += ['    ' + line for line in str(child).split('\n')]
            lines.append('')
        lines.append(f'{"":.^24}')
        lines.append(f'{" Total on all ranks ":.^24}')
        lines.append(f'{totalstr:.^24}')

        return '\n'.join(lines)

    @property
    def grand_total(self) -> int:
        """ Grand total of bytes. """

        total = 0
        for entry in self.arrays.values():
            total += entry.get_total_size() * entry.dtype.itemsize

        for child in self.children.values():
            total += child.grand_total

        return total

    def add_key(self,
                key: str,
                shape: tuple[int, ...] | int = (),
                dtype: DTypeLike = float,
                *,
                total_size: int | None = None,
                on_num_ranks: int = 1):
        assert isinstance(key, str)
        if isinstance(shape, int):
            shape = (shape, )
        assert all([isinstance(d, (int, np.integer)) for d in shape])
        shape = tuple(int(d) for d in shape)
        assert isinstance(on_num_ranks, int)
        dtype = np.dtype(dtype)
        self.arrays[key] = MemoryEntry(shape, dtype,
                                       total_size=total_size,
                                       on_num_ranks=on_num_ranks)

    def add_child(self,
                  name: str,
                  child: MemoryEstimate):
        assert isinstance(child, MemoryEstimate)
        self.children[name] = child


class HasMemoryEstimate(ABC):

    """ Classes inheriting from this class are able to
    provide a memory estimate """

    @abstractmethod
    def get_memory_estimate(self) -> MemoryEstimate:
        raise NotImplementedError
