from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterator, Sequence, Union

import numpy as np
from numpy.typing import NDArray

from gpaw import GPAW
from gpaw.analyse.wignerseitz import wignerseitz
from gpaw.io import Writer
from gpaw.mpi import broadcast, world
from gpaw.utilities.tools import tri2full

from .utils import Logger, parulmopen, ParallelMatrix
from .typing import Communicator, GPAWCalculator


AtomProjectionsType = Sequence[Union[list[int], NDArray[np.float64]]]  # | breaks on py3.9


class VoronoiWeights(ABC):

    """ Abstract base class for Voronoi weights in Kohn-Sham basis. """

    def __init__(self,
                 comm: Communicator | None = None,
                 log: Logger | None = None):
        if comm is None:
            comm = world
        if log is None:
            log = Logger()

        self._comm = comm
        self._log = log

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        pass

    def __len__(self) -> int:
        """ Number of projections. """
        return self.nproj

    @abstractmethod
    def __iter__(self) -> Iterator[NDArray[np.float64] | None]:
        """ Iteratively yield Voronoi weights for each projection.

        Yields
        ------
        Matrix of Voronoi weights on root rank, ``None`` on other ranks.
        """
        raise NotImplementedError

    def __str__(self) -> str:
        lines = [f'{self.__class__.__name__} for ground state with {self.nn} bands',
                 f'{self.nproj} projections:']

        for i, atoms in enumerate(self.atom_projections):
            atomsstr = str(atoms)
            if len(atomsstr) > 50:
                atomsstr = atomsstr[:47] + '...'
            lines.append(f'  #{i:<3.0f}: On atoms {atomsstr}')

        return '\n'.join(lines)

    @property
    def root(self) -> bool:
        """ Whether this rank is the root rank. """
        return self.comm.rank == 0

    @property
    def log(self) -> Logger:
        """ Logger object. """
        return self._log

    @property
    @abstractmethod
    def atom_projections(self) -> AtomProjectionsType:
        """ Atom projections. """
        raise NotImplementedError

    @property
    @abstractmethod
    def nn(self) -> int:
        """ Number of bands. """
        raise NotImplementedError

    @property
    def nproj(self) -> int:
        """ Number of projections. """
        return len(self.atom_projections)

    @property
    def comm(self) -> Communicator:
        """ MPI Communicator. """
        return self._comm

    @property
    @abstractmethod
    def saved_fields(self) -> dict[str, Any]:
        """ Saved data fields associated with the object.

        If this object is read from a ULM file there might be some extra
        data in that file. Return that data, or an empty dict if there is none.
        """
        raise NotImplementedError


