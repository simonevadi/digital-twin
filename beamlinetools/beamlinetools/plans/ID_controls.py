import time

from bluesky.plan_stubs import mv, abs_set
from bluesky.plans import count,scan, list_grid_scan, grid_scan

from IPython import get_ipython
user_ns = get_ipython().user_ns


# the following functons are left here because they might 
# be useful. They must be edited depending on the beamline components names


###########################################################################
# IDon and IDoff

def IDon():
    user_ns["pgm"].ID_on.set(1) # 1 should set IDon
    user_ns["u49_2"].id_control.set(1) # 1 should set to remote
    #if set_table != False:
    #    user_ns["ue48_pgm"].table.put(set_table)
    #user_ns["ue48_pgm"].harmonic.put(4)

def IDoff():
    user_ns["pgm"].ID_on.set(0) # 1 should set IDoff
    user_ns["u49_2"].id_control.set(0) # 1 should set to local
    
    
###########################################################################
# Set Harmonic

def SetHarmonic(Harmonic):
    """
    Change the harmonic for the UE48 undulator
    
    Parameters
    ----------
    harmonic : int or str
        1 for the first harmonic
        3 for the second harmonic
        5 for the fifth harmonic
        7 for the seventh harmonic
        'maxflux' for maxflux
        
    """


        
    d={1:0,3:1,5:2,7:3,'maxflux':4}    
    if table not in d:
        print("Value not permitted.")
        print("Permitted values are", d.keys())
    else:
        user_ns["pgm"].harmonic.put(d[harmonic])
    
###########################################################################
# Set Table and Harmonic

def SetTable(table):
    """
    Change the table for the UE48 undulator
    
    Parameters
    ----------
    table : int or str 
        "EllipPos" 
        "EllipNeg"
        "LinHor"
        "LinVer"
        an integer between [0,11] for the other tables,
        see BluePanels for the options
    """

    d={"EllipPos":0,"EllipNeg":1,"LinHor":2,"LinVer":3}
    if table in d:
        user_ns["pgm"].table.put(d[table])
    elif isinstance(table,int)==True:
        if table >=0 or table <= 11:
            user_ns["pgm"].table.put(d[table])
        else:
            print("Permitted Values are:")
            print("str: ", d.keys())
            print("int: values between [0,11]")





    

