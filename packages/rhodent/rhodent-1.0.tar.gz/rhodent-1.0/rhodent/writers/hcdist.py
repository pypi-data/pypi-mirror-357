from __future__ import annotations

from typing import cast
import numpy as np
from numpy.typing import NDArray
from gpaw.mpi import world

from ..density_matrices.time import ConvolutionDensityMatrices
from .writer import (Writer, ResultsCollector, TimeAverageResultsCollector,
                     PulseConvolutionAverageResultsCollector)
from ..utils import get_gaussian_pulse_values


class HotCarriersWriter(Writer):

    """ Calculate hot-carrier totals, and optionally broadened hot-carrier energy distributions

    Parameters
    ----------
    collector
        ResultsCollector object
    only_one_pulse
        False if the resulting outputs should have one dimension corresponding
        to different pulses. True if there should be no such dimension. If True,
        then the calculator must only hold one pulse.
    """

    def __init__(self,
                 collector: ResultsCollector,
                 only_one_pulse: bool):
        super().__init__(collector)
        self.only_one_pulse = only_one_pulse
        if only_one_pulse:
            if isinstance(self.density_matrices, ConvolutionDensityMatrices):
                assert len(self.density_matrices.pulses) == 1, 'Only one pulse allowed'
        else:
            assert isinstance(self.density_matrices, ConvolutionDensityMatrices)

    @property
    def common_arrays(self) -> dict[str, NDArray[np.float64] | NDArray[np.int64] | int | float]:
        common = super().common_arrays
        assert isinstance(self.density_matrices, ConvolutionDensityMatrices)

        if isinstance(self.collector, (TimeAverageResultsCollector, PulseConvolutionAverageResultsCollector)):
            # Averages over time are taken
            common['avgtime_t'] = self.density_matrices.times * 1e-3
        else:
            common['time_t'] = self.density_matrices.times * 1e-3

        if isinstance(self.density_matrices, ConvolutionDensityMatrices):
            # If pulses are Gaussian pulses, then get dictionaries of 'pulsefreq' and 'pulsefwhm'
            pulsedicts = [get_gaussian_pulse_values(pulse) for pulse in self.density_matrices.pulses]

            try:
                pulsefreqs = [d['pulsefreq'] for d in pulsedicts]
                pulsefwhms = [d['pulsefwhm'] for d in pulsedicts]

                if self.only_one_pulse:
                    common['pulsefreq'] = pulsefreqs[0]
                    common['pulsefwhm'] = pulsefwhms[0]
                else:
                    common['pulsefreq_p'] = np.array(pulsefreqs)
                    common['pulsefwhm_p'] = np.array(pulsefwhms)
            except KeyError:
                # Not GaussianPulses
                pass

        if self.calc.sigma is not None:
            # There is an energy grid
            common['sigma'] = self.calc.sigma
            common['energy_o'] = np.array(self.calc.energies_occ)
            common['energy_u'] = np.array(self.calc.energies_unocc)

        return common


