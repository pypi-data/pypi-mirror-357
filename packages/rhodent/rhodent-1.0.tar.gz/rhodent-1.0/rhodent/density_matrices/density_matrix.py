from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from gpaw.mpi import broadcast, world, SerialCommunicator
from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition

from ..typing import ArrayIsOnRootRank, DistributedArray, Communicator


class DensityMatrix:

    """ Wrapper for the density matrix in the Kohn-Sham basis at one moment
    in time or at one frequency.

    The plain density matrix and/or derivatives thereof may be stored.

    Parameters
    ----------
    ksd
        KohnShamDecomposition object.
    matrices
        Dictionary mapping derivative orders (0, 1, 2) for zeroth,
        first, second derivative, .. to arrays storing the matrices.
    comm
        MPI communicator. Serial communicator by default.
    """

    def __init__(self,
                 ksd: KohnShamDecomposition,
                 matrices: dict[int, NDArray[np.complex128] | None],
                 comm: Communicator | None = None):
        self._ksd = ksd
        if comm is None:
            comm = SerialCommunicator()  # type: ignore
        self._comm = comm

        # Calculate occupation number difference
        f_n = self.ksd.occ_un[0]
        imin, imax, amin, amax = self.ksd.ialims()
        self._f_ia = f_n[imin:imax+1, None] - f_n[None, amin:amax+1]
        self._f_ia[self._f_ia < 0] = 0

        # Calculate mask
        min_occdiff = min(self.ksd.f_p)
        mask_ia = self.f_ia >= min_occdiff

        self._matrices: dict[int, DistributedArray] = dict()
        self.derivative_desc = {0: 'Plain DM', 1: '1st DM derivative', 2: '2nd DM derivative'}

        # Save the matrices
        for derivative, rho in matrices.items():
            assert isinstance(derivative, int)
            if self.rank == 0:
                assert isinstance(rho, np.ndarray), rho
                self._matrices[derivative] = rho * mask_ia
            else:
                assert rho is None
                self._matrices[derivative] = ArrayIsOnRootRank()

    @property
    def ksd(self) -> KohnShamDecomposition:
        """ Kohn-Sham decomposition object. """
        return self._ksd

    @property
    def rank(self) -> int:
        """ MPI rank of the communicator. """
        return self.comm.rank

    @property
    def comm(self) -> Communicator:
        return self._comm  # type: ignore

    @property
    def f_ia(self) -> DistributedArray:
        """ Occupation number difference :math:`f_{ia}`. """
        return self._f_ia

    @property
    def rho_ia(self) -> DistributedArray:
        r""" Electron-hole part of induced density matrix :math:`\delta rho_{ia}`. """
        try:
            return self._matrices[0]
        except KeyError:
            raise ValueError('Plain density matrix not in {self._matrices.keys()}')

    @property
    def drho_ia(self) -> DistributedArray:
        r""" First time derivative of :math:`\delta rho_{ia}`. """
        try:
            return self._matrices[1]
        except KeyError:
            raise ValueError('First derivative of density matrix not in {self._matrices.keys()}')

    @property
    def ddrho_ia(self) -> DistributedArray:
        r""" Second time derivative of :math:`\delta rho_{ia}`. """
        try:
            return self._matrices[2]
        except KeyError:
            raise ValueError('Second derivative of density matrix not in {self._matrices.keys()}')

    @property
    def Q_ia(self) -> DistributedArray:
        r""" The quantity

        .. math::
            Q_{ia} = \frac{2 \mathrm{Re}\:\delta\rho_{ia}}{\sqrt{2 f_{ia}}}

        where :math:`f_{ia}` is the occupation number difference of pair :math:`ia`.
        """
        return self._divide_by_sqrt_fia(np.sqrt(2) * self.rho_ia.real)

    @property
    def P_ia(self) -> DistributedArray:
        r""" The quantity

        .. math::
            P_{ia} = \frac{2 \mathrm{Im}\:\delta\rho_{ia}}{\sqrt{2 f_{ia}}}

        where :math:`f_{ia}` is the occupation number difference of pair :math:`ia`.
        """
        return self._divide_by_sqrt_fia(np.sqrt(2) * self.rho_ia.imag)

    @property
    def dQ_ia(self) -> DistributedArray:
        r""" First time derivative of :math:`Q_{ia}`. """
        return self._divide_by_sqrt_fia(np.sqrt(2) * self.drho_ia.real)

    @property
    def dP_ia(self) -> DistributedArray:
        r""" First time derivative of :math:`P_{ia}`. """
        return self._divide_by_sqrt_fia(np.sqrt(2) * self.drho_ia.imag)

    @property
    def ddQ_ia(self) -> DistributedArray:
        r""" Second time derivative of :math:`Q_{ia}`. """
        return self._divide_by_sqrt_fia(np.sqrt(2) * self.ddrho_ia.real)

    @property
    def ddP_ia(self) -> DistributedArray:
        r""" Second time derivative of :math:`P_{ia}`. """
        return self._divide_by_sqrt_fia(np.sqrt(2) * self.ddrho_ia.imag)

    def _divide_by_sqrt_fia(self,
                            X_ia: DistributedArray) -> DistributedArray:
        r""" Divide by :math:`\sqrt{f_{ia}}` where :math:`f_{ia} \neq 0`.
        Leave everything else as 0."""
        if self.rank > 0:
            assert isinstance(X_ia, ArrayIsOnRootRank)
            return ArrayIsOnRootRank()
        assert not isinstance(X_ia, ArrayIsOnRootRank)
        flt_ia = self.f_ia != 0
        Y_ia = np.zeros_like(X_ia)
        Y_ia[flt_ia] = X_ia[flt_ia] / np.sqrt(self.f_ia[flt_ia])

        return Y_ia

    def copy(self) -> DensityMatrix:
        """ Copy the density matrix. """
        matrices: dict[int, NDArray[np.complex128] | None] = {
            derivative: np.array(matrix) for derivative, matrix in self._matrices.items()}
        dm = DensityMatrix(ksd=self.ksd, matrices=matrices, comm=self.comm)
        return dm

    @classmethod
    def broadcast(cls,
                  density_matrix: DensityMatrix | None,
                  ksd: KohnShamDecomposition,
                  root: int,
                  dm_comm,
                  comm) -> DensityMatrix:
        """ Broadcast a density matrix object which is on one rank to all other ranks.

        Parameters
        ----------
        density_matrix
            The density matrix to be broadcast on the root rank, and ``None`` on other ranks.
        ksd
            KohnShamDecomposition object.
        root
            Rank of the process that has the original data.
        dm_comm
            Must be identical to communicator of :attr:`density_matrix`.
        comm
            MPI communicator. Must be complementary to the communicator of :attr:`density_matrix`.
        """
        matrices: dict[int, NDArray[np.complex128] | None]
        # Broadcast necessary metadata
        if comm.rank == root:
            assert density_matrix is not None
            matrix_shapes_dtypes = {derivative: (matrix.shape, matrix.dtype)
                                    for derivative, matrix in density_matrix._matrices.items()}
            broadcast(matrix_shapes_dtypes, root=root, comm=comm)
            matrices = {derivative: None if isinstance(arr, ArrayIsOnRootRank) else arr
                        for derivative, arr in density_matrix._matrices.items()}
        else:
            assert density_matrix is None
            matrix_shapes_dtypes = broadcast(None, root=root, comm=comm)

        if comm.rank != root:
            if dm_comm.rank == 0:
                matrices = {derivative: np.empty(shape, dtype=dtype)
                            for derivative, (shape, dtype) in matrix_shapes_dtypes.items()}
            else:
                matrices = {derivative: None
                            for derivative, (shape, dtype) in matrix_shapes_dtypes.items()}

        if dm_comm.size > 1 and comm.size > 1:
            # Make sure communicators are complementary
            comm_members = comm.get_members()
            dm_members = dm_comm.get_members()

            intersect = set(comm_members) & set(dm_members)
            intersect.remove(world.rank)
            assert len(intersect) == 0, f'{comm_members} / {dm_members}'

        # On density matrix non-root ranks, return ArrayIsOnRootRank()
        if dm_comm.rank > 0:
            return DensityMatrix(ksd=ksd, matrices=matrices, comm=dm_comm)

        # Broadcast the matrices
        for derivative, matrix in matrices.items():
            comm.broadcast(np.ascontiguousarray(matrix), root)

        if comm.rank == root:
            assert density_matrix is not None
            return density_matrix
        else:
            return DensityMatrix(ksd=ksd, matrices=matrices, comm=dm_comm)
