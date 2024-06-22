from RadarDevKit.Interfaces.Ethernet.EthernetConfig import EthernetParams
from RadarDevKit.RadarModule import RadarModule, GetRadarModule
from RadarDevKit.ConfigClasses import SysParams
from config import get_radar_params, get_ethernet_config, get_run_params
from config import RunParams

from constants import SPEED_LIGHT, DIST_BETWEEN_ANTENNAS

import numpy as np

# Get the FD data from the Radar
def get_FD_data(radarModule: RadarModule, radarParams: SysParams):
    
    fc = (radarParams.minFreq*(10**6)) + (radarParams.manualBW / 2)*(10**6) # Central frequency in Hz - Conversion from Mhz to Hz
    
    # Process the FD data based on the data type
    if radarModule.sysParams.FFT_data_type == 0:  # only magnitudes were transmitted
        fd_data = radarModule.FD_Data.data
        mag_data = radarModule.FD_Data.data
    elif radarModule.sysParams.FFT_data_type == 2:  # real/imaginary 
        comp_data = [complex(float(radarModule.FD_Data.data[n]), float(radarModule.FD_Data.data[n + 1])) for n in range(0, len(radarModule.FD_Data.data), 2)]
        mag_data = np.abs(comp_data)
    elif radarModule.sysParams.FFT_data_type == 3:  # magnitudes/object angle
        fd_data = radarModule.FD_Data.data      
        mag_data = [fd_data[n] for n in range(0, len(fd_data), 2)]
        angle_data_iq25 = np.array([fd_data[n] for n in range(1, len(fd_data), 2)])
        
        # The IQ25 refers to a specific precision that is kept and used for the RADIAN angle representation of the data
        # The explicit conversion below is given in the appendix
        angle_data_deg = angle_data_iq25 * (180 / (2**25 * np.pi))
        
    elif radarModule.sysParams.FFT_data_type == 1: # magnitudes/phase [I1, I1 Phase, Q1, Q1 Phase, I2, I2 Phase, ...]
        # Central frequency to go from phase to angles
        fd_data = radarModule.FD_Data.data
        mag_data = [fd_data[n] for n in range(0, len(fd_data), 2)]
        
        phase_data_iq25 = np.array([fd_data[n] for n in range(1, len(fd_data), 2)])
        
        max_iq25 = 2**25
        phase_data_radians = phase_data_iq25
        phase_data_radians = (phase_data_iq25 / (max_iq25))
        # phase_data_radians = ((phase_data_iq25 * 180) / ((max_iq25)*np.pi))
        
        iq_data = np.array(phase_data_radians).reshape(-1, 4)  # Reshape into Nx4 where each row is [I1, Q1, I2, Q2]

        I1_phase = iq_data[:, 0]
        Q1_phase = iq_data[:, 1]
        I2_phase = iq_data[:, 2]
        Q2_phase = iq_data[:, 3]
        
        # If phase data needs to be calculated from I and Q (uncomment if needed)
        phase1 = np.arctan(Q1_phase / I1_phase)
        phase2 = np.arctan(Q2_phase / I2_phase)
        # phase1 = np.arctan2(Q1, I1) ? This is old - remove it eventually
        phase_differences = phase2 - phase1  

        # Calculate the view angle
        alpha = np.arcsin((phase_differences * SPEED_LIGHT) / (2 * np.pi * fc * DIST_BETWEEN_ANTENNAS))
        alpha_degrees = np.degrees(alpha)  # Convert from radians to degrees
        
        # An array of measured data - [Rx1 Phase, Rx2 Phase, Estimated View Angle] (512x3)
        phase_data = np.hstack((phase1, phase2, alpha_degrees))
    
    # Convert to dBm
    min_dbm = -60  # [dBm]
    for n in range(len(mag_data)):
        try:
            # Conversion of the amplitude to relative frequency per milivolt is given in Appendix and used below
            mag_data[n] = 20 * np.log10(mag_data[n] / 2.**21)
        except:
            mag_data[n] = min_dbm
    
    # Create the matrix of measured data - [512, 7] => [I1, Q1, I2, Q2, Rx1 Phase, Rx2 Phase, Estimated View Angle]
    return np.hstack((mag_data, phase_data))

def get_fd_data_from_radar(run_params: RunParams, radar_sys_params: SysParams, ether_params: EthernetParams):
    # Collect data
    radarModule = GetRadarModule(updatedRadarParams=radar_sys_params,
                                updatedEthernetConfig=ether_params)
    radarModule.GetFdData(run_params.ramp_type)
    return get_FD_data(radarModule, radarParams=radar_sys_params)

if __name__ == "__main__":  
    test = get_fd_data_from_radar(get_run_params(), get_radar_params, get_ethernet_config())
    print("test")
