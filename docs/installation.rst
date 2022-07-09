============
Installation
============
Installing sampex is as simple as:

.. code-block:: shell

   python3 -m pip install sampex

I've kept the library dependencies at a minimum: only numpy, pandas, and matplotlib.

Configuration
-------------
Before you can use `sampex` you'll need to

1. **Download the SAMPEX data `data`_**. Currently `sampex` doesn't download data for you, so you will need to download it yourself (via wget or something similar) and save the data directory for step 2.
2. **Configure `sampex` where to find that data.** Run `python3 -m sampex config` and answer the prompt. The configuration paths are accessible via the `sampex.config` dictionary.

.. _data: https://izw1.caltech.edu/sampex/DataCenter/data.html

======================
Developer Installation
======================

If you want to develop this package, run
.. code-block:: shell

   git clone git@github.com:mshumko/sampex.git
   cd sampex


Then one of these commands to install sampex (preferably into a virtual environment):
.. code-block:: shell

   python3 -m pip install -e .

or 
.. code-block:: shell

   python3 -m pip install -r requirements.txt 

and then follow the above configuration steps.