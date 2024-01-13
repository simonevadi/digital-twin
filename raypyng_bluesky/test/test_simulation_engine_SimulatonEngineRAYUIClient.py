from raypyng_bluesky.twisted_client import ClientProtocolRAY
from raypyng_bluesky.simulation_engine import SimulatonEngineRAYUIClient
from raypyng.rml import RMLFile


exports_list = ["KB2", "DetectorAtFocus", "KB1", "Dipole"]
sim = SimulatonEngineRAYUIClient('127.0.0.1', 12345,'rp_', verbose=True)
sim.setup_simulation()
rml = RMLFile('/home/simone/Documents/RAYPYNG/raypyng_master/raypyng_bluesky/test/tmp/beamline.rml')
sim.simulate('client_tmp', rml, exports_list)