from RadarDevKit.ConfigClasses import SysParams
from RadarDevKit.Interfaces.Ethernet.EthernetConfig import EthernetParams

class CFARParams():    
    def __init__(self, guard_cell: int = 5, subgroup: int = 10, threshold: float = 10):
        # CasoCFAR Params
        self.guard_cells = guard_cell
        self.subgroup = subgroup
        self.threshold = threshold
        
class RunParams():
    def __init__(self, cfar_params: CFARParams):
        # Settings to let the program run from recorded data
        self.runFromRecordedData = False
        self.recordedDataName = ""
        self.recordFormat = "custom"
        
        self.ramp_type = "UP-Ramp"
        
        self.cfar_params = cfar_params
        # The minimum amount of data that must be kept in memory to window on
        self.data_window = (2*cfar_params.guard_cells) + (2*cfar_params.subgroup) + 1

# Updated configuration for the system parameters of the Radar
def get_radar_params():
    updatedSysParams = SysParams()
    updatedSysParams.minFreq = 24000
    updatedSysParams.manualBW = 600
    updatedSysParams.t_ramp = 7
    updatedSysParams.active_RX_ch = 15
    updatedSysParams.freq_points = 512
    updatedSysParams.FFT_data_type = 3
    
    return updatedSysParams

# Updated ethernet configuration to connect to the Radar    
def get_ethernet_config():
    ethernetConfig = EthernetParams()
    ethernetConfig.port = 1024
    ethernetConfig.ip = "10.0.0.59"
    return ethernetConfig

def get_cfar_params():
    return CFARParams()

def get_run_params():
    return RunParams(get_cfar_params())
