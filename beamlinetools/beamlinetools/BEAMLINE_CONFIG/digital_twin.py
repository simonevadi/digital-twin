from raypyng_bluesky.RaypyngOphydDevices import RaypyngOphydDevices
from .base import RE

# insert here the path to the rml file that you want to use
rml_path = '/home/simone/projects/raypyng/rml/PlaneMirror.rml'

RaypyngOphydDevices(RE=RE, rml_path=rml_path, temporary_folder=None, name_space=None, prefix=None, ray_ui_location=None)