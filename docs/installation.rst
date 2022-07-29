.. role:: python(code)
   :language: python

============
Installation
============
Installing sampex is as simple as:

.. code-block:: shell

   python3 -m pip install sampex

I've kept the library dependencies at a minimum: only numpy, pandas, and matplotlib.

Configuration
-------------
You can configure this package so it knows the top-level directory to search for (or save) the data to.

.. code-block:: shell

   python3 -m sampex config

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