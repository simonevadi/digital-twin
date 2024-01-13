Tutorial
********

Setup an Ipython profile
=========================
The code is thought to be used in an environment where bluesky is setup. For doing this it is convenient to create an ipython profile
and modify the startup files. An rml file created with RAY-UI containg a beamline is also needed.
The code in the following example and an rml file ready to use is available at this `link <https://github.com/hz-b/raypyng-bluesky/tree/main/examples/profile_raypyng-bluesky-tutorial>`_ 
In the startup folder of the ipython profile create a file called ``0-bluesky.py`` that contains a minimal setup of bluesky and raypyng-bluesky. 


The first part of the file contains a minimal installation of bluesky

.. code:: python

    import os
    from bluesky import RunEngine
    from raypyng_bluesky.RaypyngOphydDevices import RaypyngOphydDevices

    RE = RunEngine({})	

    # Send all metadata/data captured to the BestEffortCallback.
    from bluesky.callbacks.best_effort import BestEffortCallback
    bec = BestEffortCallback()


    # Make plots update live while scans run.
    from bluesky.utils import install_kicker
    install_kicker()

    # create a temporary database
    from databroker import Broker
    db = Broker.named('temp')
    RE.subscribe(db.insert)
    RE.subscribe(bec)

    # import the magics
    from bluesky.magics import BlueskyMagics
    get_ipython().register_magics(BlueskyMagics)

    # import plans
    from bluesky.plans import (
        relative_scan as dscan, 
        scan, scan as ascan,
        list_scan,
        rel_list_scan,
        rel_grid_scan,  rel_grid_scan as dmesh,
        list_grid_scan,
        adaptive_scan,
        rel_adaptive_scan,
        inner_product_scan            as a2scan,
        relative_inner_product_scan   as d2scan,
        tweak)
    
    # import stubs
    from bluesky.plan_stubs import (
        abs_set,rel_set,
        mv, mvr,
        trigger,
        read, rd,
        stage, unstage,
        configure,
        stop)

The last part contains the the two lines of code used to create RaypyngOphyd devices. See the API documentation for 
more details about ``RaypyngOphydDevices``. If you already have an ipython profile with Bluesky you can just add these lines.

.. code:: python

    # insert here the path to the rml file that you want to use
    rml_path = '...rml/elisa.rml'

    RaypyngOphydDevices(RE=RE, rml_path=rml_path, temporary_folder=None, name_space=None, prefix=None, ray_ui_location=None)


The ipython profile can be started using:

.. code:: python

    ipython --profile=raypyng-bluesky-tutorial --matplotlib=qt5

All the elements present in the rml file as ophyd devices. If you set ``prefix=None``, the prefix ``rp_`` is automatically
prepended to the name of the optical elements found in the rml file to create the dame of the object in python. If you have a Dipole called 
``Dipole``, then the name would be: ``rp_Dipole``. You can now use the simulated motors as you would normally do in bluesky.

To see a list of the implemented motors and detectors use the ipython autocompletion by typing in the ipython shell

.. code:: python

    rp_

and pressing ``tab``.

What can go wrong, and how to correct it
=========================================

If once you setup the ipython profile as explained in the section above no elements are found, might be that the ``RaypyngOphydDevices`` 
class fails to insert the ophyd devices in the correct namespace. In this case try to call the classes passing explicitly the correct namespace
like this:

.. code:: python

    import sys
    RaypyngOphydDevices(RE=RE, rml_path=rml_path, temporary_folder=None, name_space=sys._getframe(0), prefix=None, ray_ui_location=None)


If when you start a scan (see section below in this tutorial), RAY-UI is not found, it is because you installed it in a non-standard location. 
In this case simply pass the absolute path of the folder where you installed RAY-UI to the class:

.. code:: python

    ray_path = ... # here the path to RAY-UI folder
    RaypyngOphydDevices(RE=RE, rml_path=rml_path, temporary_folder=None, name_space=None, prefix=None, ray_ui_location=ray_path)


RaypyngOphyd - Motors
======================
Presently only a subset of the parameters available in rml file in RAY-UI are implemented as motor axes. To see which ones are available, 
use the tab-autocompletion. For instance, to see what axes are available for the motor ``rp_Dipole`` write in the ipython shell:

.. code:: python

    rp_Dipole.

and press tab: among the other things you will see that are implemented ``rp_Dipole.nrays``, the number of rays to use in the simulation,  
and ``p_Dipole.en``, the photon energy in eV. You can of course also use the ``.get()`` and ``.set()`` methods:

.. code:: python

    In [1]: rp_Dipole.en.get()
    Out[1]: 1000.0

    In [2]: rp_Dipole.en.set(1500)
    Out[2]: <ophyd.sim.NullStatus at 0x7fbf4c25adc0>

    In [3]: rp_Dipole.en.get()
    Out[3]: 1500.0
    
For a complete description of the axis available for each optical element see the `API documentation <https://raypyng-bluesky.readthedocs.io/en/latest/API.html#id1>`_ 

RaypyngOphyd - Detectors
=========================

When an ``ImagePlane``, or an ``ImagePlaneBundle`` is found in the rml file, a detector is created. Each detector 
can return four properties of the x-ray beam. For instance, for the ``DetectorAtFocus``:
- ``rp_DetectorAtFocus.intensity``: the intensity [Ph/s/A/BW]
- ``rp_DetectorAtFocus.bw``: the bandwidth  [eV]
- ``rp_DetectorAtFocus.hor_foc``: the horizontal focus [um]
- ``rp_DetectorAtFocus.ver_foc``: the vertical focus [um]


A scan in Bluesky
=========================
It is possible to do scan using the simulation engine RAY-UI as it is normally done in bluesky.
For instance you can scan the photon energy and see the intensity at the source and and the sample position. 
While at the beamline to change the energy we would simply ask the monochromator to do it, for the simulations 
one needs to change the energy of the source

.. code:: python

    RE(scan([rp_DetectorAtSource.intensity,rp_DetectorAtFocus.intensity], rp_Dipole.en, 200, 2200, 11))


