import os
import sys
import inspect
import traceback

from raypyng.rml import RMLFile

from .devices import SimulatedPGM, SimulatedApertures, SimulatedMirror, SimulatedSource
from .detector import RaypyngDetectorDevice, RaypyngTriggerDetector
from .preprocessor import SupplementalDataRaypyng
from .simulation_engine import SimulatonEngineRAYUI, SimulatonEngineRAYUIClient



class RaypyngDictionary():
    """A class defining a dictionary of the differen elements in rayui and the classe to be used as Ophyd devices
    """    
    

    def __init__(self, *args,**kwargs):
        self._optical_elements = ['Toroid', 'PlaneMirror', 'Cylinder', 'Ellipsoid', 'Foil', 'Zoneplate', 'Cone', 'Sphere', 'Paraboloid', 'Experts Optics', 'Elliptical Toroid', 'Hyperboloid', 'Reflection Zoneplate', 'Crystal', 'Cylindrical Crystal']
        self._optical_elements_dict = {k:SimulatedMirror for k in self._optical_elements}

        self._sources = ['MatrixSource','Point Source', 'Pixel Source', 'Circle Source',  'Dipole',  'Wiggler', 'Wunder Source', 'Helical Double Undulator', 'Simple Undulator', 'Twin Orbit Point Source', 'Undulator File', 'Helical Double Undulator File', 'Source Data File']
        self._source_dict = {k:SimulatedSource for k in self._sources}

        self._gratings = ['PlaneGrating', 'Spherical Grating', 'Toroidal Grating' ]
        self._grating_dict = {k:SimulatedPGM for k in self._gratings}

        self._apertures = ['Slit', 'Aperture']
        self._aperture_dict = {k:SimulatedApertures for k in self._apertures}

        self._detectors = ['ImagePlane', 'ImagePlaneBundle']
        self._detector_dict = {k:RaypyngDetectorDevice for k in self._detectors}

        self._type_to_class_dict ={**self._optical_elements_dict, 
                            **self._source_dict, 
                            **self._grating_dict, 
                            **self._aperture_dict,
                            **self._detector_dict}
        
    @property
    def type_to_class_dict(self):
        return self._type_to_class_dict
    
    

    
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
    def __init__(self, *args, RE, rml_path, temporary_folder=None, name_space=None, prefix=None, ray_ui_location=None, ip=None, port=None, simulation_engine='rayui',**kwargs):
       

        self.RE = RE
        self.rml = RMLFile(rml_path)
        

        if prefix == None:
            self.prefix='rp_'
        else:
            self.prefix = prefix+'_'

        if simulation_engine == 'rayuiClient':
            if ip==None:
                raise ValueError(f"The simulation engine '{simulation_engine}' requires a valid ip")
            elif port==None:
                raise ValueError(f"The simulation engine '{simulation_engine}' requires a valid port")
        
        simulation_engine_dict = {'rayui':SimulatonEngineRAYUI(ray_ui_location=ray_ui_location),
                                  'rayuiClient':SimulatonEngineRAYUIClient(ip, port, self.prefix)}
        
        if simulation_engine in simulation_engine_dict.keys():
            self.simulation_engine = simulation_engine_dict[simulation_engine]
        else:
            raise ValueError(f"The simulation engine '{simulation_engine}' is not yet implemented")
        
        if temporary_folder == None:
            stack = traceback.extract_stack()
            fn = stack[-2].filename
            self.temporary_folder = os.path.join(os.path.dirname(fn), 'tmp')
        else:
            self.temporary_folder = temporary_folder        
        if name_space == None:
            filename = inspect.stack()[1].filename
            for i in inspect.stack():
                if i.filename == filename:
                    self.name_space = i.frame.f_globals
        else:
            self.name_space = name_space.f_globals



        self.ray_ui_location = ray_ui_location
        rpg = RaypyngDictionary()
        self.type_to_class_dict = rpg.type_to_class_dict
        
        self.prepend_to_oe_name()
        self.create_raypyng_elements_from_rml()
        self.create_trigger_detector()
        self.setup_trigger_detector()
        self.append_preprocessor()
    
    def prepend_to_oe_name(self):
        """Prepend a prefix to the name of all the Ophyd object created
        """        
        for oe in self.rml.beamline.children():
            oe.attributes()['name']=self.prefix+oe['name']

    def create_raypyng_elements_from_rml(self):
        """Iterate through the raypyng objects created by RMLFile and create corresponding Ophyd Devices

        Returns:
            OphydDevices: the Ophyd devices created 
        """        
        if self.name_space is None: 
            # this does not work.. I get the wrong frame, the one of the class
            self.name_space = sys._getframe(1).f_globals
        ret = ()
        for oe in self.rml.beamline.children():
            cls = self.type_to_class_dict[oe['type']]
            k = oe['name']
            if oe['type'] == 'ImagePlane':
                self.name_space[k] = cls(name=k, rml=self.rml, tmp=self.temporary_folder)
                ret = ret + (self.name_space[k],)
            else:
                self.name_space[k] = cls(obj=oe, name=k)
                ret = ret + (self.name_space[k],)
        return ret
    
    def create_trigger_detector(self):
        """Create a trigger detector called RaypyngTriggerDetector
        """        
        ret = ()
        k = 'TriggerDetector'
        cls = RaypyngTriggerDetector
        self.name_space[k] = cls(name='RaypyngTriggerDetector', rml=self.rml, temporary_folder=self.temporary_folder, simulation_api=self.simulation_engine)
        ret = ret + (self.name_space[k],)
    
    def setup_trigger_detector(self):
        TriggerDetector = self.trigger_detector()
        TriggerDetector.set_ray_ui_location(self.ray_ui_location)
        TriggerDetector.set_simulation_engine(self.simulation_engine)

    def trigger_detector(self):
        """Return the RaypyngTriggerDetector

        Returns:
            RaypyngTriggerDetector (RaypyngTriggerDetector): the trigger detector
        """        
        return self.name_space['TriggerDetector']
    
    def append_preprocessor(self):
        """Add supplemental data to the RunEngine to trigger the simulations
        """        
        TriggerDetector = self.trigger_detector()
        sd = SupplementalDataRaypyng(trigger_detector=TriggerDetector)
        self.RE.preprocessors.append(sd) 




