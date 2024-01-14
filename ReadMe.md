
# Digital Twin

## Introduction
This is the project used to develop the digital-twin project. 

## Getting Started
Run the `install.sh` script. The script is doing the followng:
1. Create a python environment called .venv 
2. install `xvfb`, a library used to hide the graphical user interface of RAY-UI.
3. Update the submodules `raypyng` and `raypyng-bluesky` 
4. Install in `raypyng`, `raypyng-bluesky`, and `beamlinetools` in `.venv` with the flag -e (the changes done in the source code of the three packages will be immediately available in ipython/python)
5. Install ipython

Make sure you have RAY-UI installed, possibly in the home folder.

## Bluesky
We use bluesky via an ipython profile, in this case `profile_raypyng`. Normally in the startup folder of an ipython profile there are files that are loaded before running the ipython session. In this case the startup file is loading the content of `beamlinetools/BEAMLINE_CONFIG`. 

The digital twin is configured in the file `beamlinetools/BEAMLINE_CONFIG/digital_twin.py`. The rml file that is loaded is in the rml folder in this project.

![Diagram](diagram.pdf)


## Usage
Start the ipython profile by running `./start.sh`
