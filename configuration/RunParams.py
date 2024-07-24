from .CFARParams import CFARParams
from .CFARType import CfarType
from .RunType import RunDataFormat, RunType

class RunParams():
    """
    Parameters to run the radar system
    """
    def __init__(self, cfar_params: CFARParams):
        # Settings to let the program run from recorded data should be recorded, or read from a preexisting location
        self.recordedDataFolder= "test_data"
        self.runType = RunType.LIVE
        self.recordedDataFormat = RunDataFormat.FD_CUSTOM
        
        if (self.runType == RunType.LIVE_RECORD):
          print("Data will be recorded.")
        
        if(self.recordedDataFormat == RunDataFormat.SENTOOL_FD and not self.runType == RunType.RERUN):
            exit("You cannot use the SENTOOL_FD format for a live data run, since this program cannot record data in that format.")
        
        self.ramp_type = "UP-Ramp"
        self.cfar_params = cfar_params
        # The minimum amount of data that must be kept in memory to window on
        if(self.cfar_params.cfar_type == CfarType.LEADING_EDGE):
            self.data_window_size = cfar_params.num_guard + cfar_params.num_train + 1 + 1 # 1 more to have 1 extra
        else:
            self.data_window_size = (2*cfar_params.num_guard) + (2*cfar_params.num_train) + 1 + 1 # 1 more to have 1 extra