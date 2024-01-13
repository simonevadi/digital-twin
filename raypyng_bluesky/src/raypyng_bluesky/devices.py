from ophyd.device import Device
from ophyd import Component as Cpt


from .axes import SimulatedAxisSource, SimulatedAxisMisalign 
from .axes import SimulatedAxisAperture, SimulatedAxisGrating
from .axes import SimulatedAxisReflectingElement

class MisalignComponents(Device):
    """Define the misalignment components of an optical element
    using SimulatedAxisMisalign
    """    
    raypyng  = True
    tx       = Cpt(SimulatedAxisMisalign, name="translationXerror", kind='normal')
    ty       = Cpt(SimulatedAxisMisalign, name="translationYerror", kind='normal')
    tz       = Cpt(SimulatedAxisMisalign, name="translationZerror", kind='normal')
    rx       = Cpt(SimulatedAxisMisalign, name="rotationXerror", kind='normal')
    ry       = Cpt(SimulatedAxisMisalign, name="rotationYerror", kind='normal')
    rz       = Cpt(SimulatedAxisMisalign, name="rotationZerror", kind='normal')
        
    def __init__(self, *args, obj, **kwargs):
        super().__init__(*args, **kwargs)
        self.tx.set_axis(obj=obj, axis="translationXerror")
        self.ty.set_axis(obj=obj, axis="translationYerror")
        self.tz.set_axis(obj=obj, axis="translationZerror")
        self.rx.set_axis(obj=obj, axis="rotationXerror")
        self.ry.set_axis(obj=obj, axis="rotationYerror")
        self.rz.set_axis(obj=obj, axis="rotationZerror")

class SimulatedPGM(MisalignComponents):
    """Define the Plan Grating Monochromator using SimulatedAxisMisalign
    and SimulatedAxisGrating.

    Additionaly defines a two dictionaries to store different grating parameters
    and a method  ``change_grating()`` to switch between them.
    """    
    raypyng  = True
    cff               = Cpt(SimulatedAxisGrating, name='cFactor')
    lineDensity       = Cpt(SimulatedAxisGrating, name='lineDensity')
    orderDiffraction  = Cpt(SimulatedAxisGrating, name='orderDiffraction')
    lineProfile       = Cpt(SimulatedAxisGrating, name='lineProfile')
    blazeAngle        = Cpt(SimulatedAxisGrating, name='blazeAngle')
    aspectAngle       = Cpt(SimulatedAxisGrating, name='aspectAngle')
    grooveDepth       = Cpt(SimulatedAxisGrating, name='grooveDepth')
    grooveRatio       = Cpt(SimulatedAxisGrating, name='grooveRatio')
    _gratings          = None
    grating_dict_keys_blazed = ['lineDensity',
                                'orderDiffraction',
                                'lineProfile',
                                'blazeAngle',
                                'aspectAngle',
                                ]
    grating_dict_keys_laminar = ['lineDensity',
                                'orderDiffraction',
                                'lineProfile',
                                'aspectAngle',
                                'grooveDepth',
                                'grooveRatio',
                                ]
    grating_dict_keys_sinus   = ['lineDensity',
                                'orderDiffraction',
                                'lineProfile',
                                'grooveDepth',
                                ]

    grating_dict_keys_unknown = ['lineDensity',
                                'orderDiffraction',
                                'lineProfile',
                                'gratingEfficiency'
                                ]
    gratings_dict = {'blazed':grating_dict_keys_blazed,
                    'laminar': grating_dict_keys_laminar,
                    'sinus': grating_dict_keys_sinus,
                    'unknown':grating_dict_keys_unknown,}


    @property
    def gratings(self):
        return self._gratings
    
    @gratings.setter
    def gratings(self,name_and_dict_tuple):
        """Any additional grating can be added here

        Args:
            name_and_dict_tuple (touple):  touple made of the name of the grating (str)
                                            and a dictionary that contains the 
                                            parameters of the grating. See the 'How to' 
                                            section of the documentation.
        """        
        name, grat_dict = name_and_dict_tuple
        self._check_grating_dict(name, grat_dict)
        self.gratings[name] = grat_dict

    def _check_grating_dict(self, name, grat_dict):
        keysList = list(grat_dict.keys())
        grating_dict_keys = self.gratings_dict[grat_dict['lineProfile']]
        if not sorted(keysList) == sorted(grating_dict_keys):
            raise ValueError (f"In the dictionary for the grating '{name}' these and onl these elements must be included\n{grating_dict_keys}")

    def __init__(self, *args, obj, **kwargs):
        super().__init__(*args,obj=obj, **kwargs)
        self.cff.set_axis(obj=obj, axis="cFactor")
        self.lineDensity.set_axis(obj=obj, axis="lineDensity")
        self.orderDiffraction.set_axis(obj=obj, axis="orderDiffraction")
        self.lineProfile.set_axis(obj=obj, axis="lineProfile")
        self.blazeAngle.set_axis(obj=obj, axis="blazeAngle")
        self.aspectAngle.set_axis(obj=obj, axis="aspectAngle")
        self.grooveDepth.set_axis(obj=obj, axis="grooveDepth")
        self.grooveRatio.set_axis(obj=obj, axis="grooveRatio")
        self._setup_default_grating()

    def _setup_default_grating(self):
        self._gratings = {'default': 
                            {'lineDensity':self.lineDensity.get(),
                            'orderDiffraction':self.orderDiffraction.get(),
                            'lineProfile': self.lineProfile.get(),
                            'blazeAngle':self.blazeAngle.get(),
                            'aspectAngle': self.aspectAngle.get(),
                            'grooveDepth':self.grooveDepth.get(),
                            'grooveRatio':self.grooveRatio.get(),
                            }
                        }

    def rename_default_grating(self, new_name):
        """Rename the default grating

        Args:
            new_name (str): the new name for the default grating
        """        
        self.gratings[new_name] = self.gratings.pop('default')

    def rename_grating(self, new_name, old_name):
        """Rename any grating

        Args:
            new_name (str): the new name for the default grating
            old_name (str): the old name of the grating
        """        
        self.gratings[new_name] = self.gratings.pop(old_name)

    
    def change_grating(self, grating_name):
        """Change between gratings based on the line density

        Args:
            grating_name (str): the name you of the grating you want to use
        """        
        if grating_name not in self.gratings.keys():
            raise ValueError('This grating does not exists')
        
        grating = self.gratings[grating_name]

        self.lineDensity.set(grating['lineDensity'])
        self.orderDiffraction.set(grating['orderDiffraction'])
        self.lineProfile.set(grating['lineProfile'])

        if grating['lineProfile']=='blaze':
            self.blazeAngle.set(grating['blazeAngle'])
            self.aspectAngle.set(grating['aspectAngle'])
        elif grating['lineProfile']=='laminar':
            self.aspectAngle.set(grating['aspectAngle'])
            self.grooveDepth.set(grating['grooveDepth'])
            self.grooveRatio.set(grating['grooveRatio'])
        elif grating['lineProfile']=='sinus':
            self.blazeAngle.set(grating['grooveDepth'])
        elif grating['lineProfile']=='unknown':
            self.blazeAngle.set(grating['gratingEfficiency'])
        
        
        
