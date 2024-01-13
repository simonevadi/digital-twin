import sys
sys.path.insert(1, '../src')
from raypyng.rml import RMLFile

from raypyng_bluesky.devices import SimulatedPGM, SimulatedApertures, SimulatedMirror, SimulatedSource
from raypyng_bluesky.detector import RaypyngDetectorDevice
rml = RMLFile('raypyng_bluesky/examples/rml/elisa.rml')

mirrors = ['Toroid', 'PlaneMirror', 'Cylinder', 'Ellipsoid']
mirror_dict = {k:SimulatedMirror for k in mirrors}

sources = ['Dipole']
source_dict = {k:SimulatedSource for k in sources}

monos = ['PlaneGrating']
mono_dict = {k:SimulatedPGM for k in monos}

apertures = ['Slit']
aperture_dict = {k:SimulatedApertures for k in apertures}

detectors = ['ImagePlane']
detector_dict = {k:RaypyngDetectorDevice for k in detectors}

type_dictionries ={**mirror_dict, 
                    **source_dict, 
                    **mono_dict, 
                    **aperture_dict,
                    **detector_dict}

for oe in rml.beamline.children():
    print(oe['name'], oe['type'])

temporary_folder = ('raypyng_bluesky/temp')

def create_instance(rml=None, tmp=temporary_folder):
    ret = ()
    for oe in rml.beamline.children():
        cls = type_dictionries[oe['type']]
        k = oe['name']
        print(k, cls, tmp)
        if oe['type'] == 'ImagePlane':
            globals()[k] = cls(name=k, rml=rml, tmp=tmp)
            ret = ret + (globals()[k],)
        else:
            globals()[k] = cls(obj=oe, name=k)
            ret = ret + (globals()[k],)
    return ret

