from bluesky.preprocessors import (
    SupplementalData,
    baseline_wrapper,
)

from bluesky.preprocessors import (
    plan_mutator,
    single_gen,
    ensure_generator,
)

from bluesky.utils import Msg
import bluesky.plan_stubs as bps



def trigger_sim(plan, trigger_detector):
    """Trigger simulations for raypyng plans

    This function is composed of four steps:
    
    1- populate_raypyng_devices_list_at_stage:
        at the 'stage message' each device is classified
        and saved into two list. One list is dedicated to 
        raypng devices, and one for all the others
    2- prepare_simulations_at_open_run:
        when the message is 'open_run', if both raypyng 
        devices and normal devices have been staged raise 
        an exception. Otherwise the list of exports is 
        prepared(consists of detector names included in the plan) 
        and passed to the trigger detector.

    3-  insert_before_first_det_trigger:
        before the first detector is triggered, a trigger
        message for the raypyng trigger detector is inserted
        in the same group as the other detectors
    4-  cleanup_at_close_run:
        when the message is 'close_run' the simulation_done
        file is removed and the list containing the raypyng and
        other devices, created at point 1, are cleared.
    
    Args:
        plan (bluesky.plan): the plan that is being executed
        trigger_detector (RaypyngTriggerDetector): the trigger detector

    Raises:
        ValueError: if in the plan a mix of raypyng devices are other devices 
        are used raise an exeption
    """    

    # get list of detectors in the plan
    try:
        gi_detectors = plan.gi_frame.f_locals['detectors']
    except KeyError as e:
        gi_detectors = []

    # prepare list to append the raypyng objects (motors/detectors)
    raypyng_devices     = []
    non_raypyng_devices = []


    def populate_raypyng_devices_list_at_stage(msg):
        if msg.command == 'stage':      
            if hasattr(msg.obj, 'raypyng'):
                raypyng_devices.append(msg.obj)
            else:
                non_raypyng_devices.append(msg.obj) 
  
        return None, None  

    def prepare_simulations_at_open_run(msg): 
        if msg.command == 'open_run':
            if len(raypyng_devices)>0 and len(non_raypyng_devices)==0: 
                exports = [det.parent_detector_name for det in gi_detectors]
                # once we make the trigger detector a device this should use the
                # configure method, see issue #5
                trigger_detector.update_exports(exports)

            elif len(raypyng_devices)>0 and len(non_raypyng_devices)>0:
                raise ValueError(f"Do not mix raypyng devices with other devices,\n\
                    the following devices are not raypyng devices:\n {non_raypyng_devices}")
        return None, None 

    def insert_before_first_det_trigger(msg):
        if msg.command == 'trigger' and msg.obj.name == gi_detectors[0].name: 
            if len(raypyng_devices)>0 and len(non_raypyng_devices)==0: 
                group = msg.kwargs['group']
                trigger_msgs = Msg('trigger', trigger_detector, group=group)
                rayui_api = trigger_detector.setup_simulation() 
                for det in gi_detectors:
                    det.set_simulation_api(rayui_api)
                def new_gen():
                    yield from ensure_generator(trigger_msgs)
                    yield msg
                return new_gen(), None
        else:
            return None, None
    
    def cleanup_at_close_run(msg): 
        if msg.command == 'close_run':
            trigger_detector.delete_temporary_folder()
            if len(raypyng_devices)>0 and len(non_raypyng_devices)==0: 
                raypyng_devices.clear()
                non_raypyng_devices.clear()
        return None, None 


    plan1 = plan_mutator(plan, populate_raypyng_devices_list_at_stage)
    plan2 = plan_mutator(plan1, prepare_simulations_at_open_run)
    plan3 = plan_mutator(plan2, insert_before_first_det_trigger)
    plan4 = plan_mutator(plan3, cleanup_at_close_run)
    
    return (yield from plan4)

class SupplementalDataRaypyng(SupplementalData):
    """Supplemental data for raypyng.

    The Run engine is needed to be able to include the 
    trigger detector automatically

    Args:
            trigger_detector (RaypyngTriggerDetector): The detector to trigger raypyng
    """    

    def __init__(self, *args,trigger_detector, **kwargs):
        """
        Args:
            trigger_detector (RaypyngTriggerDetector): The detector to trigger raypyng
        """        
        super().__init__(*args, **kwargs)
        self.trigger_detector = trigger_detector
        
    def __call__(self, plan):
        plan = trigger_sim(plan, self.trigger_detector)
        plan = baseline_wrapper(plan, self.baseline)
        return (yield from plan)

