from datetime import datetime

import pytest
import numpy as np

import sampex


def test_lica():
    day = datetime(2007, 1, 20)
    l = sampex.LICA(day)
    l.load()

    assert l['time'].shape[0] == 86388
    assert l['Stop'].shape[0] == 86388
    assert l['time'][0] == np.datetime64('2007-01-20T00:00:06.000000000')
    assert l['time'][-1] == np.datetime64('2007-01-21T00:00:00.000000000')

    with pytest.raises(KeyError):
        l['counts']
    return