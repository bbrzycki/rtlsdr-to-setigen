import sys
sys.path.insert(0, '/Users/bryanbrzycki/Documents/Research/Breakthrough-Listen/Code/setigen')
import setigen as stg

import numpy as np

def to_voltages(ts, iq_data, carrier_freq):
    return np.real(iq_data * np.exp(1j * 2 * np.pi * carrier_freq * ts))

sample_rate = 2.048e6
carrier_freq = 90.3e6


num_taps = 8
num_branches = 16

chan_bw = sample_rate / num_branches

digitizer = stg.voltage.RealQuantizer(target_fwhm=32,
                                      num_bits=8)

filterbank = stg.voltage.PolyphaseFilterbank(num_taps=num_taps, 
                                             num_branches=num_branches)

requantizer = stg.voltage.ComplexQuantizer(target_fwhm=32,
                                           num_bits=8)



antenna = stg.voltage.Antenna(sample_rate=sample_rate, 
                              fch1=carrier_freq - sample_rate/2,
                              ascending=True,
                              num_pols=1)

start_rec_chan = 0
num_rec_chans = 8
rvb = stg.voltage.RawVoltageBackend(antenna,
                                    digitizer=digitizer,
                                    filterbank=filterbank,
                                    requantizer=requantizer,
                                    start_rec_chan=start_rec_chan,
                                    num_rec_chans=num_rec_chans,
                                    block_size=num_rec_chans*num_taps*2*1024,
                                    blocks_per_file=128,
                                    num_subblocks=32)



f = open('test.dat', 'rb')





def my_signal(ts):
    num_samples = len(ts)
    
    iq = f.read(2*num_samples)
    iq = np.frombuffer(iq, dtype=np.uint8).astype(float)
    iq -= 128
    iq = iq[0::2] + iq[1::2] * 1j
    
    v = to_voltages(ts, iq, carrier_freq)
    return v

antenna.x.add_signal(my_signal)


rvb.record(raw_file_stem='test',
           obs_length=55, 
           length_mode='obs_length',
           header_dict={'HELLO': 'test_value',
                        'TELESCOP': 'GBT'},
           verbose=False)

f.close()