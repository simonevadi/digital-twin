from IPython import get_ipython
import collections
import re

class Devices:
    def __init__(self,user_ns=None):
        self._maxdepth = 10
        self._user_ns = user_ns or get_ipython().user_ns

    def resolve(self, name:str)->object:
        """get ophyd device by its name

        Args:
            name (str): name of a device

        Returns:
            object: reference to the ophydd device or None
        """
        dd = self._enumerate_devices()
        if name in dd:
            return dd[name]
        else:
            return None

    def device_name_dict(self)->object:
        """
        Get a dictionary of all known ophyd devices
        """
        return self._enumerate_devices()

    def find_devices(self, pattern:str)->dict:
        """
        Find one or more ophyd devices which name is matching the given pattern
        """
        known_devices = self._enumerate_devices()
        search_pattern = re.compile(pattern)
        return { key:value for (key,value) in known_devices.items() if search_pattern.match(key) is not None}

    ################################################################
    # Temporal code - to be better implemented
    def warn(self,*args,**kwargs):
        pass


    ################################################################
    # Generic utils - perhaps move into another level/class
    
    def is_ophyd_device(self,obj)->bool:
        """Check if given object is an OPHYD devioce

        Args:
            obj (_type_): object to check

        Returns:
            bool: True if obj is an ophyd device, false otherwise
        """
        return hasattr(obj, '_ophyd_labels_')

    def device_components(self,ophyd_device):
        """Transverse over all components of an ophyd device

        Args:
            ophyd_device (object): ophyd device to check

        Yields:
            (str, object): name of a component and object reference to it
        """
        if hasattr(ophyd_device, 'component_names'):
            component_names = ophyd_device.component_names
            for component_name in component_names:
                try:
                    component = getattr(ophyd_device,component_name)
                    yield component_name, component
                except:
                    pass


    ################################################################
    # Internal API
    def _enumerate_devices(self, element=None,maxdepth=10,name=""):
        """ find all ophyd devices in the current namespace

        Args:
            element (_type_, optional): ophyd device to lookup for subdevices or a namespace.
                                        if set to None then user namespace will be used.
                                        Defaults to None.
            maxdepth (int, optional): Max allowed recursion depth. If it is less or equal to
                                    zero then do nothing. Defaults to 10.
            name (str, optional): Name of the current ophyd component. Defaults to "".

        Returns:
            dict: dictionary with device names as keys and reference to a device as values
        """
        device_dict = dict()
        if maxdepth <= 0:
            self.warn("Reached max depth, results will be truncated")
            return device_dict

        if element is None: element = self._user_ns

        if self.is_ophyd_device(element):#hasattr(element, '_ophyd_labels_'):
            device_dict[element.name]=element
            for component_name, component in self.device_components(element):
                # add all subdevices to the list. Do it in a reverse order so that parent 
                # device record is not overwritten by a subdevice
                sd = self._enumerate_devices(component,maxdepth=maxdepth-1,name=component_name)
                sd.update(device_dict)
                device_dict = sd
        elif len(name)==0 and hasattr(element,'items'):
            for key, obj in element.items():
                try:
                    if not key.startswith('_'):# and pattern__re.match(key):
                        device_dict.update(self._enumerate_devices(obj,maxdepth=maxdepth-1,name=key))
                except Exception as e:
                    print(f"WARNING::{e}")
                    pass

        return device_dict


    def _enumerate_devices2(self, element=None,maxdepth=10,pattern=".*", prefix="",name=""):
        """ find all ophyd devices in the current namespace

        Args:
            element (_type_, optional): ophyd device to lookup for subdevices or a namespace. Defaults to None.
            maxdepth (int, optional): _description_. Defaults to 10.
            pattern (str, optional): _description_. Defaults to ".*".
            prefix (str, optional): _description_. Defaults to "".
            name (str, optional): _description_. Defaults to "".

        Returns:
            _type_: _description_
        """
        device_dict = dict()#InternalDict()#collections.defaultdict(list)
        if maxdepth <= 0:
            self.warn("Reached max depth, results will be truncated")
            return device_dict

        if element is None: element = self._user_ns

        pattern_re = None
        # if isinstance(pattern, str):
        #     pattern_re = re.compile(pattern)
        # elif isinstance(pattern, re.Pattern):
        #     pass
        # else:
        #     raise Exception("pattern must be either string or re.Pattern!")

        if self.is_ophyd_device(element):#hasattr(element, '_ophyd_labels_'):
            device_dict[element.name]=element
            for component_name, component in self.device_components(element):
                # add all subdevices to the list. Do it in a reverse order so that parent 
                # device record is not overwritten by a subdevice
                sd = self._enumerate_devices(component,maxdepth=maxdepth-1,pattern=pattern_re,prefix=prefix+"   ",name=component_name)
                sd.update(device_dict)
                device_dict = sd
        elif len(name)==0 and hasattr(element,'items'):
            for key, obj in element.items():
                try:
                    if not key.startswith('_'):# and pattern__re.match(key):
                        device_dict.update(self._enumerate_devices(obj,maxdepth=maxdepth-1,pattern=pattern_re,prefix=prefix+"",name=key))
                except Exception as e:
                    print(f"WARNING::{e}")
                    pass

        return device_dict


