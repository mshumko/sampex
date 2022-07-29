# sampex
Easily load and plot data from the Solar Anomalous and Magnetospheric Particle Explorer (SAMPEX) satellite that operated from 1992-2012. This library currently downloads and loads data from the `HILT`, `PET`, and `LICA` instruments, as well as the `attitide` files.  

[Documentation](https://sampex.readthedocs.io/en/latest/)

The example plot below sums up what this library does. I generated it with this console command: ```plot_sampex 2007 1 20 --yscale log```
![Example SAMPEX data from the HILT, PET, and LICA instruments](https://github.com/mshumko/sampex/blob/aba90331438b1cc1152e99469df5a65847bc9535/sampex_example.png?raw=true)

# Install
Installing this package is as simple as
```bash
python3 -m pip install sampex
```

If you want to develop this package, run
```bash
git clone git@github.com:mshumko/sampex.git
cd sampex
```

Then one of these commands to install sampex into a virtual environment:
```bash
python3 -m pip install -e .
```
or 
```bash
python3 -m pip install -r requirements.txt 
```
# Get started
You can configure this package so it knows the top-level directory to search for (or save) the data to.

```bash
python3 -m sampex config
```
and paste the top-level SAMPEX data directory in the prompt.

## Examples
There are a handful of examples in the [documentation](https://sampex.readthedocs.io/en/latest/examples.html)