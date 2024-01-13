# These are experimental IPython magics, providing quick shortcuts for simple
# tasks. None of these save any data.

# To use, run this in an IPython shell:
# ip = get_ipython()
# ip.register_magics(BlueskyMagicsSimo)

import asyncio
import warnings
# from bluesky.utils import ProgressBarManager
from beamlinetools.utils.pbar_bessy import ProgressBarManager
from bluesky import RunEngine, RunEngineInterrupted
from IPython.core.magic import Magics, magics_class, line_magic
from traitlets import MetaHasTraits
import numpy as np
import collections
from datetime import datetime
from operator import attrgetter
import bluesky.plans as bp
import bluesky.plan_stubs as bps

from IPython import get_ipython
user_ns = get_ipython().user_ns



try:
    # cytools is a drop-in replacement for toolz, implemented in Cython
    from cytoolz import partition
except ImportError:
    from toolz import partition


# This is temporarily here to allow for warnings to be printed
# we changed positioners to a property but since we never instantiate
# the class we need to add this
class MetaclassForClassProperties(MetaHasTraits, type):
    @property
    def positioners(self):
        if self._positioners:
            warnings.warn("BlueskyMagics.positioners is deprecated. "
                          "Please use the newer labels feature.")
        return self._positioners

    @positioners.setter
    def positioners(self, val):
        warnings.warn("BlueskyMagics.positioners is deprecated. "
                      "Please use the newer labels feature.")
        self._positioners = val

    @property
    def detectors(self):
        if self._detectors:
            warnings.warn("BlueskyMagics.detectors is deprecated. "
                          "Please use the newer labels feature.")
        return self._detectors

    @detectors.setter
    def detectors(self, val):
        warnings.warn("BlueskyMagics.detectors is deprecated. "
                      "Please use the newer labels feature.")
        self._detectors = val

    _positioners = []
    _detectors = []