class VoronoiWeightCalculator(VoronoiWeights):

    r"""Calculate Voronoi weights in the basis of ground state Kohn-Sham orbitals.

    For each atomic projection, calculates

    .. math::

        W_{nn'}
        = \left<\psi_n | \hat{w} | \psi_{n'}\right>
        = \left<\tilde{\psi}_n | \hat{w} | \tilde{\psi}_{n'}\right>
        + \sum_{aij} \left<\tilde{\psi}_n | \tilde{p}_i^a\right>
        \Delta S_{ij}^a \left<\tilde{p}_i^a | \tilde{\psi}_{n'}\right>

    where the operator :math:`\hat{w} = w(\vec{r})` is 1 in the
    Voronoi region of atoms and 0 outside.
    The sum over atoms is restricted to atoms in the region :math:`w(\vec{r}) = 1`.

    The PAW projectors

    .. math::

        P_{ni}^a = \left<\tilde{p}_i^a | \tilde{\psi}_n \right>

    and overlap matrix

    .. math::

        \Delta S_{ij}^a
        = \left<\phi_i^a|\phi_j^a\right>
        - \left<\tilde{\phi}_i^a|\tilde{\phi}_j^a\right>

    are obtained from the GPAW calculator and the smooth weight matrix is obtained by
    a basis change of the smooth LCAO weights

    .. math::

        \left<\tilde{\psi}_n | \hat{w} | \tilde{\psi}_{n'}\right> =
        \sum_{\mu\nu} C_{n\mu} C_{n'\nu}
        \left<\tilde{\phi}_\mu | \hat{w} | \tilde{\phi}_{\nu}\right>.

    Parameters
    ----------
    voronoi_lcao
        Object that calculates or loads the LCAO weights from file.
    """

    _voronoi_lcao: VoronoiLCAOWeights

    def __init__(self,
                 voronoi_lcao: VoronoiLCAOWeights):
        assert isinstance(voronoi_lcao, VoronoiLCAOWeights)
        self._voronoi_lcao = voronoi_lcao

        super().__init__(comm=voronoi_lcao.comm, log=voronoi_lcao.log)

    def __iter__(self) -> Iterator[NDArray[np.float64] | None]:
        for proj_atoms, weight_MM in zip(self.atom_projections, self.voronoi_lcao):
            nM = self.voronoi_lcao.nM
            nn = self.voronoi_lcao.nn

            # Transform to KS basis C_nM @ weight_MM @ C_nM.T
            w_MM = ParallelMatrix((nM, nM), np.float64, comm=self.comm,
                                  array=weight_MM)
            C_nM = ParallelMatrix((nn, nM), np.float64, comm=self.comm,
                                  array=self.voronoi_lcao.C_nM)

            _v_nn = C_nM @ w_MM @ C_nM.T
            self.log('Transformed weights to KS basis', flush=True, who='Voronoi', rank=0)

            # Calculate PAW corrections on the root rank
            if self.root:
                dS_aii = self.voronoi_lcao.dS_aii
                P_ani = self.voronoi_lcao.P_ani
                v_nn = _v_nn.array
                assert dS_aii is not None
                assert P_ani is not None

                for a, P_ni in P_ani.items():
                    if a not in proj_atoms:
                        continue
                    v_nn += P_ni @ dS_aii[a] @ P_ni.T

                self.log('Added PAW corrections to weights', flush=True, who='Voronoi', rank=0)

                yield v_nn
            else:
                yield None

    @property
    def voronoi_lcao(self) -> VoronoiLCAOWeights:
        return self._voronoi_lcao

    @property
    def atom_projections(self) -> AtomProjectionsType:
        return self.voronoi_lcao.atom_projections

    @property
    def nn(self) -> int:
        return self.voronoi_lcao.nn

    @property
    def nM(self) -> int:
        return self.voronoi_lcao.nM

    @property
    def comm(self) -> Communicator:
        return self.voronoi_lcao.comm

    @property
    def saved_fields(self) -> dict[str, Any]:
        return dict()

    def calculate_and_write(self,
                            out_fname: str,
                            write_extra: dict[str, Any] = dict()):
        """ Calculate the Voronoi weights in the Kohn-Sham basis and write to file.

        The weights are saved in a numpy archive if the file extension is ``.npz``
        or in a ULM file if the file extension is ``.ulm``.

        Parameters
        ----------
        out_fname
            File name of the resulting data file.
        write_extra
            Dictionary of additional data written to the file.
        """
        to_be_written = dict()
        if world.rank == 0:
            to_be_written.update(self.saved_fields)
            to_be_written.update(write_extra)

        if out_fname.endswith('.npz'):
            # Calculate weights
            weight_inn = list(self)

            # Write on root ranks
            if self.root:
                return

            to_be_written['atom_projections'] = atom_projections_to_numpy(self.atom_projections)
            np.savez(out_fname, weight_inn=np.array(weight_inn), **to_be_written)
        elif out_fname.endswith('.ulm'):
            with Writer(out_fname, world, mode='w', tag='Voronoi') as writer:
                writer.write(version=1)
                writer.write('atom_projections', self.atom_projections)
                writer.write(**to_be_written)

                writer.add_array('weight_inn', (self.nproj, self.nn, self.nn), dtype=float)

                # Calculate weights
                for weight_nn in self:
                    # Write on root (DummyWriter on other ranks)
                    writer.fill(weight_nn)
        else:
            raise ValueError(f'output-file must have ending .npz or .ulm, is {out_fname}')
        self.log(f'Weights written to {out_fname}', flush=True, who='Voronoi', rank=0)
        world.barrier()

    @classmethod
    def from_gpw(cls,
                 atom_projections: AtomProjectionsType,
                 gpw_file: str,
                 voronoi_grid: VoronoiGrid | None | str = None,
                 comm: Communicator | None = None) -> VoronoiWeightCalculator:
        """
        Set up calculation from GPAW file.

        Parameters
        ----------
        atom_projections
            List of atom groups. Each atom group is a list of integers (of any length).
        gpw_file
            File name of GPAW ground state file.
        voronoi_grid
            Voronoi grid, or ``None`` to calculate it, or a file name to read it from file.
        comm
            Communicator.
        """
        voronoi_lcao = VoronoiLCAOWeightCalculator(
                atom_projections=atom_projections,
                gpw_file=gpw_file,
                comm=comm)
        return cls(voronoi_lcao)

    @classmethod
    def from_lcao_file(cls,
                       voronoi_lcao_file: str,
                       comm: Communicator | None = None) -> VoronoiWeightCalculator:
        """
        Set up calculation from file of already computed weights in LCAO basis.

        Parameters
        ----------
        voronoi_lcao_file
            File name of file with Voronoi weights in LCAO basis.
        comm
            Communicator.
        """
        voronoi_lcao = VoronoiLCAOReader(voronoi_lcao_file, comm=comm)
        return cls(voronoi_lcao)


