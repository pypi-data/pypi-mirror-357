from __future__ import annotations

from typing import Collection, Generator
import numpy as np
from numpy.typing import NDArray

from gpaw.tddft.units import au_to_as

from .base import BaseDistributor, RhoParameters
from .time import TimeDistributor, AlltoallvTimeDistributor
from ..buffer import DensityMatrixBuffer
from ..readers.gpaw import KohnShamRhoWfsReader
from ...utils import get_array_filter, safe_fill_larger, fast_pad
from ...perturbation import create_perturbation, PerturbationLike, PulsePerturbation
from ...utils.logging import format_times
from ...utils.memory import MemoryEstimate
from ...typing import Array1D


class PulseConvolver(BaseDistributor):
    r""" Class performing pulse convolution of density matrices.

    The procedure of the pulse convolution is the following:

    - The entire time series of (real and/or imaginary parts of) density matrices
      is read, in several chunks of indices (n1, n2). Each MPI rank works on
      different chunks.
    - Each chunk is Fourier transformed, divided by the Fourier transform of the
      original perturbation and multiplied by the Fourier transform of the
      new pulse(s).
    - Optionally, derivatives are computed by multiplying the density matrices
      in the frequency domain by factors of :math:`i \omega`.
    - Each chunk is inverse Fourier tranformed, and only selected times are kept.

    Additionally, this class can redistribute the resulting convoluted density matrices
    so that the each rank holds the entire density matrix, for a few times.

    Parameters
    ----------
    rho_nn_reader
        Object begin able to iteratively read density matrices in the time domain.
        Density matrices are split in chunks and distributed among ranks.
    perturbation
        The perturbation which the density matrices read by :attr:`rho_nn_reader`
        are a response to.
    pulses
        List of pulses to perform to convolution with.
    derivative_order_s
        List of derivative orders to compute.
    filter_times
        After convolution keep only these times (or the times closest to them).
        In atomic units.
    result_on_ranks
        List of ranks among which the resulting arrays will be distributed.
        Empty list (default) to distribute among all ranks.
    """

    def __init__(self,
                 rho_nn_reader: TimeDistributor,
                 perturbation: PerturbationLike,
                 pulses: Collection[PerturbationLike],
                 derivative_order_s: list[int] = [0],
                 filter_times: list[float] | Array1D[np.float64] | None = None,
                 result_on_ranks: list[int] = []):
        super().__init__(rho_nn_reader.rho_wfs_reader,
                         rho_nn_reader._parameters,
                         comm=rho_nn_reader.comm)
        self.rho_nn_reader = rho_nn_reader

        # Check if we need to perform upscaling
        wfs_time_t = self.rho_nn_reader.time_t
        dt = self.rho_nn_reader.dt
        self._warn_too_small_dt = False

        if filter_times is None or len(filter_times) < 2:
            self._upscaling = 1
        else:
            # See if there is a mismatch between wanted and existing time grids.
            # If so, then upscale the data in the Fourier transform step.
            self._requested_dt = min(np.diff(np.sort(filter_times)))
            upscaling = int(np.round(dt / self._requested_dt))
            if upscaling < 1:
                upscaling = 1
            elif upscaling > 100:
                self._warn_too_small_dt = True
                upscaling = 1
            self._upscaling = upscaling

        # Construct an upscaled times grid
        self._time_t = wfs_time_t[0] + dt/self.upscaling * np.arange(len(wfs_time_t) * self.upscaling)

        # And filter it
        self._flt_t = get_array_filter(self._time_t, filter_times)

        # Set up pulses and perturbation
        self.pulses = [create_perturbation(pulse) for pulse in pulses]
        if not all(isinstance(pulse, PulsePerturbation) for pulse in self.pulses):
            raise ValueError('Pulse convolution can only be performed with pulses of type PulsePerturbation.')
        self.perturbation = create_perturbation(perturbation)

        # Set up derivatives
        assert all(order in [0, 1, 2] for order in derivative_order_s)
        assert all(np.diff(derivative_order_s) > 0), 'Derivative orders must be strictly increasing'
        self.derivative_order_s = derivative_order_s

        # Check which ranks the result should be stored on
        if len(result_on_ranks) == 0:
            self._result_on_ranks = set(range(self.comm.size))
        else:
            assert all(isinstance(rank, int) and rank >= 0 and rank < self.comm.size
                       for rank in result_on_ranks), result_on_ranks
            self._result_on_ranks = set(result_on_ranks)

        self._dist_buffer: DensityMatrixBuffer | None = None

    @property
    def dtype(self):
        return np.float64

    @property
    def xshape(self):
        return (len(self.pulses), self.nt)

    @property
    def time_t(self) -> NDArray[np.float64]:
        """ Array of times corresponding to convoluted density matrices; in atomic units. """
        return self._time_t[self._flt_t]

    @property
    def nt(self) -> int:
        """ Number of times for which convoluted density matrices are calculated. """
        return len(self.time_t)

    @property
    def nlocalt(self) -> int:
        """ Number of times stored on this rank after redistribution of the result. """
        return (self.nt + self.nranks_result - 1) // self.nranks_result

    @property
    def upscaling(self) -> int:
        """ Upscaling factor.

        Data is upscaled in time by this factor during the Fourier transformation step,
        in order to calculate convoluted density matrices at a denser grid of times than
        what is present in the time-dependent wave functions file.
        """
        return self._upscaling

    @property
    def result_on_ranks(self) -> list[int]:
        """ Set of ranks among which the result will be distributed. """
        return sorted(self._result_on_ranks)

    @property
    def nranks_result(self) -> int:
        """ Number of ranks storing part of the result after redistribution. """
        return len(self._result_on_ranks)

    def distributed_work(self) -> list[list[int]]:
        # Empty list for ranks that will not have any part of the result
        timet_r = self.comm.size * [[]]
        for r, rank in enumerate(self.result_on_ranks):
            timet_r[rank] = list(range(r, self.nt, self.nranks_result))

        return timet_r

    def my_work(self) -> list[int]:
        timet_r = self.distributed_work()
        return timet_r[self.comm.rank]

    def __str__(self) -> str:
        wfs_nt = len(self.rho_nn_reader.time_t)
        dt = self.rho_nn_reader.dt

        lines = []
        lines.append('Pulse convolver')
        lines.append(f'  Performing convolution trick on {self.maxnchunks} ranks')
        lines.append('  Fast Fourier transform')
        lines.append(f'    matrix dimensions {self.rho_nn_reader._parameters.nnshape}')
        lines.append(f'    grid of {wfs_nt} times')
        lines.append(f'    {self.describe_reim()}')
        lines.append('   In frequency domain')
        lines.append(f'     calculating {self.describe_derivatives()}')
        if self._warn_too_small_dt:
            lines.append('WARNING:, the smallest spacing between requested times is ')
            lines.append(f'{self._requested_dt * au_to_as:.2f}. This is much smaller than the time step ')
            lines.append(f'in the time-dependent wave functions file ({dt * au_to_as:.2f} as). ')
            lines.append('No upscaling will be done.')
        elif self.upscaling == 1:
            lines.append('     not upscaling data')
        else:
            lines.append(f'     upscaling by factor {self.upscaling}')
            lines.append(f'       requested time step {self._requested_dt * au_to_as:.2f} as')
            lines.append(f'       time stpe in file {dt * au_to_as:.2f} as.')
        lines.append(f'     convolution with {len(self.pulses)} pulses')
        lines.append('  Fast inverse Fourier transform')
        lines.append(f'    keeping time grid of {self.nt} times')
        lines.append(f'      {format_times(self.time_t, units="au")}')
        lines.append('')

        lines.append('  Redistributing into full density matrices')
        lines.append(f'    {self.niters} iterations to process all chunks')
        lines.append(f'    matrix dimensions {self.rho_nn_reader._parameters.full_nnshape}')
        lines.append(f'    result stored on {self.nranks_result} ranks')

        return '\n'.join(lines)

    def get_memory_estimate(self) -> MemoryEstimate:
        parameters = self.rho_nn_reader._parameters

        narrays = (2 if self.yield_re and self.yield_im else 1) * len(self.derivative_order_s)
        temp_shape = parameters.nnshape + (self.maxnchunks, len(self.pulses), self.nlocalt, narrays)
        result_shape = parameters.full_nnshape + (len(self.pulses), self.nlocalt, narrays)

        total_result_size = int(np.prod(parameters.full_nnshape + (len(self.pulses), self.nt))) * narrays

        comment = f'Buffers hold {narrays} arrays ({self.describe_reim()}, {self.describe_derivatives()})'
        own_memory_estimate = MemoryEstimate(comment=comment)
        own_memory_estimate.add_key('Temporary buffer', temp_shape, float,
                                    on_num_ranks=self.nranks_result)
        own_memory_estimate.add_key('Result buffer', result_shape, float,
                                    total_size=total_result_size,
                                    on_num_ranks=self.nranks_result)

        memory_estimate = MemoryEstimate()
        memory_estimate.add_child('Time-dependent wave functions reader',
                                  self.rho_nn_reader.rho_wfs_reader.get_memory_estimate())
        memory_estimate.add_child('Parallel density matrices reader',
                                  self.rho_nn_reader.get_memory_estimate())
        memory_estimate.add_child('Pulse convolver',
                                  own_memory_estimate)

        return memory_estimate

    def _freq_domain_derivative(self,
                                order: int) -> NDArray[np.complex128 | np.float64]:
        r""" Take derivative in frequency space by multiplying by .. math:

        (i \omega)^n.

        Parameters
        ----------
        order
            Order :math:`n` of the derivative.
        """
        if order == 0:
            return np.array([1])

        padnt = fast_pad(self.rho_nn_reader.nt)
        dt = self.rho_nn_reader.dt
        omega_w = 2 * np.pi * np.fft.rfftfreq(padnt, dt)

        return (1.0j * omega_w) ** order  # type: ignore

    @property
    def dist_buffer(self) -> DensityMatrixBuffer:
        """ Buffer of denisty matrices on this rank after redistribution. """
        if self._dist_buffer is None:
            self._dist_buffer = self.redistribute()
        return self._dist_buffer

    def __iter__(self) -> Generator[DensityMatrixBuffer, None, None]:
        """ Iteratively read density matrices and perform the pulse convolution.

        Each iteration performs the calculation for a different chunk of the
        density matrix. Each rank works on a different set of chunks.
        All ranks always work on the entire grid of times, during all interations.

        Yields
        ------
        A chunk of the convoluted density matrices, for the requested times.
        """
        wfs_time_t = self.rho_nn_reader.time_t  # Times in wave functions file
        padnt = fast_pad(len(wfs_time_t))  # Pad with zeros

        # Take Fourier transform of pulses
        pulse_pt = [pulse.pulse.strength(wfs_time_t) for pulse in self.pulses]
        pulse_pw = np.fft.rfft(pulse_pt, axis=-1, n=padnt)

        # Create buffer for result
        dm_buffer = DensityMatrixBuffer(self.rho_nn_reader._parameters.nnshape,
                                        (len(self.pulses), self.nt),
                                        np.float64)
        dm_buffer.zero_buffers(real=self.yield_re, imag=self.yield_im, derivative_order_s=self.derivative_order_s)

        for read_buffer in self.rho_nn_reader:
            x = []
            if self.yield_re:
                x.append((read_buffer._re_buffers[0], dm_buffer._re_buffers))
            if self.yield_im:
                x.append((read_buffer._im_buffers[0], dm_buffer._im_buffers))
            for data_nnt, buffers in x:
                # Take the Fourier transform of the data (Rerho or Imrho) and divide by
                # the Fourier transform of the perturbation
                # The data is padded by zeros, circumventing the periodicity of the Fourier transform
                data_nnw = self.perturbation.normalize_frequency_response(data_nnt, wfs_time_t, padnt, axis=-1)

                # Loop over the desired outputs (and which derivative orders they are)
                for derivative, buffer_nnpt in buffers.items():
                    deriv_w = self._freq_domain_derivative(derivative)
                    for p, pulse_w in enumerate(pulse_pw):
                        # Multiply factor for derivative (power of I*omega)
                        # All timesteps cancel when taking fft->ifft, so do not scale by it
                        _data_nnw = data_nnw * (deriv_w * pulse_w)
                        # Inverse Fourier transform
                        # Optionally, the data is upscaled by padding with even more zeros
                        conv_nnt = np.fft.irfft(_data_nnw, n=padnt * self.upscaling, axis=-1) * self.upscaling
                        buffer_nnpt[..., p, :] = conv_nnt[..., :len(self._time_t)][..., self._flt_t]

            yield dm_buffer.copy()

    def create_out_buffer(self) -> DensityMatrixBuffer:
        """ Create the DensityMatrixBuffer to hold the temporary density matrix after each redistribution """
        parameters = self.rho_nn_reader._parameters
        nlocalt = self.nlocalt if self.comm.rank in self.result_on_ranks else 0
        out_dm = DensityMatrixBuffer(nnshape=parameters.nnshape,
                                     xshape=(self.maxnchunks, len(self.pulses), nlocalt),
                                     dtype=np.float64)
        out_dm.zero_buffers(real=self.yield_re, imag=self.yield_im, derivative_order_s=self.derivative_order_s)

        return out_dm

    def create_result_buffer(self) -> DensityMatrixBuffer:
        """ Create the DensityMatrixBuffer to hold the resulting density matrix """
        parameters = self.rho_nn_reader._parameters
        nnshape = parameters.full_nnshape
        full_dm = DensityMatrixBuffer(nnshape=nnshape,
                                      xshape=(len(self.pulses), len(self.my_work())),
                                      dtype=np.float64)
        full_dm.zero_buffers(real=self.yield_re, imag=self.yield_im, derivative_order_s=self.derivative_order_s)

        return full_dm

    def redistribute(self) -> DensityMatrixBuffer:
        """ Perform the pulse convolution and redistribute the resulting density matrices.

        During the pulse convolution step, the data is distributed such that each rank
        stores the entire time series for one chunk of the density matrices, i.e. indices n1, n2.

        This function then performs a redistribution of the data such that each rank stores full
        density matrices, for certain times.

        If the density matrices are split into more chunks than there are ranks, then the
        chunks are read, convoluted with pulses and distributed in a loop several times until all
        data has been processed.

        Returns
        -------
        Density matrix buffer with x-dimensions (number of pulses, number of local times)
        where the number of local times variers between the ranks.
        """
        local_work = iter(self)
        parameters = self.rho_nn_reader._parameters
        log = self.log
        self.rho_nn_reader.rho_wfs_reader.lcao_rho_reader.striden == 0, \
            'n stride must be 0 (index all) for redistribute'

        # Time indices of result on each rank
        timet_r = self.distributed_work()

        out_dm = self.create_out_buffer()
        full_dm = self.create_result_buffer()

        _exhausted = object()

        # Loop over the chunks of the density matrix
        for chunki, indices_r in enumerate(self.work_loop_by_ranks()):
            # At this point, each rank stores one unique chunk of the density matrix.
            # All ranks have the entire time series of data for their own chunk.
            # If there are more chunks than ranks, then this loop will run
            # for several iterations. If the number of chunks is not divisible by the number of
            # ranks then, during the last iteration, some of the chunks are None (meaning the rank
            # currently has no data).

            # List of chunks that each rank currently stores, where element r of the list
            # contains the chunk that rank r works with. Ranks higher than the length of the list
            # currently store no chunks.
            # The list itself is identical on all ranks.
            chunks_by_rank = [indices[2:] for indices in indices_r if indices is not None]

            ntargets = len(chunks_by_rank)

            if self.comm.rank < ntargets:
                # This rank has data to send. Compute the pulse convolution and store the result
                dm_buffer = next(local_work)
            else:
                # This rank has no data to send
                assert next(local_work, _exhausted) is _exhausted
                # Still, we need to create a dummy buffer
                dm_buffer = DensityMatrixBuffer(nnshape=parameters.nnshape,
                                                xshape=(0, 0), dtype=np.float64)
                dm_buffer.zero_buffers(real=self.yield_re, imag=self.yield_im,
                                       derivative_order_s=self.derivative_order_s)

            log.start('alltoallv')

            # Redistribute the data:
            # - dm_buffer stores single chunks of density matrices, for all times and pulses.
            # - out_dm will store several chunks, for a few times
            # source_indices_r describes which slices of dm_buffer should be sent to which rank
            # target_indices_r describes to which positions of the out_dm buffer should be received
            # from which rank
            source_indices_r = [None if len(t) == 0 else (slice(None), t) for t in timet_r]
            target_indices_r = [r if r < ntargets else None for r in range(self.comm.size)]
            dm_buffer.redistribute(out_dm,
                                   comm=self.comm,
                                   source_indices_r=source_indices_r,
                                   target_indices_r=target_indices_r,
                                   log=log)

            if self.comm.rank == 0:
                log(f'Chunk {chunki+1}/{self.niters}: distributed convoluted response in '
                    f'{log.elapsed("alltoallv"):.1f}s', who='Response', flush=True)

            # Copy the redistributed data into the aggregated results buffer
            for array_nnrpt, full_array_nnpt in zip(out_dm._iter_buffers(), full_dm._iter_buffers()):
                for r, nn_indices in enumerate(chunks_by_rank):
                    safe_fill_larger(full_array_nnpt[nn_indices], array_nnrpt[:, :, r])

        assert next(local_work, _exhausted) is _exhausted

        return full_dm

    @classmethod
    def from_reader(cls,  # type: ignore
                    rho_nn_reader: KohnShamRhoWfsReader,
                    parameters: RhoParameters,
                    perturbation: PerturbationLike,
                    pulses: Collection[PerturbationLike],
                    derivative_order_s: list[int] = [0],
                    filter_times: list[float] | Array1D[np.float64] | None = None,
                    result_on_ranks: list[int] = []) -> PulseConvolver:
        time_distributor = AlltoallvTimeDistributor(rho_nn_reader, parameters)
        pulse_convolver = cls(time_distributor,
                              pulses=pulses,
                              perturbation=perturbation,
                              derivative_order_s=derivative_order_s,
                              filter_times=filter_times,
                              result_on_ranks=result_on_ranks)
        return pulse_convolver
