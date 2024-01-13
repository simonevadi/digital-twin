from IPython.core.magic import Magics, magics_class, line_magic

from .base import BlueskyMagicsBase

@magics_class
class PeakInfoMagic(BlueskyMagicsBase):
    """
    Magic class for diplayin peak information
    """

    @property
    def metadata(self):
        """
        last run metadata
        """
        return self.shell.user_ns['db'][-1]['primary'].metadata

    @property
    def bec(self):
        """
        best effort callback instance
        """
        return self.shell.user_ns['bec']

    @line_magic
    def peakinfo(self, line):
        """
        show last scan peak information
        """

        if line is None or len(line)==0:
            # no paramters given : list all recorded detectors
            detectors  = self.metadata['start']['detectors']
            for detector in detectors:
                self.peakinfo(detector)
        else:
            # some parameters given, process them

            # first translate orginal detector names
            # to the hinted ones
            names = []
            hints = self.metadata['descriptors'][0]['hints']
            for detector_name in line.split():
                try:
                    if detector_name in hints:
                        fields = hints[detector_name]["fields"]
                        names.extend(fields)
                    else:
                        names.append(detector_name)
                except NameError:
                    print(f"Detector {detector_name} is unknown")

            # then transverse over peaks
            peaks = self.bec.peaks
            for detector_name in names:
                print(f"{detector_name}:")
                for peak_param_name in peaks.ATTRS:
                    try:
                        value = peaks[peak_param_name][detector_name]
                        print(f"\t{peak_param_name}={value}")
                    except:
                        value = "NOTFOUND"
                    #print(f"\t{peak_param_name}={value}")
        
    
    
#get_ipython().register_magics(PeakInfoMagic)
