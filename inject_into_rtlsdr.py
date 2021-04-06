import sys
sys.path.insert(0, '/home/bryanb/setigen')
import setigen as stg

import numpy as np


iq_sample_rate = 2.048e6
sample_rate = iq_sample_rate * 2
carrier_freq = 90.3e6

antenna = stg.voltage.Antenna(sample_rate=sample_rate, 
                              fch1=carrier_freq - iq_sample_rate / 2,
                              ascending=True,
                              num_pols=1)


num_taps = 8
num_branches = 64
fftlength = 1024
int_factor = 1

digitizer = stg.voltage.ComplexQuantizer(target_fwhm=32,
                                         num_bits=8)

filterbank = stg.voltage.PolyphaseFilterbank(num_taps=num_taps, 
                                             num_branches=num_branches)

requantizer = stg.voltage.ComplexQuantizer(target_fwhm=32,
                                           num_bits=8)

start_chan = 0
num_chans = num_branches // 2
rvb = stg.voltage.RawVoltageBackend(antenna,
                                    digitizer=digitizer,
                                    filterbank=filterbank,
                                    requantizer=requantizer,
                                    start_chan=start_chan,
                                    num_chans=num_chans,
                                    block_size=33554432,
                                    blocks_per_file=128,
                                    num_subblocks=32)

# Define function to read in IQ data
f = open('rtlsdr.dat', 'rb')

def iq_signal(f):
    """f is the file handler"""
    def sub_func(ts):
        num_samples = len(ts)

        iq = f.read(num_samples)

        iq = xp.array(np.frombuffer(iq, dtype=np.uint8), dtype='float')
        iq -= 128
        iq = iq[0::2] + iq[1::2] * 1j

        # IQ bandwidth is iq_sample_rate, so shift by half
        shift_freq = iq_sample_rate / 2
        iq_shifted = iq * xp.exp(1j * 2 * xp.pi * shift_freq * ts[0::2])

        v = xp.zeros(num_samples, dtype='complex')
        v[0::2] = iq_shifted
        return v
    return sub_func

antenna.x.add_signal(iq_signal(f))

# Add synthetic signals
antenna.x.add_noise(0, 1)

level = stg.voltage.get_level(snr=3e4, 
                              raw_voltage_backend=rvb,
                              obs_length=60, 
                              length_mode='obs_length',
                              fftlength=fftlength)

unit_drift_rate = stg.voltage.get_unit_drift_rate(rvb,
                                                  fftlength=fftlength,
                                                  int_factor=int_factor)

# Update noise stats, and reset file pointer
antenna.x.update_noise()
f.seek(0)

antenna.x.add_constant_signal(f_start=90.9e6, 
                              drift_rate=0.2e6/60,
                              level=antenna.x.get_total_noise_std()*level*np.sqrt(0.2e6/60/unit_drift_rate))


rvb.record(raw_file_stem='test',
           obs_length=60, 
           length_mode='obs_length',
           header_dict={},
           verbose=False)

# Remember to close the file!
f.close()
