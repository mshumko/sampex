from datetime import datetime

import pytest
import numpy as np

import sampex


def test_pet():
    day = datetime(2007, 1, 20)
    p = sampex.PET(day)
    p.load()

    assert p['time'].shape[0] == 664800
    assert p['counts'].shape[0] == 664800
    assert p['time'][0] == np.datetime64('2007-01-20T00:00:03.000000000')
    assert p['time'][-1] == np.datetime64('2007-01-21T00:00:33.900000000')

    with pytest.raises(KeyError):
        p['P1']
    return