import unittest

import numpy as np
import os
import shutil
import pathlib as pl

import sys
sys.path.insert(1, '../src')

from raypyng.simulate import Simulate


class TestNoAnalyze(unittest.TestCase):
    
    def test0_produced_files(self):
        """The name is test0 beecause it has to run before the others
        """
        dirpath = "RAYPy_Simulation_test_NoAnalyze"
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            shutil.rmtree(dirpath)
            

        this_file_dir=os.path.dirname(os.path.realpath(__file__))
        rml_file = os.path.join(this_file_dir,'rml/elisa.rml')

        sim = Simulate(rml_file, hide=True)

        rml=sim.rml
        elisa = sim.rml.beamline



        # define the values of the parameters to scan 
        energy    = np.arange(200, 7201,1000)
        SlitSize  = np.array([0.1])
        cff       = np.array([2.25])
        nrays     = 10000

        # define a list of dictionaries with the parameters to scan
        params = [  
                    # set two parameters: "alpha" and "beta" in a dependent way. 
                    {elisa.Dipole.photonEnergy:energy}, 
                    # set a range of  values 
                    {elisa.ExitSlit.totalHeight:SlitSize},
                    # set values 
                    {elisa.PG.cFactor:cff},
                    {elisa.Dipole.numberRays:nrays}
                ]

        #and then plug them into the Simulation class
        sim.params=params

        # sim.simulation_folder = '/home/simone/Documents/RAYPYNG/raypyng/test'
        sim.simulation_name = 'test_NoAnalyze'

        # repeat the simulations as many time as needed
        sim.repeat = 2

        sim.analyze = False # don't let RAY-UI analyze the results
        sim.raypyng_analysis=True # let raypyng analyze the results

        ## This must be a list of dictionaries
        sim.exports  =  [{elisa.Dipole:'RawRaysOutgoing'},
                        {elisa.DetectorAtFocus:['RawRaysOutgoing']}
                        ]

        #uncomment to run the simulations
        result = sim.run(multiprocessing=5, force=True)
        self.assertTrue(result)

    def test_input_Dipole_file(self):
        dirpath = "RAYPy_Simulation_test_NoAnalyze"
        file = 'input_param_Dipole_numberRays.dat'
        path = os.path.join(dirpath,file)
        path = pl.Path(path)
        self.assertTrue(path.is_file())

        file = 'input_param_Dipole_photonEnergy.dat'
        path = os.path.join(dirpath,file)
        path = pl.Path(path)
        self.assertTrue(path.is_file())
    
    def test_input_ExitSlit_file(self):
        dirpath = "RAYPy_Simulation_test_NoAnalyze"
        file = 'input_param_ExitSlit_totalHeight.dat'
        path = os.path.join(dirpath,file)
        path = pl.Path(path)
        self.assertTrue(path.is_file())

    def test_input_PG_file(self):
        dirpath = "RAYPy_Simulation_test_NoAnalyze"
        file = 'input_param_PG_cFactor.dat'
        path = os.path.join(dirpath,file)
        path = pl.Path(path)
        self.assertTrue(path.is_file())
    
    def test_round_folder(self):
        dirpath = "RAYPy_Simulation_test_NoAnalyze"
        for i in range(2):
            path = os.path.join(dirpath,'round_'+str(i))
            path = pl.Path(path)
            self.assertTrue(path.is_dir())
    
    def test_round_folders_csv(self):
        dirpath = "RAYPy_Simulation_test_NoAnalyze"
        for i in range(2):
            path = os.path.join(dirpath,'round_'+str(i))
            f = find_files_in_folder(path)
            self.assertEqual(17,len(f))
    
    def test_round_folders_rml(self):
        dirpath = "RAYPy_Simulation_test_NoAnalyze"
        for i in range(2):
            path = os.path.join(dirpath,'round_'+str(i))
            f = find_files_in_folder(path, suffix='.rml')
            self.assertEqual(8,len(f))
    
    def test_round_folders_rml(self):
        dirpath = "RAYPy_Simulation_test_NoAnalyze"
        for i in range(2):
            path = os.path.join(dirpath,'round_'+str(i))
            f = find_files_in_folder(path, suffix='.dat')
            self.assertEqual(16,len(f))

    def test_input_Dipole_file(self):
        dirpath = "RAYPy_Simulation_test_NoAnalyze"
        file = 'Dipole.dat'
        path = os.path.join(dirpath,file)
        path = pl.Path(path)
        self.assertTrue(path.is_file())
 
    def test_input_DetectorAtFocus_file(self):
        dirpath = "RAYPy_Simulation_test_NoAnalyze"
        file = 'DetectorAtFocus.dat'
        path = os.path.join(dirpath,file)
        path = pl.Path(path)
        self.assertTrue(path.is_file())



def find_files_in_folder(path_to_dir, suffix=".csv" ):
     filenames = os.listdir(path_to_dir)
     return [ filename for filename in filenames if filename.endswith( suffix ) ]


if __name__ == '__main__':
    unittest.main(verbosity=0)




        