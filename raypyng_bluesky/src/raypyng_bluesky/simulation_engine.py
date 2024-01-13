import os
import asyncio
import time

from raypyng.runner import RayUIRunner, RayUIAPI
from raypyng.postprocessing import PostProcess
from raypyng_bluesky.asyncio_client import run_asyncio_client


class SimulatonEngineRAYUI():
    """A class that takes care of the communication with the RAY-UI api

    This class is used in case the simulation engine requested is RAY-UI on the local machine

        Args:
            ray_ui_location (str): the location of RAY-UI program. If None the program will look
                                    into the defaults folders.
        """       
    def __init__(self, ray_ui_location:str) -> None:
              
        self.ray_ui_location = ray_ui_location

    def check_if_simulation_is_done(self):
        """Retrieve the simulation done signal of the RayUIAPI.

        Returns:
            (bool): The simulation done signal.
        """        
        return self.a._simulation_done
    
    def setup_simulation(self):
        """Get ready to simulate, by calling the RayUIRunner and the RayUIAPI

        Returns:
            (RayUIAPI): an instance of the RayUIAPI class
        """        
        self.r = RayUIRunner(ray_path=self.ray_ui_location, hide=True)
        self.a = RayUIAPI(self.r)
        return self.a

    def simulate(self, path, rml, exports_list):
        """Start the simulations with RAY-UI using the RayUIAPI

        Args:
            path (str): the path to the temporary folder
            rml (RMLFile): the instance of the RMLFile class used to save the rml file
            exports_list (list): list of the exported objects
        """        

        # make sure tmp folder exists, if not create it
        if not os.path.exists(path):
            os.makedirs(path)
        rml.write(os.path.join(path,'tmp.rml'))
        self.r.run()
        self.a.load(os.path.join(path,'tmp.rml'))
        self.a.trace(analyze=False)
        self.a.save(os.path.join(path,'tmp.rml'))
        for exp in exports_list:
            self.a.export(exp, "RawRaysOutgoing", path, '')
            pp = PostProcess()
            pp.postprocess_RawRays(exported_element=exp, 
                                exported_object='RawRaysOutgoing', 
                                dir_path=path, 
                                sim_number='', 
                                rml_filename=os.path.join(path,'tmp.rml'))
        
        self.a.quit()
        return 




class SimulatonEngineRAYUIClient():  
    def __init__(self, ip, port, prefix, verbose=False) -> None:
        self.ip = ip
        self.port = port
        self.verbose=verbose
        self._simulation_done = False
        self.prefix = prefix

    def check_if_simulation_is_done(self):      
        return self._simulation_done
    
    def setup_simulation(self):      
        self._simulation_done = False
        return 

    def simulate(self, path, rml, exports_list):      
        if not os.path.exists(path):
            os.makedirs(path)
        rml.write(os.path.join(path,'tmp.rml'))

        done_sim = asyncio.run(run_asyncio_client(self.ip, self.port, self.prefix, exports_list, path))
        
        while done_sim is not True:
            time.sleep(.1)
            pass
        if done_sim:
            self._simulation_done = True

        return 
