How To Guides
**************

Change grating
===========================
This feature is stil experimental, and the implementation is somehow poor. However, the method can still be used to implement a grating change.


When the ``RaypyngOphydDevices`` class is called, Ophyd devices are automatically created
.. code:: python

    from raypyng_bluesky.RaypyngOphydDevices import RaypyngOphydDevices

    # define here the path to the rml file
    rml_path = ('...rml/elisa.rml')

    RaypyngOphydDevices(RE=RE, rml_path=rml_path, temporary_folder=None, name_space=None, ray_ui_location='/home/simone/RAY-UI-development')#sys._getframe(0))

In this case we know that inside the ``elisa.rml`` file we have a plane grating monochromator, and an elment that is the a plane grating called ``PG``, 
and that an Ophyd device called ``rp_PG`` is therefore created. The gratings can hold any number of different configurations, and the configuration found in the 
rml file is saved with the name ``'default'``
We can rename the default grating to a more meaningful name, in this case since it is a 1200 lines/mm blazed grating we will call it simply '1200'
.. code:: python

    rp_PG.rename_default_grating('1200')


the second grating is a laminar grating with a pitch of 400 lines/mm. 

.. code:: python

    rrp_PG.gratings=('400', {'lineDensity':400, 
                        'orderDiffraction':1,
                        'lineProfile':'laminar',
                        'aspectAngle':90,
                        'grooveDepth':15,
                        'grooveRatio':0.65,}
                )

To change the gratings then, one can use the method implmented in the grating Ophyd device to change the grating, giving as
argument the pitch of the grating. To use the blazed grating use:

.. code:: python

    rp_PG.change_grating('1200')

while to use the laminar grating:

.. code:: python

    rp_PG.change_grating('400')


Four different kind of gratings can be implemented: ``blazed``,
``laminar``, ``sinus``, and ``unknown``. Each grating needs slightly different
parameters:

.. code:: python
    
    grating_dict_keys_blazed = {'name': 
                                    {'lineDensity':value,
                                    'orderDiffraction':value,
                                    'lineProfile':value,
                                    'blazeAngle':value,
                                    'aspectAngle':value,
                                    }
                                }
    grating_dict_keys_laminar = {'name':
                                    {'lineDensity':value,
                                    'orderDiffraction:value',
                                    'lineProfile':value,
                                    'aspectAngle':value,
                                    'grooveDepth':value,
                                    'grooveRatio':value,
                                    }
                                }
    grating_dict_keys_sinus   = {'name':
                                    {'lineDensity':value,
                                    'orderDiffraction':value,
                                    'lineProfile':value,
                                    'grooveDepth':value,
                                    }
                                }

    grating_dict_keys_unknown = {'name':
                                    {'lineDensity':value,
                                    'orderDiffraction':value,
                                    'lineProfile':value,
                                    'gratingEfficiency':value
                                    }
                                }

Write your own simulation Engine
=================================

The simulations are performed using RAY-UI on a local computer. However, in the future,
more simulation engines can be easily written, as long the following three methods are provided.


.. code:: python

    class SimulatonEngineCUSTOM():
        
        def __init__(self) -> None:
                
            pass

        def check_if_simulation_is_done(self):
            """
            When the simulation is completed and the files are correctly exported,
            this should return True, otherwise False.
            """
            pass
        
        def setup_simulation(self):
            """This function can be used to do any prelimary operatio to setup the simulations, called once per simulated point.
            """
            pass

        def simulate(self, path, rml, exports_list):
            """ This function takes care of executing the simulations, called once per simulated point.

            Once the simulations have been performed the results should be saved in the tmp folder,
            in filenames with the name: 'exports_list[i]+_analyzed_rays.dat'.
            The following arguments are passed by the RaypyngTrigger Detector, and should be accepted
            Args:

            path (str): the result of the simulation must be saved in the temporary_folder
                        os.path.join(path,'tmp')
            rml (RMLFile): an instance of the RMLFile class. Can be used to save the rml file 
                            in its latest status as a base for the simulation
            exports_list (list): list of strings indicatin the names of the Oe to be exported, 
                                typically different image planes in the beamline
            """
            pass

Your simulation engine should export in the `tmp` folder a file with the following columns and a header:

.. code:: bash

    # SourcePhotonFlux	NumberRaysSurvived	PercentageRaysSurvived	PhotonFlux	Bandwidth	HorizontalFocusFWHM	VerticalFocusFWHM
    6.934960000000000000e+12	1.000000000000000000e+04	1.000000000000000000e+02	6.934960000000000000e+12	-4.999559755833615782e-02	1.904934623550874839e+00	5.918353021235417399e-01

At the moment the detectors will extract only the `PhotonFlux`, `Bandwidth`, `HorizontalFocusFWHM`, and the `VerticalFocusFWHM`.
Since it is not clear how the program will develop in the future, even if not used save all the columns, including the not used
`SourcePhotonFlux`,	`NumberRaysSurvived`, and `PercentageRaysSurvived` (they can be zeros). 


Then the `__init__()` of the `RaypyngOphydDevices` class should be modified to accept the new simulation engine.

.. code:: python

    class RaypyngOphydDevices():
        """Create ophyd devices from a RAY-UI rml file and adds them to a name space.

        If you are using ipython ``sys._getframe(0)`` returns the name space of the ipython instance.
        (Remember to ``import sys``)

        Args:
            RE (RunEngine): Bluesky RunEngine
            rml_path (str): the path to the rml file
            temporary_folder (str): path where to create temporary folder. If None it is automatically
                                    set into the ipython profile folder. Default to None.
            name_space (frame, optional): If None the class will try to understand the correct namespace to add the Ophyd devices to.
                                        If the automatic retrieval fails, pass ``sys._getframe(0)``. Defaults to None.
            prefix (str): the prefix to prepend to the oe names found in the rml file
            ray_ui_location (str): the location of the RAY-UI installation folder. If None the program will try to find it automatically. Deafault to None.
        """    
        def __init__(self, *args, RE, rml_path, temporary_folder=None, name_space=None, prefix=None, ray_ui_location=None, simulation_engine='rayui',**kwargs):
        

            self.RE = RE
            self.rml = RMLFile(rml_path)
            simulation_engine_dict = {'rayui':SimulatonEngineRAYUI(ray_ui_location=ray_ui_location),
                                        'custom':SimulationEngineCUSTOM(*args)}

            if simulation_engine in simulation_engine_dict.keys():
                self.simulation_engine = simulation_engine_dict[simulation_engine]
            else:
                raise ValueError(f"The simulation engine '{simulation_engine}' is not yet implemented")