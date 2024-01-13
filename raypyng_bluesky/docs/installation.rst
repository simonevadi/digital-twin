Installation
*************
raypyng-bluesky will work only if using a Linux or a macOS distribution.

Install RAY-UI
--------------
Download the RAY-UI installer from  `this link
<https://www.helmholtz-berlin.de/forschung/oe/wi/optik-strahlrohre/arbeitsgebiete/ray_en.html>`_, 
and run the installer.



Install xvfb 
------------
xvfb is a virtual X11 framebuffer server that let you run RAY-UI headless

Install xvfb:

.. code-block:: bash

  sudo apt install xvfb


.. note::

  xvfb-run script is a part of the xvfb distribution and 
  runs an app on a new virtual X11 server.


Install raypyng-bluesky
-------------------------
* You will need Python 3.8 or newer. From a shell ("Terminal" on OSX), 
  check your current Python version.

  .. code-block:: bash

    python3 --version

  If that version is less than 3.8, you must update it.

  We recommend installing raypyng into a "virtual environment" so that this
  installation will not interfere with any existing Python software:

  .. code-block:: bash

    python3 -m venv ~/raypyng-bluesky-tutorial
    source ~/raypyng-bluesky-tutorial/bin/activate

  Alternatively, if you are a
  `conda <https://conda.io/docs/user-guide/install/download.html>`_ user,
  you can create a conda environment:

  .. code-block:: bash

    conda create -n raypyng-bluesky-tutorial "python>=3.8"
    conda activate raypyng-bluesky-tutorial

* Install the latest versions of raypyng and ophyd. Also, install IPython 
  (a Python interpreter designed by scientists for scientists).

  .. code-block:: bash

     python3 -m pip install --upgrade raypyng-bluesky ipython

* Start IPython:

  .. code-block:: python

     ipython --matplotlib=qt5

  The flag ``--matplotlib=qt5`` is necessary for live-updating plots to work.

  Or, if you wish you use raypyng from a Jupyter notebook, install a kernel like
  so:

  .. code-block:: python

     ipython kernel install --user --name=raypyng-bluesky-tutorial --display-name "Python (raypyng-bluesky)"

  You may start Jupyter from any environment where it is already installed, or
  install it in this environment alongside raypyng and run it from there:

  .. code-block:: python

     pip install notebook
     jupyter notebook
