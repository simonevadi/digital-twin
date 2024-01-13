from beamlinetools.magics.simplify_syntax import Simplify
from beamlinetools.magics.peakinfo import PeakInfoMagic
from bluesky.magics import BlueskyMagics
from beamlinetools.magics.standard_magics import BlueskyMagicsCustom


## IMPORTANT : do not change the order of the follwing two lines. 
# standard magics
get_ipython().register_magics(BlueskyMagics)

# custom magics - it will override some standard magics
get_ipython().register_magics(BlueskyMagicsCustom)

# this is the set of agics that simplifies the syntax
simplify = Simplify(get_ipython())
simplify.autogenerate_magics('/home/simone/projects/raypyng/beamlinetools/beamlinetools/BEAMLINE_CONFIG/plans.py')
run_plan = simplify.execute_magic

# this are the peakinfo magics
get_ipython().register_magics(PeakInfoMagic)
# usage: peakinfo