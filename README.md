# rtlsdr-to-setigen

This repository has examples on taking data with RTL-SDR devices, using the `rtl_sdr` command line utility, and producing Breakthrough Listen GUPPI RAW files from the collected data.

The `setigen.voltage` module takes in time series voltage data and produces synthetic GUPPI RAW data files. However, taking IQ data and creating custom signal injection functions, we can load complex IQ data into the pipeline and create raw files. If desired, we can inject ideal drifting cosine signals on top of this, just using the standard `setigen.voltage` functions. 

## Contents

* `observe.sh` is a bash script based on the `rtl_sdr` utility that collects data from an RTL-SDR device. Specifically, the script collects 1% more data than specified by observation length, just to make sure we have enough data to save after passing everything through the polyphase filterbank in the `setigen` voltage pipeline. `example_observation.sh` is a sample call to `observe.sh`, used to collect 60 seconds of data for use in the tutorial notebooks.
* `passing_rtlsdr_to_setigen.ipynb` is a Jupyter notebook that walks through steps to set up the `setigen` voltage pipeline, and details on reading in and formatting the RTL-SDR IQ data. Shows results after creating RAW files and reducing with `rawspec`. 
* `injecting_signals_in_rtlsdr.ipynb` is a Jupyter notebook that further injects a drifting cosine signal onto RTL-SDR data, and shows the results.
* `inject_into_rtlsdr.py` is just the code from the injection notebook, compiled into a Python script.

## Code sources

`setigen`: https://github.com/bbrzycki/setigen

`rawspec`: https://github.com/UCBerkeleySETI/rawspec

`rtl_sdr`: https://osmocom.org/projects/rtl-sdr/wiki ([Installation help](https://inst.eecs.berkeley.edu/~ee123/sp16/rtl_sdr_install.html))