class VoronoiReader(VoronoiWeights):

    """ Read Voronoi weights from ulm file.

    Parameters
    ----------
    ulm_fname
        File name.
    comm
        GPAW MPI communicator object. Defaults to world.
    """

    _nn: int
    _atom_projections: AtomProjectionsType

    def __init__(self,
                 ulm_fname: str,
                 comm: Communicator | None = None):
        super().__init__(comm=comm)

        self.ulm_fname = ulm_fname
        self.reader = parulmopen(self.ulm_fname, self.comm)

        # Read size
        if self.root:
            weight_inn = self.reader.proxy('weight_inn')
            assert weight_inn.dtype is np.dtype(float)
            assert weight_inn.shape[1] == weight_inn.shape[2]
            atom_projections = self.reader.atom_projections
            nn = weight_inn.shape[1]
            brdcast = (atom_projections, nn)
        else:
            brdcast = None

        brdcast = broadcast(brdcast, root=0, comm=self.comm)
        self._atom_projections, self._nn = brdcast  # type: ignore

    @property
    def atom_projections(self) -> AtomProjectionsType:
        return self._atom_projections

    @property
    def nn(self) -> int:
        return self._nn

    def __exit__(self, exc_type, exc_value, tb):
        self.reader.close()

    def __iter__(self) -> Iterator[NDArray[np.float64] | None]:
        for i in range(len(self)):
            if self.root:
                weight_nn = self.reader.proxy('weight_inn', i)[:]
            else:
                weight_nn = None

            yield weight_nn

    @property
    def saved_fields(self) -> dict[str, Any]:
        """ Saved data fields associated with the object

        If this object is read from a ULM file there might be some extra
        data in that file. Return that data, or an empty dict if there is none.
        """
        data = {key: getattr(self.reader, key) for key in self.reader.keys()
                if key not in ['weight_inn', 'atom_projections']}

        return data


class EmptyVoronoiWeights(VoronoiWeights):

    """ Object representing a lack of weights. """

    def __iter__(self):
        return
        yield

    @property
    def atom_projections(self):
        return []

    @property
    def nn(self):
        return 0

    @property
    def saved_fields(self):
        return {}


