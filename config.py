from RadarDevKit.ConfigClasses import SysParams
from RadarDevKit.Interfaces.Ethernet.EthernetConfig import EthernetParams
from resources.FDDataMatrix import FDSignalType
from resources.RunType import RunType, RunDataFormat
from RadarDevKit.RadarModule import RadarModule, GetRadarModule

from enum import Enum

class CFARParams():    
    def __init__(self, num_guard: int = 3, num_train: int = 10, threshold: float = 10.0):
        # CasoCFAR Params
        self.cfar_type = CfarType.LEADING_EDGE
        self.num_guard = num_guard
        self.num_train = num_train
        self.threshold = 0.4
        self.threshold_is_percentage = True

class CfarType(Enum):
    CASO = 0,
    LEADING_EDGE = 1
        
class RunParams():
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
        self.data_window_size = (2*cfar_params.num_guard) + (2*cfar_params.num_train) + 1
        
class PlotConfig():
    def __init__(self):
        self.plot_raw_fd_signal = False
        self.raw_fd_signal_to_plot = FDSignalType.I1
        self.plot_raw_fd_with_threshold_signal = False
        self.plot_raw_fd_heatmap = True
        self.plot_fd_detections = True

# Updated configuration for the system parameters of the Radar
def get_radar_params():
    updatedSysParams = SysParams()
    updatedSysParams.minFreq = 24000
    updatedSysParams.manualBW = 600
    updatedSysParams.t_ramp = 7
    updatedSysParams.active_RX_ch = 15
    updatedSysParams.freq_points = 512
    updatedSysParams.FFT_data_type = 1
    
    return updatedSysParams

# Updated ethernet configuration to connect to the Radar    
def get_ethernet_config():
    ethernetConfig = EthernetParams()
    ethernetConfig.port = 1024
    ethernetConfig.ip = "10.0.0.59"
    return ethernetConfig

def get_radar_module():
    return GetRadarModule(updatedRadarParams=get_radar_params(),
                                updatedEthernetConfig=get_ethernet_config())

def get_cfar_params():
    return CFARParams()

def get_run_params():
    return RunParams(get_cfar_params())

def get_plot_config():
    return PlotConfig()
