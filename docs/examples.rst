========
Examples
========

This example gallery using the best practices and illustrates functionality throughout `sampex`. 

Merging the HILT and Attitude data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Most often you'll need to put the instrument data in context. Here the context is the attitude data. This short example shows how you can merge the HILT and Attutude data together.

.. note::
    This example does not interpolate the attitude data, it only finds the nearest attitude timestamps within 3 seconds (the attitude data is reported every 6 seconds). This works well for many applications.

.. code:: python

    from datetime import datetime

    import pandas as pd

    import sampex

    day = datetime(2007, 1, 20)
    
    hilt = sampex.HILT(day)
    hilt.load()
    att = sampex.Attitude(day)
    att.load()

    merged = pd.merge_asof(hilt.data, att.data, left_index=True, right_index=True,
        tolerance=pd.Timedelta(seconds=3), direction='nearest')