class VoronoiLCAOWeights(ABC):

    """ Abstract base class for Voronoi weights in LCAO basis. """

    _atom_projections: AtomProjectionsType
    _comm: Communicator
    _log: Logger
    _dS_aii: Any
    _P_ani: Any
    _C_nM: Any

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        pass

    def __len__(self) -> int:
        """ Return the number of projections. """
        return self.nproj

    @abstractmethod
    def __iter__(self) -> Iterator[NDArray[np.float64] | None]:
        """ Iteratively yield Voronoi weights in the LCAO basis for each projection.

        Yields
        ------
        Matrix of Voronoi weights on root rank, ``None`` on other ranks.
        """
        raise NotImplementedError

    @property
    def log(self) -> Logger:
        return self._log

    def log_parallel(self, *args, **kwargs) -> Logger:
        """ Log message with communicator information. """
        return self._log(*args, **kwargs, comm=self.comm, who='Voronoi')

    @property
    @abstractmethod
    def nn(self) -> int:
        """ Number of bands. """
        raise NotImplementedError

    @property
    @abstractmethod
    def nM(self) -> int:
        """ Number of basis functions. """
        raise NotImplementedError

    @property
    def nproj(self) -> int:
        """ Number of atomic projections """
        return len(self.atom_projections)

    @property
    def atom_projections(self) -> AtomProjectionsType:
        """ List of atom projections. """
        return self._atom_projections

    @property
    def calc(self) -> GPAWCalculator | None:
        """ GPAW calculator instance. """
        return None

    @property
    def comm(self) -> Communicator:
        """ MPI Communicator. """
        return self._comm

    @property
    def root(self) -> bool:
        """ Whether this rank is the root rank. """
        return self.comm.rank == 0

    @property
    def C_nM(self) -> NDArray[np.float64] | None:
        """ LCAO wave function coefficients on root rank, ``None`` on other ranks. """
        return self._C_nM if self.root else None

    @property
    def P_ani(self) -> dict[int, NDArray[np.float64]] | None:
        r""" PAW projectors :math:`P_{ni}^a` on the root rank, ``None`` on other ranks.

        .. math::

            P_{ni}^a = \left<\tilde{p}_i^a | \tilde{\psi}_n \right>
        """
        return self._P_ani if self.root else None

    @property
    def dS_aii(self) -> dict[int, NDArray[np.float64]] | None:
        r""" Overlap matrix PAW corrections :math:`\Delta S_{ij}^a` on the root rank, ``None`` on other ranks.

        .. math::

            \Delta S_{ij}^a
            = \left<\phi_i^a|\phi_j^a\right>
            - \left<\tilde{\phi}_i^a|\tilde{\phi}_j^a\right>
        """
        return self._dS_aii if self.root else None

    @property
    @abstractmethod
    def saved_fields(self) -> dict[str, Any]:
        """ Saved data fields associated with the object.

        If this object is read from a ULM file there might be some extra
        data in that file. Return that data, or an empty dict if there is none.
        """
        raise NotImplementedError

    @property
    def arrays(self) -> dict[str, Any]:
        if self.comm.rank != 0:
            return {}

        arrays = dict(P_ani=self.P_ani,
                      C_nM=self.C_nM,
                      dS_aii=self.dS_aii)

        return arrays


class VoronoiLCAOReader(VoronoiLCAOWeights):

    """ Read Voronoi weights in the LCAO basis from ULM file.

    Parameters
    ----------
    ulm_fname
        File name.
    comm
        GPAW MPI communicator object. Defaults to world.
    """

    def __init__(self,
                 ulm_fname: str,
                 comm=None):
        self.ulm_fname = ulm_fname

        if comm is None:
            comm = world

        self._log = Logger()
        self._comm = comm
        self.reader = parulmopen(self.ulm_fname, self.comm)

        self._dS_aii: dict[int, NDArray[np.float64]] | None
        self._P_ani: dict[int, NDArray[np.float64]] | None
        self._C_nM = NDArray[np.float64] | None

        # Read arrays on root rank
        if self.root:
            weight_iMM = self.reader.proxy('weight_iMM')
            assert weight_iMM.dtype is np.dtype(float)
            assert weight_iMM.shape[1] == weight_iMM.shape[2]
            self._dS_aii = self.reader.dS_aii
            self._P_ani = self.reader.P_ani
            self._C_nM = self.reader.C_nM[:]
            atom_projections = self.reader.atom_projections
            brdcast = (atom_projections, ) + self._C_nM.shape
        else:
            brdcast = None
            self._C_nM = None
            self._P_ani = None
            self._dS_aii = None

        # Broadcast atom projections and number of bands and basis functions
        brdcast = broadcast(brdcast, root=0, comm=self.comm)
        self._atom_projections, self._nn, self._nM = brdcast  # type: ignore

    def __exit__(self, exc_type, exc_value, tb):
        self.reader.close()

    @property
    def nn(self) -> int:
        return self._nn

    @property
    def nM(self) -> int:
        return self._nM

    def __iter__(self) -> Iterator[NDArray[np.float64]]:
        for i in range(len(self)):
            if self.root:
                weight_MM = self.reader.proxy('weight_iMM', i)[:]
            else:
                weight_MM = None

            yield weight_MM

    @property
    def saved_fields(self) -> dict[str, Any]:
        data = {key: getattr(self.reader, key) for key in self.reader.keys()
                if key not in ['weight_iMM', 'atom_projections',
                               'dS_aii', 'P_ani', 'C_nM']}

        return data


