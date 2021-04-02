import sys
sys.path.insert(0, '/home/bryanb/setigen')
import setigen as stg

import numpy as np


iq_sample_rate = 2.048e6
sample_rate = iq_sample_rate * 2
carrier_freq = 90.3e6


num_taps = 8
num_branches = 64
fftlength = 65536

chan_bw = sample_rate / num_branches

digitizer = stg.voltage.ComplexQuantizer(target_fwhm=32,
                                      num_bits=8)

filterbank = stg.voltage.PolyphaseFilterbank(num_taps=num_taps, 
                                             num_branches=num_branches)

requantizer = stg.voltage.ComplexQuantizer(target_fwhm=32,
                                           num_bits=8)



antenna = stg.voltage.Antenna(sample_rate=sample_rate, 
                              fch1=carrier_freq - iq_sample_rate / 2,
                              ascending=True,
                              num_pols=1)

print(antenna.fch1)


start_chan = 0
num_chans = num_branches//2
rvb = stg.voltage.RawVoltageBackend(antenna,
                                    digitizer=digitizer,
                                    filterbank=filterbank,
                                    requantizer=requantizer,
                                    start_chan=start_chan,
                                    num_chans=num_chans,
                                    block_size=num_chans*num_taps*2*1024,
                                    blocks_per_file=128,
                                    num_subblocks=32)

print(f'chan_bw: {rvb.chan_bw}')


f = open('test.dat', 'rb')



def to_voltages(ts, iq):
    shift_freq = iq_sample_rate / 2
    v = iq * np.exp(1j * 2 * np.pi * shift_freq * ts)
    v_temp = np.zeros(2*len(v), dtype='complex128')
    v_temp[0::2] = v
    v_temp[1::2] = 0
#     v_temp[1::2] = -np.imag(v)
    return v_temp # np.repeat(v, 2)

def my_signal(ts):
    num_samples = len(ts)
    
    iq = f.read(num_samples)
    iq = np.frombuffer(iq, dtype=np.uint8).astype(float)
    iq -= 128
    iq = iq[0::2] + iq[1::2] * 1j
    
    v = to_voltages(ts[0::2], iq)
    return v

antenna.x.add_signal(my_signal)

antenna.x.add_noise(0, 1)

level = stg.voltage.get_intensity(3e4, 
                  rvb,
                  obs_length=55, 
                  length_mode='obs_length',
                  fftlength=fftlength)
unit_drift_rate = stg.voltage.get_unit_drift_rate(rvb,
                        fftlength=fftlength,
                        int_factor=1)
antenna.x.add_constant_signal(90.9e6, 
                              0.2e6/60,
                              antenna.x.get_total_noise_std()*level*np.sqrt(0.2e6/60/unit_drift_rate))


rvb.record(raw_file_stem='test',
           obs_length=55, 
           length_mode='obs_length',
           header_dict={'HELLO': 'test_value',
                        'TELESCOP': 'GBT'},
           verbose=False)

f.close()
