# Long timeout for all signals
from ophyd.signal import EpicsSignalBase
from bluesky import RunEngine
from bluesky.plans import scan
from tiled.client import from_uri


# from beamlinetools.devices.accelerator import DetailedAccelerator, TopUpMonitoring
# from bessyii_devices.keithley import Keithley6514, Keithley6517

# simulated devices
from ophyd.sim import noisy_det, det1, det2, det3, det4, motor, motor1, motor2, motor, noisy_det   # two simulated detectors

# Ring
# print("Loading Accelerator")
# accelerator = DetailedAccelerator("", name="accelerator")
# next_injection = TopUpMonitoring("", name="next_injection")
# accelerator.wait_for_connection()
# next_injection.wait_for_connection()



# Keithleys
# endstation = "OPTICSES01X:"
# print("Loading keithleys")
# kth1 = Keithley6517(endstation+"Keithley1:",name='kth1')


# kth1.wait_for_connection()



# Pgm



# Apertures


# Mirrors