class VoronoiLCAOWeightCalculator(VoronoiLCAOWeights):

    r"""Calculate Voronoi weights in LCAO basis.

    For each atomic projection, calculates

    .. math::

        \tilde{v}_{\mu\nu}
        = \left<\tilde{\phi}_{\mu} | \hat{w} | \tilde{\phi}_{\nu}\right>
        = \int w(\vec{r}) \tilde{\phi}_{\mu}^*(\vec{r}) \tilde{\phi}_{\nu}(\vec{r}) d\vec{r}

    where the operator :math:`\hat{w} = w(\vec{r})` is 1 in the
    Voronoi region of the atomic projections and 0 outside, and :math:`\tilde{\phi}_{\nu}` are
    the smooth LCAO basis functions.

    Parameters
    ----------
    atom_projections
        List of atom groups. Each atom group is a list of integers (of any length).
    gpw_file
        File name of GPAW ground state file.
    voronoi_grid
        Voronoi grid, or ``None`` to calculate it, or a file name to read it from file.
    domain
        Domain size.
    comm
        Communicator.
    """

    _calc: GPAWCalculator

    def __init__(self,
                 atom_projections: AtomProjectionsType,
                 gpw_file: str,
                 voronoi_grid: VoronoiGrid | None | str = None,
                 domain: int = -1,
                 comm: Communicator | None = None):
        assert all([isinstance(proj_atoms, list) or isinstance(proj_atoms, np.ndarray)
                    for proj_atoms in atom_projections])
        self._atom_projections = atom_projections

        if comm is None:
            comm = world

        self._comm = comm
        self._log = Logger()

        if voronoi_grid is None:
            voronoi_grid = VoronoiGridCalculator()
        if isinstance(voronoi_grid, str):
            voronoi_grid = VoronoiGridReader(voronoi_grid)
        self.voronoi_grid = voronoi_grid

        if domain == -1:
            domain = self.comm.size

        # Set up GPAW calculator
        calc = GPAW(gpw_file, txt=None, communicator=self.comm, parallel={'domain': domain})
        calc.initialize_positions()
        self.log('Loaded and initialized GPAW', rank=0, flush=True, who='Voronoi')
        self._calc = calc  # type: ignore

        # Collect wave functions, projectors and overlap to the root rank
        C_nM = calc.wfs.collect_array('C_nM', k=0, s=0)
        P_ani = proj_as_dict_on_master(self.calc.wfs.kpt_u[0].projections, 0, self.nn)
        dS_aii = {a: setup.dO_ii for a, setup in enumerate(calc.wfs.setups)}

        self._C_nM = C_nM if self.root else None
        self._P_ani = P_ani if self.root else None
        self._dS_aii = dS_aii if self.root else None

    @property
    def nn(self) -> int:
        return self.calc.wfs.bd.nbands

    @property
    def nM(self) -> int:
        return self.calc.wfs.setups.nao

    @property
    def calc(self) -> GPAWCalculator:
        return self._calc

    def __iter__(self) -> Iterator[NDArray[np.float64] | None]:
        # Get the Voronoi grid
        a_G = self.voronoi_grid.a_G(self.calc, self.log)

        for proj_atoms in self.atom_projections:
            w_G = np.where(np.isin(a_G, proj_atoms), 1.0, 0.0)
            if self.calc.comms['b'].rank != 0:
                # The band comm ranks compute the same information
                return None

            # Calculate the weights on the domain communicator
            weight_MM = self.calc.wfs.basis_functions.calculate_potential_matrices(w_G)[0]
            tri2full(weight_MM)

            # Sum to the root rank
            self.calc.comms['d'].sum(weight_MM, root=0)

            self.log(f'Computed LCAO weights for projection {proj_atoms}', rank=0, flush=True, who='Voronoi')

            if self.root:
                yield weight_MM
            else:
                yield None

    @property
    def saved_fields(self) -> dict[str, Any]:
        return dict()

    def calculate_and_write(self,
                            out_fname: str,
                            write_extra: dict[str, Any] = dict()):
        """ Calculate the Voronoi weights in the LCAO basis and write to file.

        The weights are saved in a numpy archive if the file extension is ``.npz``
        or in a ULM file if the file extension is ``.ulm``.

        Parameters
        ----------
        out_fname
            File name of the resulting data file.
        write_extra
            Dictionary of additional data written to the file.
        """
        to_be_written = dict()
        if world.rank == 0:
            to_be_written.update(self.saved_fields)
            to_be_written.update(self.arrays)
            to_be_written.update(write_extra)

        if out_fname.endswith('.npz'):
            # Calculate weights
            weight_iMM = list(self)

            # Write on root ranks
            if self.root:
                return

            to_be_written['atom_projections'] = atom_projections_to_numpy(self.atom_projections)
            np.savez(out_fname, weight_iMM=np.array(weight_iMM), **to_be_written)
        elif out_fname.endswith('.ulm'):
            with Writer(out_fname, self.comm, mode='w', tag='Voronoi') as writer:
                writer.write(version=1)
                writer.write('atom_projections', self.atom_projections)
                writer.write(**to_be_written)

                writer.add_array('weight_iMM', (self.nproj, self.nM, self.nM), dtype=float)

                # Calculate weights
                for weight_MM in self:
                    # Write on root (DummyWriter on other ranks)
                    writer.fill(weight_MM)
        else:
            raise ValueError(f'output-file must have ending .npz or .ulm, is {out_fname}')
        self.log(f'Written weights in LCAO basis to {out_fname}', flush=True, who='Voronoi', rank=0)
        world.barrier()


