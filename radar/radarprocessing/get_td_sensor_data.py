from radar.radarprocessing.TDData import TDData
from radar.RadarDevKit.RadarModule import RadarModule
from constants import SPEED_LIGHT, DIST_BETWEEN_ANTENNAS
from radar.configuration.RunType import RunType

import numpy as np
import pandas as pd

def get_td_data_raw(radar_module: RadarModule, ramp_type: str = "UP-Ramp") -> TDData:
    """
    Get the TD in the raw absolute value format
    """
    radar_module.GetTdData(measurement=ramp_type)
    time = pd.Timestamp.now().replace(microsecond=0)
    n_samples = 1024
    
    td_data = []
    n = 0
    for ch in range(4):      # maximum possible channels = 4
        if radar_module.sysParams.active_RX_ch & (1<<ch):
            ind1 = n*n_samples
            ind2 = ind1 + n_samples
            n += 1
            td_data.append(radar_module.TD_Data.data[ind1:ind2])
        else:
            td_data.append([0]*n_samples)
            
    # Application data with shape (4, 1024) -- I1 Time, Q1 Tim, I2 Time, Q2 Time
    td_data_amplitude =  np.array(td_data)
    
    # Transpose into shape (1024, 4)
    td_data_voltage = np.array(td_data_voltage).T

    return TDData(td_data_voltage, time)

def get_td_data_voltage(radar_module: RadarModule, ramp_type: str = "UP-Ramp") -> TDData:
    """
    Get the TD in units of Voltage.
    Return the TD data in voltage format.
    """
    radar_module.GetTdData(measurement=ramp_type)
    # If there's an error return, we'll try again
    if radar_module.error:
        return None
    
    time = pd.Timestamp.now()
    n_samples = 1024
    
    td_data = []
    n = 0
    for ch in range(4):      # maximum possible channels = 4
        if radar_module.sysParams.active_RX_ch & (1<<ch):
            ind1 = n*n_samples
            ind2 = ind1 + n_samples
            n += 1
            td_data.append(radar_module.TD_Data.data[ind1:ind2])
        else:
            td_data.append([0]*n_samples)
            
    # Application data with shape (4, 1024) -- I1 Time, Q1 Tim, I2 Time, Q2 Time
    td_data_amplitude =  np.array(td_data)
    # Covert from amplitude to the voltage values, per the manual's calculation
    td_data_voltage = (3 * td_data_amplitude) / ((2.**12) * 4 * radar_module.sysParams.t_ramp)
    
    # Transpose into shape (1024, 4), for easier handling of range bins and return
    return TDData(td_data_voltage.T, time)