def write_hot_carrier_distributions(out_fname: str,
                                    writer: HotCarriersWriter):
    zerostr = 'relative to Fermi level'
    average_times = isinstance(writer.collector, (TimeAverageResultsCollector, PulseConvolutionAverageResultsCollector))

    energies_occ = writer.calc.energies_occ
    energies_unocc = writer.calc.energies_unocc
    if len(energies_occ) == 0 and len(energies_unocc) == 0:
        raise ValueError('Either occupied or unoccupied energies grid must be given')

    _data = dict(**writer.common_arrays)
    _data.update(writer.calculate_data()._data)

    if world.rank > 0:
        return

    pulsefreq = _data.pop('pulsefreq', None)
    pulsefwhm = _data.pop('pulsefwhm', None)

    data = cast(dict[str, NDArray[np.float64]], _data)

    # Set up array to be written in the data file.
    # Rows are energies, columns are projections and/or times
    nI = len(writer.voronoi)
    ne = max(len(energies_occ), len(energies_unocc))  # Longest length of energies

    eh_labels = []
    if len(energies_occ) > 0:
        # Compute hole distributions
        eh_labels.append('H')
    if len(energies_unocc) > 0:
        # Compute electron distributions
        eh_labels.append('E')

    if average_times:
        nt = 1
    else:
        nt = len(data['time_t'])

    ncolspertime = len(eh_labels) * (1 + nI)

    savedata = np.full((ne, len(eh_labels) + nt * ncolspertime), np.nan)
    savedata_by_times = [savedata[:, col:col + ncolspertime]
                         for col in range(len(eh_labels), savedata.shape[1], ncolspertime)]

    # Set up format string
    fmt = len(eh_labels) * ['%15.6f'] + nt * ncolspertime * ['%18.8e']

    # Set up header contents
    header_lines = [f'Hot carrier (H=hole, E=electron) distributions {zerostr}']

    if pulsefreq is not None:
        header_lines.append(f'Response to pulse with frequency {pulsefreq:.2f}eV, '
                            f'FWHM {pulsefwhm:.2f}fs')

    if average_times:
        avgtimes = data['avgtime_t']
        header_lines.append(f'Averaged for {len(avgtimes)} times between '
                            f'{avgtimes[0]:.1f}fs-{avgtimes[-1]:.1f}fs')
    else:
        times = data['time_t']
        header_lines.append(f'Computed for the following {len(times)} times (in units of fs)')
        header_lines += [f'  {time:.4f}' for t, time in enumerate(times)]

    if nI > 0:
        header_lines.append('Atomic projections')
        header_lines += [f'  {i:4.0f}: {str(proj)}' for i, proj in enumerate(writer.voronoi.atom_projections)]

    header_lines.append(f'Gaussian folding, Width {writer.calc.sigma:.4f}eV')
    desc_entries = ([f'{label} energy (eV)' for label in eh_labels] +
                    [f'Total {label} (1/eV)' for label in eh_labels] +
                    [f'Proj {s} {i:2.0f} (1/eV)' for i in range(nI) for s in eh_labels])
    desc_entries = ([f'{s:>15}' for s in desc_entries[:len(eh_labels)]] +
                    [f'{s:>18}' for s in desc_entries[len(eh_labels):]])
    desc_entries[0] = desc_entries[0][2:]  # Remove two spaces to account for '# '
    if not average_times:
        desc_entries.append(' ... repeated for next times')
    header_lines.append(' '.join(desc_entries))

    # Write the data to the array
    if average_times:
        if len(eh_labels) == 2:
            # Computed both electron and hole distributions
            savedata[:len(energies_occ), 0] = energies_occ
            savedata[:len(energies_unocc), 1] = energies_unocc

            savedata[:len(energies_occ), 2] = data['hcdist_o']
            savedata[:len(energies_unocc), 3] = data['hcdist_u']

            if nI > 0:
                savedata[:len(energies_occ), 4::2] = data['hcdist_proj_Io'].T
                savedata[:len(energies_unocc), 5::2] = data['hcdist_proj_Iu'].T
        elif 'H' in eh_labels:
            # Only hole distributions
            savedata[:, 0] = energies_occ
            savedata[:, 1] = data['hcdist_o']

            if nI > 0:
                savedata[:, 2:] = data['hcdist_proj_Io'].T
        else:
            # Only electron distributions
            savedata[:, 0] = energies_unocc
            savedata[:, 1] = data['hcdist_u']

            if nI > 0:
                savedata[:, 1:] = data['hcdist_proj_Iu'].T
    else:
        if len(eh_labels) == 2:
            # Computed both electron and hole distributions
            savedata[:len(energies_occ), 0] = energies_occ
            savedata[:len(energies_unocc), 1] = energies_unocc

            for t, sdata in enumerate(savedata_by_times):
                sdata[:len(energies_occ), 0] = data['hcdist_to'][t]
                sdata[:len(energies_unocc), 1] = data['hcdist_tu'][t]

                if nI > 0:
                    sdata[:len(energies_occ), 2::2] = data['hcdist_proj_tIo'][t].T
                    sdata[:len(energies_unocc), 3::2] = data['hcdist_proj_tIu'][t].T
        elif 'H' in eh_labels:
            # Only hole distributions
            savedata[:, 0] = energies_occ

            for t, sdata in enumerate(savedata_by_times):
                sdata[:, 0] = data['hcdist_to'][t]

                if nI > 0:
                    sdata[:, 1:] = data['hcdist_proj_tIo'][t].T
        else:
            # Only electron distributions
            savedata[:, 0] = energies_unocc

            for t, sdata in enumerate(savedata_by_times):
                sdata[:, 0] = data['hcdist_tu'][t]

                if nI > 0:
                    sdata[:, 1:] = data['hcdist_proj_tIu'][t].T

    np.savetxt(out_fname, savedata, fmt, header='\n'.join(header_lines))
    writer.calc.log(f'Written {out_fname}', who='Calculator', flush=True)


