from bluesky import RunEngine
from os.path import expanduser
from tiled.client import from_uri

RE = RunEngine({})

# Start the tiled client if env variables are defined
from os import environ
if environ.get('TILED_URL') is not None and environ.get('TILED_API_KEY') is not None:
    db = from_uri(environ.get('TILED_URL'), api_key=environ.get('TILED_API_KEY'))
    def post_document(name,doc):
        db.post_document(name,doc)

    RE.subscribe(post_document)



from bluesky.callbacks.best_effort import BestEffortCallback
bec = BestEffortCallback()

# Send all metadata/data captured to the BestEffortCallback.
RE.subscribe(bec)

# Database definition, change catalog_name for the actual
# name of the database
#import databroker
#db = databroker.catalog["catalog_name"]
#RE.subscribe(db.v1.insert)

# Temporary database, once mongo is installed and a database created use
 # comment the following lines 
#from databroker import Broker
#db = Broker.named('temp')
#RE.subscribe(db.insert)
# Let's try to make tiled work
#client.write_array([1, 2, 3], metadata={"color": "red", "barcode": 10})

from ophyd.sim import det, motor
from bluesky.plans import scan



# If you need debug messages from the RE then uncomment this
#from bluesky.utils import ts_msg_hook
#RE.msg_hook = ts_msg_hook







# Configure persistence between sessions of metadata
# change beamline_name to the name of the beamline
# from bluesky.utils import PersistentDict
# import os
# cwd = os.getcwd()
# RE.md = PersistentDict(expanduser('/opt/bluesky/data/persistence/beamline'))


# import matplotlib
import matplotlib