@magics_class
class BlueskyMagicsCustom(Magics, metaclass=MetaclassForClassProperties):
    """
    IPython magics for bluesky.

    To install:

    >>> ip = get_ipython()
    >>> ip.register_magics(BlueskyMagics)

    Optionally configure default detectors and positioners by setting
    the class attributes:

    * ``BlueskyMagics.detectors``
    * ``BlueskyMagics.positioners``

    For more advanced configuration, access the magic's RunEngine instance and
    ProgressBarManager instance:

    * ``BlueskyMagics.RE``
    * ``BlueskyMagics.pbar_manager``
    """
    RE = RunEngine({}, loop=asyncio.new_event_loop())
    pbar_manager = ProgressBarManager()

    def _ensure_idle(self):
        if self.RE.state != 'idle':
            print('The RunEngine invoked by magics cannot be resumed.')
            print('Aborting...')
            self.RE.abort()

    @line_magic
    def mov(self, line):
        if len(line.split()) % 2 != 0:
            raise TypeError("Wrong parameters. Expected: "
                            "%mov motor position (or several pairs like that)")
        args = []
        for motor, pos in partition(2, line.split()):
            args.append(eval(motor, self.shell.user_ns))
            args.append(eval(pos, self.shell.user_ns))
        plan = bps.mv(*args)
        self.pbar_manager.user_ns=self.shell.user_ns
        self.RE.waiting_hook = self.pbar_manager
        try:
            self.RE(plan)
        except RunEngineInterrupted:
            ...
        self.RE.waiting_hook = None
        self._ensure_idle()
        return None

    @line_magic
    def cen(self, line):
        run       = user_ns['client'][-1]
        detector  = run.metadata['start']['detectors'][0]
        motor     = run.metadata['start']['motors'][0]
        parent_finder = run.metadata['start']['plan_args']['args'][0]
        parent     = find_parent(parent_finder)
        motor_axis = motor.replace(parent+'_', '.')
        peak_dict = user_ns['bec'].peaks
        mot_pos   = peak_dict['cen'][detector]
        print('Moving motor', motor, 'to position', mot_pos)
        plan = bps.mv(eval('user_ns[parent]'+motor_axis),mot_pos)
        self.RE.waiting_hook = self.pbar_manager
        try:
            self.RE(plan)
        except RunEngineInterrupted:
            ...
        self.RE.waiting_hook = None
        self._ensure_idle()
        print('Done')
        
        
    @line_magic
    def pic(self, line):
        run       = user_ns['client'][-1]
        detector  = run.metadata['start']['detectors'][0]
        motor     = run.metadata['start']['motors'][0]
        parent_finder = run.metadata['start']['plan_args']['args'][0]
        parent     = find_parent(parent_finder)
        motor_axis = motor.replace(parent+'_', '.')
        peak_dict = user_ns['bec'].peaks
        mot_pos   = peak_dict['max'][detector][0]
        print('Moving motor', motor, 'to position', mot_pos)
        plan = bps.mv(eval('user_ns[parent]'+motor_axis),mot_pos)
        self.RE.waiting_hook = self.pbar_manager
        try:
            self.RE(plan)
        except RunEngineInterrupted:
            ...
        self.RE.waiting_hook = None
        self._ensure_idle()
        print('Done')

    FMT_PREC = 6

    @line_magic
    def ct(self, line):
        # If the deprecated BlueskyMagics.detectors list is non-empty, it has
        # been configured by the user, and we must revert to the old behavior.
        if type(self).detectors:
            if line.strip():
                dets = eval(line, self.shell.user_ns)
            else:
                dets = type(self).detectors
        else:
            # new behaviour
            devices_dict = get_labeled_devices(user_ns=self.shell.user_ns)
            if line.strip():
                if '[' in line or ']' in line:
                    raise ValueError("It looks like you entered a list like "
                                     "`%ct [motors, detectors]` "
                                     "Magics work a bit differently than "
                                     "normal Python. Enter "
                                     "*space-separated* labels like "
                                     "`%ct motors detectors`.")
                # User has provided a white list of labels like
                # %ct label1 label2
                labels = line.strip().split()
            else:
                labels = ['detectors']
            dets = []
            for label in labels:
                dets.extend(obj for _, obj in devices_dict.get(label, []))
        plan = bp.count(dets)
        print("[This data will not be saved. "
              "Use the RunEngine to collect data.]")
        # Get the current date and time
        current_datetime = datetime.now()
        # Format the date and time in European format
        formatted_datetime = current_datetime.strftime("%A, %d/%m/%Y %H:%M:%S")
        # Print the formatted date and time
        print(f"Date and Time: {formatted_datetime}")
        try:
            self.RE(plan, _ct_callback)
        except RunEngineInterrupted:
            ...
        self._ensure_idle()
        return None

    FMT_PREC = 6

    @line_magic
    def wa(self, line):
        "List positioner info. 'wa' stands for 'where all'."
        # If the deprecated BlueskyMagics.positioners list is non-empty, it has
        # been configured by the user, and we must revert to the old behavior.
        if type(self).positioners:
            if line.strip():
                positioners = eval(line, self.shell.user_ns)
            else:
                positioners = type(self).positioners
            if len(positioners) > 0:
                _print_positioners(positioners, precision=self.FMT_PREC)
        else:
            # new behaviour
            devices_dict = get_labeled_devices(user_ns=self.shell.user_ns)
            if line.strip():
                if '[' in line or ']' in line:
                    raise ValueError("It looks like you entered a list like "
                                     "`%wa [motors, detectors]` "
                                     "Magics work a bit differently than "
                                     "normal Python. Enter "
                                     "*space-separated* labels like "
                                     "`%wa motors detectors`.")
                # User has provided a white list of labels like
                # %wa label1 label2
                labels = line.strip().split()
            else:
                # Show all labels.
                labels = list(devices_dict.keys())
            for label in labels:
                headers = ['Positioner', 'Value']
                LINE_FMT = '{: <30} {: <11} '
                lines = []
                lines.append(LINE_FMT.format(*headers))
                try:
                    devices_dict[label]
                except KeyError:
                    print('<no matches for this label>')
                    continue
                if label == 'detectors' or label == 'motors' or label == 'keithley':
                    continue
                elif label == "pgm":   # manual patch for pgm, labels do not show up                    
                    print()
                    print(label)
                    device         = devices_dict[label]
                    device_name    = device[0].name
                    #device_name    = device_name.partition('.')[0]
                    attribute_pgm  = ["en","grating","beta","theta", "cff"]
                    for attrib in attribute_pgm:
                        axis_name, axis_value = get_axis_pgm_emil(device_name, attrib)
                        lines.append(LINE_FMT.format(axis_name , axis_value))
                    print('\n'.join(lines))
                    continue
                print()
                print(label)
                for n,device in enumerate(devices_dict[label]):
                    device_name, device_value = get_axis(device)
                    device_name = device_name.replace("_", ".")
                    lines.append(LINE_FMT.format(device_name , device_value))
                print('\n'.join(lines))



    
