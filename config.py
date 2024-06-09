from RadarDevKit.ConfigClasses import SysParams
from RadarDevKit.Interfaces.Ethernet.EthernetConfig import EthernetParams

# Updated configuration for the system parameters of the Radar
def get_sys_params():
    updatedSysParams = SysParams()
    updatedSysParams.minFreq = 24000
    updatedSysParams.manualBW = 250
    updatedSysParams.t_ramp = 7
    updatedSysParams.active_RX_ch = 15
    updatedSysParams.freq_points = 512
    updatedSysParams.FFT_data_type = 0
    
    return updatedSysParams

# Updated ethernet configuration to connect to the Radar    
def get_ethernet_config():
    ethernetConfig = EthernetParams()
    ethernetConfig.port = 1024
    ethernetConfig.ip = "10.0.0.59"
    return ethernetConfig