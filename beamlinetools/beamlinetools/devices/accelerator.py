from ophyd import PVPositioner,EpicsMotor, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from ophyd import PseudoPositioner,PseudoSingle, PositionerBase, Signal

class BumpProperties(Device):
    """ 
    Subdevice for reading properties of an orbit bump
    """
    destination = FCpt(EpicsSignalRO, '{self.prefix}setAng',  labels={"detectors","bessy2"}, auto_monitor=True, kind='config')
    readback = FCpt(EpicsSignalRO, 'BPMZR:ang{self._segment}H',  labels={"detectors","bessy2"}, auto_monitor=True, kind='config')

    def __init__(self, prefix="", *, name, segment=None, **kwargs):
        self._segment = segment
        super().__init__(prefix, name=name, **kwargs)

class BunchProperties(Device):
    """ 
    Subdevice for reading properties of a special bunches
    """
    current = FCpt(EpicsSignalRO, '{self.prefix}rdCur{self._bunch}',  labels={"detectors","bessy2"}, auto_monitor=True, kind='hinted')
    lifetime = FCpt(EpicsSignalRO, '{self.prefix}rdLt{self._bunch}',  labels={"detectors","bessy2"}, auto_monitor=True, kind='normal')
    pos = FCpt(EpicsSignalRO, '{self.prefix}setPos{self._bunch}',  labels={"detectors","bessy2"}, auto_monitor=True, kind='config')

    def __init__(self, prefix="", *, name, bunch=None, **kwargs):
        self._bunch = bunch
        super().__init__(prefix, name=name, **kwargs)

class OrbitInformation(Device):
    """
    Information about storage ring orbit
    """
    optics  = FCpt(EpicsSignalRO,   'OPTICC:mode',      string=True,   labels={"detectors","bessy2"}, auto_monitor=True, kind='config')
    fast_orbit_correction  = FCpt(EpicsSignalRO,   'FOFBCC:stAct', string=True, labels={"detectors","bessy2"}, auto_monitor=True,  kind='config')
    slow_orbit_correction  = FCpt(EpicsSignalRO,   'RMC00V',                    labels={"detectors","bessy2"},  auto_monitor=True, kind='config')

    bump_ue49 = FCpt(BumpProperties, 'BUMPCT4R:', segment = 'T4',  labels={"detectors","bessy2"}, kind='config')
    bump_ue52 = FCpt(BumpProperties, 'ABUMPCD5R:', segment = 'D5',  labels={"detectors","bessy2"}, kind='config') 
    bump_ue56 = FCpt(BumpProperties, 'FSBUMPCR:', segment = 'D6',  labels={"detectors","bessy2"},  kind='config')
    bump_ue112 = FCpt(BumpProperties, 'ABUMPCD7R:', segment = 'D7',  labels={"detectors","bessy2"}, kind='config')

class Bunches(Device):
    '''
    All additional information about special bunches in the fill pattern
    '''
    camshaft = FCpt(BunchProperties, 'MEASURECC:CUR:',  bunch = "CS", labels={"detectors","bessy2"}, kind='normal')
    ppre1 = FCpt(BunchProperties, 'MEASURECC:CUR:',  bunch = "PPRE1", labels={"detectors","bessy2"}, kind='normal')
    ppre2 = FCpt(BunchProperties, 'MEASURECC:CUR:',  bunch = "PPRE2", labels={"detectors","bessy2"}, kind='normal')

    ptrk_x = FCpt(BunchProperties, 'MEASURECC:CUR:',  bunch = "PTrkX", labels={"detectors","bessy2"}, kind='normal')
    ptrk_y = FCpt(BunchProperties, 'MEASURECC:CUR:',  bunch = "PTrkY", labels={"detectors","bessy2"}, kind='normal')
    ptrk_z = FCpt(BunchProperties, 'MEASURECC:CUR:',  bunch = "PTrkZ", labels={"detectors","bessy2"}, kind='normal')

    slicing1 = FCpt(BunchProperties, 'MEASURECC:CUR:',  bunch = "SL1", labels={"detectors","bessy2"}, kind='normal')
    slicing2 = FCpt(BunchProperties, 'MEASURECC:CUR:',  bunch = "SL2", labels={"detectors","bessy2"}, kind='normal')
    slicing3 = FCpt(BunchProperties, 'MEASURECC:CUR:',  bunch = "SL3", labels={"detectors","bessy2"}, kind='normal')
    slicing4 = FCpt(BunchProperties, 'MEASURECC:CUR:',  bunch = "SL4", labels={"detectors","bessy2"}, kind='normal')
    slicing5 = FCpt(BunchProperties, 'MEASURECC:CUR:',  bunch = "SL5", labels={"detectors","bessy2"}, kind='normal')
    slicing6 = FCpt(BunchProperties, 'MEASURECC:CUR:',  bunch = "SL6", labels={"detectors","bessy2"}, kind='normal')
    slicing7 = FCpt(BunchProperties, 'MEASURECC:CUR:',  bunch = "SL7", labels={"detectors","bessy2"}, kind='normal') 

class TopUpMonitoring(Device):
    time_next_injection = FCpt(EpicsSignalRO,'TOPUPCC:estCntDwnS', labels={"bessy2"}, auto_monitor=False, kind='config')
    

class DetailedAccelerator(Device):
    """ 
    DetailedAccelerator provides advanced information about BESSY II operation state, including current 
    fill pattern and various details on the special bunches
    """

    current     = FCpt(EpicsSignalRO,   'MDIZ3T5G:current', kind="hinted", labels={"detectors","bessy2"}, auto_monitor = True) 
    '''ring current'''

    lifetime    = FCpt(EpicsSignalRO,   'MDIZ3T5G:lt10',    kind="config", labels={"detectors","bessy2"}, auto_monitor = True)
    '''overall life time'''

    fill        = FCpt(EpicsSignalRO,    'CUMZR:MBcurrent', kind='config',  labels={"waveform", "bessy2"}, auto_monitor = True)

    topup       = FCpt(EpicsSignalRO,   'TOPUPCC:message',  string=True,   labels={"bessy2"}, auto_monitor = True, kind='config')
    injection   = FCpt(EpicsSignalRO,   'TOPUPCC:stateName',string=True,   labels={"bessy2"}, auto_monitor = True, kind='config')
    mode        = FCpt(EpicsSignalRO,   'FPATCC:mode',      string=True,   labels={"bessy2"}, auto_monitor = True, kind='config')

    # beamshutter state
    beamshutters = FCpt(EpicsSignalRO,   'TR1SWR:stExpBSfree',   string=True,   labels={"bessy2"}, auto_monitor = True, kind='config')
    
    # Timing
    master_frequency  = FCpt(EpicsSignalRO,   'MCLKHX251C:freq',   labels={"detectors","bessy2"}, auto_monitor = True, kind='config')

    # Optics and orbit
    orbit = FCpt(OrbitInformation,      kind='config', labels={"bessy2"})

    # Special bunches
    bunches = FCpt(Bunches,             kind='config', labels={"bessy2"})

