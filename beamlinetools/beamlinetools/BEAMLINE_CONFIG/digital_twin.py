import os 
from raypyng_bluesky.RaypyngOphydDevices import RaypyngOphydDevices
from .base import RE

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Go three levels up
for _ in range(3):
    script_dir = os.path.dirname(script_dir)

# Define the correct file path relative to the new directory
rml_file_name = 'PlaneMirror.rml'
rml_path = os.path.join(script_dir, 'rml', rml_file_name)
# insert here the path to the rml file that you want to use

RaypyngOphydDevices(RE=RE, rml_path=rml_path, temporary_folder=None, name_space=None, prefix=None, ray_ui_location=None)