def write_hot_carrier_totals_by_pulse(out_fname: str,
                                      writer: HotCarriersWriter):

    Np = len(writer.calc.pulses)
    data = dict(**writer.common_arrays)
    data.update(writer.calculate_data()._data)

    if world.rank > 0:
        return

    nI = len(writer.voronoi)
    avgtimes = data['avgtime_t']
    assert isinstance(avgtimes, np.ndarray)

    savedata = np.full((Np, 2*(2+nI)), np.nan)
    savedata[:, 0] = data['pulsefreq_p']
    savedata[:, 1] = data['pulsefwhm_p']
    savedata[:, 2] = data['sumocc_p']
    savedata[:, 3] = data['sumunocc_p']
    savedata[:, 4::2] = data['sumocc_proj_pI']
    savedata[:, 5::2] = data['sumunocc_proj_pI']

    projectionsstr = '\n'.join([f'  {i:4.0f}: {str(proj)}'
                                for i, proj in enumerate(writer.voronoi.atom_projections)])
    desc_entries = (['Pulse freq (eV)', 'Pulse FWHM (fs)', 'Total H', 'Total E'] +
                    [f'Proj {s} {i:2.0f}' for i in range(nI) for s in 'HE'])
    desc_entries = ([f'{s:>17}' for s in desc_entries[:2]] +
                    [f'{s:>15}' for s in desc_entries[2:]])
    desc_entries[0] = desc_entries[0][2:]  # Remove two spaces to account for '# '

    header = (f'Hot carrier (H=hole, E=electron) numbers\n'
              f'Averaged for {len(avgtimes)} times between '
              f'{avgtimes[0]:.1f}fs-{avgtimes[-1]:.1f}fs\n'
              'Atomic projections:\n'
              f'{projectionsstr}\n'
              f'{" ".join(desc_entries)}')
    fmt = 2*['%17.6f'] + (2*(nI + 1))*['%15.8e']
    np.savetxt(out_fname, savedata, fmt, header=header)
    writer.calc.log(f'Written {out_fname}', who='Calculator', flush=True)


def write_hot_carrier_totals_by_time(out_fname: str,
                                     writer: HotCarriersWriter):
    Nt = len(writer.calc.times)
    data = dict(**writer.common_arrays)
    data.update(writer.calculate_data()._data)

    if world.rank > 0:
        return

    nI = len(writer.voronoi)

    savedata = np.full((Nt, 1 + 2*(1+nI)), np.nan)
    savedata[:, 0] = data['time_t']
    savedata[:, 1] = data['sumocc_t']
    savedata[:, 2] = data['sumunocc_t']
    savedata[:, 3::2] = data['sumocc_proj_tI']
    savedata[:, 4::2] = data['sumunocc_proj_tI']

    projectionsstr = '\n'.join([f'  {i:4.0f}: {str(proj)}'
                                for i, proj in enumerate(writer.voronoi.atom_projections)])
    desc_entries = (['Time (fs)', 'Total H', 'Total E'] +
                    [f'Proj {s} {i:2.0f}' for i in range(nI) for s in 'HE'])
    desc_entries = ([f'{s:>17}' for s in desc_entries[:1]] +
                    [f'{s:>15}' for s in desc_entries[1:]])
    desc_entries[0] = desc_entries[0][2:]  # Remove two spaces to account for '# '

    header_lines = ['Hot carrier (H=hole, E=electron) numbers\n']
    if 'pulsefreq' in data:
        header_lines += [f'Response to pulse with frequency {data["pulsefreq"]:.2f}eV, '
                         f'FWHM {data["pulsefwhm"]:.2f}fs']
    header_lines += ['Atomic projections:',
                     f'{projectionsstr}\n',
                     ' '.join(desc_entries)]
    header = '\n'.join(header_lines)
    fmt = ['%17.6f'] + (2*(nI + 1))*['%15.8e']
    np.savetxt(out_fname, savedata, fmt, header=header)
    writer.calc.log(f'Written {out_fname}', who='Calculator', flush=True)
