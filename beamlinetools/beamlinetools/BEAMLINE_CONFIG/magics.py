import os 

from beamlinetools.magics.simplify_syntax import Simplify
from beamlinetools.magics.peakinfo import PeakInfoMagic
from bluesky.magics import BlueskyMagics
from beamlinetools.magics.standard_magics import BlueskyMagicsCustom


## IMPORTANT : do not change the order of the follwing two lines. 
# standard magics
get_ipython().register_magics(BlueskyMagics)

# custom magics - it will override some standard magics
get_ipython().register_magics(BlueskyMagicsCustom)

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Generate the full path to plans.py
plans_path = os.path.join(script_dir, 'plans.py')

# this is the set of agics that simplifies the syntax
simplify = Simplify(get_ipython())
simplify.autogenerate_magics(plans_path)
run_plan = simplify.execute_magic

# this are the peakinfo magics
get_ipython().register_magics(PeakInfoMagic)
# usage: peakinfo