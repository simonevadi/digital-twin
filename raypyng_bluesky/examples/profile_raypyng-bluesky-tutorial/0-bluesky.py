from bluesky import RunEngine

RE = RunEngine({})	

from bluesky.callbacks.best_effort import BestEffortCallback
bec = BestEffortCallback()

# Send all metadata/data captured to the BestEffortCallback.

# Make plots update live while scans run.
from bluesky.utils import install_kicker
install_kicker()

from databroker import Broker
db = Broker.named('temp')

# Insert all metadata/data captured into db.
RE.subscribe(db.insert)
RE.subscribe(bec)

from bluesky.magics import BlueskyMagics

get_ipython().register_magics(BlueskyMagics)


