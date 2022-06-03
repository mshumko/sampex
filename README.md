# sampex
Classes to easily load SAMPEX data. So far it contains loader classes for the HILT, PET, and LICA data, as well as the Attitude data. 

**_NOTE:_** Heads up that loading some of the data, especially the state 4 HILT counts, takes a decent amount of time due to the sheer number of datetime conversions.

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
Before you can load the SAMPEX data you'll need to do two things:

1. Download the [SAMPEX data](https://izw1.caltech.edu/sampex/DataCenter/data.html) to a folder. wget is great for this. Write down the top-level SAMPEX data directory as you'll need it in step 2.
2. Configure this package as it needs to know what directory to begin searching for the SAMPEX data. 

    ```bash
    python3 -m sampex config
    ```
    and in the prompt paste the top-level SAMPEX data directory.

## Example 1: Load and plot the HILT data
```python
from datetime import datetime

import matplotlib.pyplot as plt

import sampex

day = datetime(2007, 1, 20)

h = sampex.HILT(day)
h.load()

fig, ax = plt.subplots()
ax.step(h['time'], h['counts'], label='HILT', where='post')
plt.suptitle(f'SAMPEX-HILT | {day.date()}')
plt.show()
```

## Example 2: Load and plot the PET data
```python
from datetime import datetime

import matplotlib.pyplot as plt

import sampex

day = datetime(2007, 1, 20)

p = sampex.PET(day)
p.load()

fig, ax = plt.subplots()
ax.step(p['time'], p['counts'], label='PET', where='post')
plt.suptitle(f'SAMPEX-PET | {day.date()}')
plt.show()
```

## Example 3: Load and plot the LICA data
```python
from datetime import datetime

import matplotlib.pyplot as plt

import sampex

day = datetime(2007, 1, 20)

l = sampex.LICA(day)
l.load()

fig, ax = plt.subplots()
ax.step(l['time'], l['stop'], label='PET', where='post')
plt.suptitle(f'SAMPEX-LICA (stop) | {day.date()}')
plt.show()
```

## Example 4: Load and plot the Attitude data
```python
from datetime import datetime

import matplotlib.pyplot as plt

import sampex

day = datetime(2007, 1, 20)

a = sampex.Attitude(day)
a.load()

fig, ax = plt.subplots()
ax.plot(a['time'], a['Altitude'], label='SAMPEX Altitude')
plt.suptitle(f'SAMPEX Altitude | {day.date()}')
plt.show()
```