from datetime import datetime

import pytest
import numpy as np

import sampex


def test_hilt_state1():
    day = datetime(1992, 10, 4)
    warning_str = 'The SAMPEX HILT data is not in order for 1992278.'
    
    h = sampex.HILT(day)
    with pytest.warns(UserWarning, match=warning_str):
        h.load()
    assert h.state == 1
    assert h['time'].shape[0] == 536700
    assert h['SSD1'].shape[0] == 536700
    assert h['time'][0] == np.datetime64('1992-10-04T00:00:05.000000000')
    assert h['time'][-1] == np.datetime64('1992-10-04T23:21:18.900000000')

    with pytest.raises(IndexError):
        h['counts']
    return

def test_hilt_state4():
    day = datetime(1999, 8, 17)

    h = sampex.HILT(day)
    h.load()

    assert h['time'].shape[0] == 4320000
    assert h['counts'].shape[0] == 4320000
    assert h['time'][0] == np.datetime64('1999-08-17T00:00:02.000000000')
    assert h['time'][-1] == np.datetime64('1999-08-18T00:00:02.980000000')

    with pytest.raises(KeyError):
        h['SSD']
        h['SSD1']
    return