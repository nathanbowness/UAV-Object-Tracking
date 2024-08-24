from RadarDevKit.ConfigClasses import SysParams
from RadarDevKit.Interfaces.Ethernet.EthernetConfig import EthernetParams
from RadarDevKit.RadarModule import GetRadarModule
from configuration.RunParams import RunParams # type: ignore
from configuration.PlotConfig import PlotConfig
from configuration.CFARParams import CFARParams
        
# Updated configuration for the system parameters of the Radar
def get_radar_params():
    updatedSysParams = SysParams()
    updatedSysParams.minFreq = 24000
    updatedSysParams.manualBW = 700
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
    return CFARParams(num_guard=2, num_train=50, threshold=10.0, threshold_is_percentage=False)

def get_run_params():
    return RunParams(get_cfar_params())

def get_plot_config():
    plotConfig = PlotConfig()
    return plotConfig
