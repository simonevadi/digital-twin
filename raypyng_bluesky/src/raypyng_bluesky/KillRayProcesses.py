import psutil

def KillRayProcesses():
    """Kill all the RAY-UI processes in a 'stopped' status
    """    
    pid_list = psutil.pids()
    for pid in pid_list:
            try:
                p = psutil.Process(pid)
                if p.name() == 'rayui' and p.status() == 'stopped':
                    try:
                        p.kill()
                        print('I found the following instance of RAY-UI in a stopped status, and killed it: pid:', pid)
                    except:
                        pass
                        print('I tried to kill the following RAY-UI process, but I failed: pid:', pid)
            except:
                pass
            
