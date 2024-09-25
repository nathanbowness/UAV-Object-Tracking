from radar_tracking.RadarDevKit.ConfigClasses import SysParams
from radar_tracking.RadarDevKit.Interfaces.Ethernet.EthernetConfig import EthernetParams
from radar_tracking.RadarDevKit.RadarModule import GetRadarModule
from radar_tracking.configuration.RadarRunParams import RadarRunParams # type: ignore
from radar_tracking.configuration.PlotConfig import PlotConfig
from radar_tracking.configuration.CFARParams import CFARParams
        
# Updated configuration for the system parameters of the Radar
def get_radar_params():
    updatedSysParams = SysParams()
    updatedSysParams.minFreq = 24000
    updatedSysParams.manualBW = 750
    updatedSysParams.t_ramp = 1
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
    return CFARParams(num_guard=2, num_train=10, threshold=10.0, threshold_is_percentage=False)

def get_run_params():
    return RadarRunParams(get_cfar_params())

def get_plot_config():
    plotConfig = PlotConfig()
    return plotConfig