def get_axis(device):
    try:
        if isinstance(device[1].get(), (int, float, complex, str)):
            #print(device[0], device[1].get())
            axis_name  = device[0]
            axis_value = device[1].get()
        else:
            #print(device[1].name , device[1].readback.get())
            axis_name  = device[1].name
            axis_value = device[1].readback.get()
    except:
        axis_value = 'Disconnected'
    return axis_name, axis_value
    
def get_axis_pgm_emil(device_name,attribute_pgm):
    axis_name = device_name+"."+attribute_pgm
    try:
        if attribute_pgm == "en":
            axis_value   = user_ns[device_name].en.get()
        elif attribute_pgm == 'grating':
            axis_value   = user_ns[device_name].grating.get()
        elif attribute_pgm == 'beta':
            axis_value   = user_ns[device_name].beta.get()
        elif attribute_pgm == 'theta':
            axis_value   = user_ns[device_name].theta.get()
        elif attribute_pgm == 'cff':
            axis_value   = user_ns[device_name].cff.get()
        elif attribute_pgm == 'grating_800_temp':
            axis_value   = user_ns[device_name].grating_800_temp.get()
        elif attribute_pgm == 'grating_400_temp':
            axis_value   = user_ns[device_name].grating_400_temp.get()
        elif attribute_pgm == 'mirror_temp':
            axis_value   = user_ns[device_name].mirror_temp.get()
        else:
            raise ValueError('This axis does not exist and must be manually added to the get_axis_pgm_emil() function')
    except Exception as e:
        # print(f'exception {e}')
        axis_value = 'Disconnected'
    return axis_name, axis_value


def get_labeled_devices(user_ns=None, maxdepth=8):
    ''' Returns dict of labels mapped to devices with that label

        Parameters
        ----------
        user_ns : dict, optional
            The namespace to search on
            Default is to grab the namespace of the ipython shell.

        maxdepth: int, optional
            max recursion depth

        Returns
        -------
            A dictionary of (name, ophydobject) tuple indexed by device label.

        Examples
        --------
        Read devices labeled as motors:
            objs = get_labeled_devices()
            my_motors = objs['motors']
    '''
    pgm_present = False
    
    # could be set but lists are more common for users
    obj_list = collections.defaultdict(list)

    if maxdepth <= 0:
        warnings.warn("Recursion limit exceeded. Results will be truncated.")
        return obj_list

    if user_ns is None:
        from IPython import get_ipython
        user_ns = get_ipython().user_ns

    for key, obj in user_ns.items():
        # ignore objects beginning with "_"
        # (mainly for ipython stored objs from command line
        # return of commands)
        # also check its a subclass of desired classes
        
        if not key.startswith("_"):
            if hasattr(obj, '_ophyd_labels_'):
                # don't inherit parent labels
                labels = obj._ophyd_labels_
                for label in labels:
                    obj_list[label].append((key, obj))

                if is_parent(obj):
                    # Get direct children (not grandchildren).
                    try:
                        children = {k: getattr(obj, k)
                                # obj might be a Signal (no read_attrs).
                                for k in getattr(obj, 'read_attrs', [])
                                if '.' not in k}
                        # Recurse over all children.
                        for c_key, v in get_labeled_devices(
                                user_ns=children,
                                maxdepth=maxdepth-1).items():
                            items = [('.'.join([key, ot[0]]), ot[1]) for ot in v]
                            obj_list[c_key].extend(items)
                    except Exception as e:
                        if obj.name == 'pgm':
                            pgm_present = True
                            pgm_obj = obj
                            obj_list['pgm'].append(obj)
                        else:
                            print(f'########################################')
                            print(f'problem with obj {obj.name}')
                            print(f"the following Exception was raised: {e} ")

    # Convert from defaultdict to normal dict before returning.
    label_obj_dict = {k: sorted(v) for k, v in obj_list.items()}
    # if pgm_present:
    #     label_obj_dict["pgm"] = pgm_obj
    return label_obj_dict


def is_parent(dev):
    # return whether a node is a parent
    # should not have component_names, or if yes, should be empty
    # read_attrs needed to check it's an instance and not class itself
    return (not isinstance(dev, type) and getattr(dev, 'component_names', []))


def _ct_callback(name, doc):
    if name != 'event':
        return
    for k, v in doc['data'].items():
        print('{: <30} {}'.format(k, v))

def find_parent(string):
    index = string.find("parent='") + 8
    counter=0
    for i in string[index:]:
        if counter == 0:
            parent=i
            counter += 1
        elif i == "'":
            return parent
        else:
            parent += i