class VoronoiGrid(ABC):

    @abstractmethod
    def a_G(self,
            calc: GPAWCalculator,
            log: Logger) -> NDArray[np.int_]:
        """ Voronoi grid (on the coarse grid of the GPAW calculator)
        distributed on the domain communicator.

        Each element in the grid is an integer corresponding to the closest atom.

        Parameters
        ----------
        GPAW calculator.
        """
        raise NotImplementedError

    def write(self,
              filename: str,
              calc: GPAWCalculator,
              log: Logger):
        """ Write grid to file.

        Parameters
        ----------
        file name
            File name.
        calc
            GPAW calculator.
        """
        filename = str(filename)

        # Calculate grid and collect to root
        big_a_G = calc.density.gd.collect(self.a_G(calc, log))
        if filename.endswith('.npz'):
            np.savez_compressed(filename, a_G=big_a_G)
        else:
            np.save(filename, big_a_G)
        log(f'Written Voronoi grid to {filename}', who='Voronoi', flush=True, rank=0)


class VoronoiGridReader(VoronoiGrid):

    """ Read Voronoi grid from file. """

    def __init__(self,
                 filename: str):
        self.filename = filename

    def a_G(self,
            calc: GPAWCalculator,
            log: Logger) -> NDArray[np.int_]:
        # Read the grid on the domain communicator root
        domain_comm = calc.comms['d']
        if domain_comm.rank == 0:
            if self.filename.endswith('.npz'):
                files = np.load(self.filename)
                big_a_G = files['a_G']
            else:
                big_a_G = np.load(self.filename)

            assert big_a_G.dtype == np.int16

        # Distribute grid across domain communicator
        gd = calc.density.gd
        a_G = gd.zeros(dtype=np.int16)
        gd.distribute(big_a_G if domain_comm.rank == 0 else None, a_G)

        log('Loaded Voronoi grid', rank=0, flush=True, who='Voronoi')

        return a_G


class VoronoiGridCalculator(VoronoiGrid):

    """ Calculate the Voronoi grid. """

    def a_G(self,
            calc: GPAWCalculator,
            log: Logger) -> NDArray[np.int_]:
        log('Computing Voronoi grid', rank=0, flush=True, who='Voronoi')
        atoms = calc.get_atoms()
        a_G = wignerseitz(calc.density.gd, atoms)
        a_G = a_G.astype(np.int16)
        log('Computed Voronoi grid', rank=0, flush=True, who='Voronoi')

        return a_G


def atom_projections_to_numpy(atom_projections: AtomProjectionsType) -> NDArray[np.int_]:
    Ni = len(atom_projections)
    if Ni == 0:
        Nj = 0
    else:
        Nj = max([len(proj_atoms) for proj_atoms in atom_projections])
    atom_projections_ij = np.full((Ni, Nj), -1, dtype=int)
    for i, proj_atoms in enumerate(atom_projections):
        na = len(proj_atoms)
        atom_projections_ij[i, :na] = proj_atoms

    return atom_projections_ij


def proj_as_dict_on_master(proj, n1: int, n2: int) -> dict[int, NDArray[np.float64]]:
    """ Collect the projectors to a dictionary on the root rank."""
    # In newer versions of GPAW this is proj.as_dict_on_master
    P_nI = proj.collect()
    if P_nI is None:
        return {}
    I1 = 0
    P_ani = {}
    for a, ni in enumerate(proj.nproj_a):
        I2 = I1 + ni
        P_ani[a] = P_nI[n1:n2, I1:I2]
        I1 = I2
    return P_ani
