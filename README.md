# sampex
Programs to download and load SAMPEX data. So far it contains loader classes for the HILT, PET, and LICA data, as well as the Attitude files. 

# Install
```bash
git clone git@github.com:mshumko/sampex.git
cd project_template

# Then one of these (see comment in requirement.txt):
python3 -m pip install -e .
```
or 
```bash
python3 -m pip install -r requirements.txt 
```
# Get started
To load the SAMPEX data you'll need to do two things:

1. Download the SAMPEX data to a folder. wget is great for this. Write down the top-level SAMPEX data directory as you'll need it in step 2.
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