class SimulatedApertures(MisalignComponents):
    """Define the apertures using SimulatedAxisMisalign
    and SimulatedAxisAperture.
    """   
    raypyng  = True
    width    = Cpt(SimulatedAxisAperture, name="totalWidth", kind='normal')
    height   = Cpt(SimulatedAxisAperture, name="totalHeight", kind='normal')
        
    def __init__(self, *args, obj, **kwargs):
        super().__init__(*args,obj=obj, **kwargs)
        self.width.set_axis(obj=obj, axis="totalWidth")
        self.height.set_axis(obj=obj, axis="totalHeight")


class SimulatedMirror(MisalignComponents):
    """Define the mirrors using SimulatedAxisMisalign.
    """   
    raypyng  = True
    grazingIncAngle  = Cpt(SimulatedAxisReflectingElement, name="grazingIncAngle", kind='normal')
    azimuthalAngle  = Cpt(SimulatedAxisReflectingElement, name="azimuthalAngle", kind='normal')

    def __init__(self, *args, obj, **kwargs):
        super().__init__(*args,obj=obj, **kwargs)
        self.grazingIncAngle.set_axis(obj=obj, axis="grazingIncAngle")
        self.azimuthalAngle.set_axis(obj=obj, axis="azimuthalAngle")


          

class SimulatedSource(Device):
    """Define the source using SimulatedAxisSource.
    """   
    raypyng   = True
    en        = Cpt(SimulatedAxisSource, name="source_en", kind='normal')
    nrays     = Cpt(SimulatedAxisSource, name="source_nrays", kind='normal')
    bandwidth = Cpt(SimulatedAxisSource, name="source_bandwidth", kind='normal')
        
    def __init__(self, *args, obj, **kwargs):
        super().__init__(*args, **kwargs)
        self.en.set_axis(obj=obj, axis="photonEnergy")  
        self.nrays.set_axis(obj=obj, axis="numberRays")
        self.bandwidth.set_axis(obj=obj, axis="energySpread")