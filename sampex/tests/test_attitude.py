from datetime import datetime

import pytest
import numpy as np

import sampex


def test_lica():
    day = datetime(2007, 1, 20)
    a = sampex.Attitude(day)
    a.load()

    assert a['time'].shape[0] == 374399
    assert a['L_Shell'].shape[0] == 374399
    assert a['time'][0] == np.datetime64('2007-01-03T00:00:07.000000000')
    assert a['time'][-1] == np.datetime64('2007-01-29T23:59:59.000000000')

    with pytest.raises(KeyError):
        a['counts']
    return