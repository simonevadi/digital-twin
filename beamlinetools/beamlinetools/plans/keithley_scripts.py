from bluesky.plans import count

import time
from IPython import get_ipython
user_ns = get_ipython().user_ns

# the following functons are left here because they might 
# be useful. They must be edited depending on the beamline components names


def kth_range(kn=None,fs=None):
    '''Set range of keithley
    Parameters
    ----------
    kn  : int 
          number of the Keithley
    fs  : int
          range; 0 for autorange, 
          or a sequential number n between 2-11, 
          where n stands for 2.0e-n Amp
    '''
    if kn==None and fs==None:
        print('Usage:kth_range(kn,fs)')
        print('kn: keithley number (int)')
        print('fs: range(int), \n0 for autorange,')
        print('or a sequential number n between 2-11,') 
        print('where n stands for 2.0e-n Amp')
        print('provide at least the keithley number kn')
        return
    if kn<=9:
        kn='0'+str(kn)
    else:
        kn=str(kn)

    if kn!=None and fs==None:
        print(user_ns["kth"+kn].rnge.get())
    elif kn!=None and fs!=None:
        if fs==0 or fs>=2 and fs<=11:
            user_ns["kth"+str(kn)].rnge.put(fs)
            time.sleep(1)
            print('kth'+kn+' range set to ',user_ns["kth"+str(kn)].rnge.get())
        else:
            print('fs value not permitted, use either 0 for autorange, or values between 2-11 ')
        

def kth_voltage(kn=None,volt=None):
    '''Set voltage (volt) of keithley
    Parameters
    ---------- 
    kn   : int
           number of the Keithley
    volt : int
           voltage
    '''
    if kn==None and volt==None:
        print('Usage:kth_voltage(kn,fs)')
        print('kn: keithley number (int)')
        print('voltage: voltage (int)')
        print('provide at least the keithley number kn')
        return
    if kn<=9:
        kn='0'+str(kn)
    else:
        kn=str(kn)
    
    if kn!=None and volt==None:	
        print(user_ns["kth"+str(kn)].vsrc.get())
        
    elif kn!=None and volt!=None:	
        if volt<=300 and volt >=0:
            user_ns["kth"+str(kn)].vsrc_ena.put(1)
            user_ns["kth"+str(kn)].vsrc.put(volt)
            time.sleep(3)
            print('kth'+kn+' voltage set to ',user_ns["kth"+str(kn)].vsrc.get())
        else:
            print('Voltage not allowed, please enter a value between 0-100 V')



