=============
API Reference
=============


.. note::
    `sampex` handles the time conversions from second-of-day and day-of-year to `pandas.Timestamp` automatically. The time units are `pandas.Timestamp`, but you can lso use times in the `datetime.datetime` format to load the data.


Summary
=======

.. autosummary::
   :nosignatures:

   sampex.load.HILT
   sampex.load.PET
   sampex.load.LICA
   sampex.load.Attitude
   sampex.load.date2yeardoy
   sampex.load.yeardoy2date


Load
====

.. automodule:: sampex.load
   :members: HILT, PET, LICA, Attitude, date2yeardoy, yeardoy2date
   :undoc-members:
   :show-inheritance:

Plot
====

.. automodule:: sampex.plot_sampex
   :members:
   :undoc-members:
   :show-inheritance: