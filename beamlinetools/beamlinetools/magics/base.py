import asyncio
from bluesky.utils import ProgressBarManager
from bluesky import RunEngine
from IPython.core.magic import Magics
from IPython import get_ipython

from bluesky import RunEngineInterrupted
from bluesky import plan_stubs as bps
from bluesky import plans as bp


from ..utils.resolve import Devices

def padprint(prefix:str,payload:str,pad_char='.',pad_length=20):
    print(f"{prefix.ljust(pad_length,pad_char)}: {payload}")


class BlueskyMagicsBase(Magics):
    RE = RunEngine({}, loop=asyncio.new_event_loop())
    #shell = get_ipython()
    pbar_manager = ProgressBarManager()

    def __init__(self, shell=None, **kwargs):
        if shell is None: shell = get_ipython()
        super().__init__(shell, **kwargs)
        self.devices = Devices(user_ns=self.shell.user_ns)

    def _ensure_idle(self):
        if self.RE.state != 'idle':
            #print('The RunEngine invoked by magics cannot be resumed.')
            #print('Aborting...')
            self.RE.abort()

    def plan_mov(self,*args,**kwargs):
        plan = bps.mv(*args,**kwargs)
        self.RE.waiting_hook = self.pbar_manager
        try:
            self.RE(plan)
        except RunEngineInterrupted:
            ...
        self.RE.waiting_hook = None
        self._ensure_idle()

    def plan_count(self,*args,callback=None,**kwargs):
        plan = bp.count(*args,**kwargs)
        self.RE.waiting_hook = self.pbar_manager
        try:
            self.RE(plan,callback)
        except RunEngineInterrupted:
            ...
        self.RE.waiting_hook = None
        self._ensure_idle()


def register_magics(*args):
    get_ipython().register_magics(args)