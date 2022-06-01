from datetime import datetime

import matplotlib.pyplot as plt

from sampex import HILT, PET, LICA, Attitude

day = datetime(2007, 1, 20)

p = PET(day)
p.load()

h = HILT(day)
h.resolve_counts_state4()
# a = Load_Attitude(day)

l = LICA(day)
l.load()

fig, ax = plt.subplots(3, sharex=True)
ax[0].step(h.hilt_resolved.index, h.hilt_resolved.counts, label='HILT', where='post')
ax[1].step(p.data.index, p.data['P1_Rate'], label='PET', where='post')
ax[2].step(l.data.index, l.data['Stop'], label='LICA/Stop', where='post')

ax[0].set(ylabel='HILT')
ax[1].set(ylabel='PET')
ax[2].set(ylabel='LICA/Stop')
ax[-1].set_xlabel('Time')

plt.suptitle(f'SAMPEX | {day.date()}')
plt.show()