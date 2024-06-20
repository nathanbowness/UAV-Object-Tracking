from RadarDevKit.RadarModule import RadarModule, GetRadarModule
from RadarDevKit.ConfigClasses import SysParams
from config import get_radar_params, get_ethernet_config, get_run_params
from config import RunParams

import numpy as np

# Get the FD data from the Radar
def get_FD_data(radarModule: RadarModule, radarParams: SysParams):
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
        # The IQ25 refers to a specific precision that is kept and used for the RADIAN phase/angle representation of the data
        # The explicit conversion below is given in the appendix
        angle_data_deg = angle_data_iq25 * (180 / (2**25 * np.pi))
        
    elif radarModule.sysParams.FFT_data_type == 1: # magnitudes/phase [I1, I1 Phase, Q1, Q1 Phase, I2, I2 Phase, ...]
        
        fc = 24350e6  # Central frequency in Hz
        b = 0.2       # Distance between antennas in meters
        c0 = 299792458  # Speed of light in m/s
        
        # Central frequency to go from phase to angles
        f_central = radarParams.manualBW / 2
        fd_data = radarModule.FD_Data.data
        mag_data = [fd_data[n] for n in range(0, len(fd_data), 2)]
        
        phase_data_iq25 = np.array([fd_data[n] for n in range(1, len(fd_data), 2)])
        
        # Convert IQ25 format phase data to normal radians (not in IQ25 representation values)
        max_iq25 = 2**25
        phase_data_radians = (phase_data_iq25 / (max_iq25))
        # Reshape the array to separate I and Q pairs
        phase_pairs  = phase_data_radians.reshape(-1, 2) # Reshape into Nx2 where each row is [I, Q]
        
        # # Calculate phase differences assuming Rx1, Rx2 alternation
        # phase_differences = phase_pairs[:, 1] - phase_pairs[:, 0]
        
        # alpha = np.arcsin((phase_differences * c0) / (2 * np.pi * fc * b))
        # alpha_degrees = np.degrees(alpha)
        
        
        # Calculate phases for each pair using arctan2, iterating over pairs
        phases = np.arctan2(phase_pairs[:, 1], phase_pairs[:, 0])

        # Assuming phases are alternately from Rx1 and Rx2:
        # phases[0], phases[2], phases[4], ... are from Rx1
        # phases[1], phases[3], phases[5], ... are from Rx2
        phase_rx1 = phases[0::2]  # Phases from Rx1
        phase_rx2 = phases[1::2]  # Phases from Rx2

        # Calculate phase differences
        phase_differences = phase_rx2 - phase_rx1

        # Calculate the angle of arrival alpha
        alpha = np.arcsin((phase_differences * c0) / (2 * np.pi * fc * b))
        alpha_degrees = np.degrees(alpha)  # Convert from radians to degrees
        
        # Compute the angle in radians for each I, Q pair
        # angles_radians = np.arctan2(phase_data_iq25_reshape[:, 1], phase_data_iq25_reshape[:, 0])
        # angles_second = np.degrees(angles_radians)
        # phase_data_deg = angles_radians * (180 / (2**25 * np.pi))
        print("test")
    
    # Convert to dBm
    min_dbm = -60  # [dBm]
    for n in range(len(mag_data)):
        try:
            # Conversion of the amplitude to relative frequency per milivolt is given in Appendix and used below
            mag_data[n] = 20 * np.log10(mag_data[n] / 2.**21)
        except:
            mag_data[n] = min_dbm
    
    # Sort for active channels
    fd_data = []
    n = 0
    for ch in range(4):  # maximum possible channels = 4
        if radarModule.sysParams.active_RX_ch & (1 << ch):
            ind1 = n * radarModule.FD_Data.nSamples
            ind2 = ind1 + radarModule.FD_Data.nSamples
            n += 1
            fd_data.append(mag_data[ind1:ind2])
        else:
            fd_data.append([0] * radarModule.FD_Data.nSamples)
            
    return fd_data

def collect_data(run_params: RunParams):
    # Collect data
    radar_params = get_radar_params()
    radarModule = GetRadarModule(updatedRadarParams=radar_params,
                                updatedEthernetConfig=get_ethernet_config())
    
    radarModule.GetFdData(run_params.ramp_type)
    return get_FD_data(radarModule, radarParams=radar_params)

if __name__ == "__main__":  
    collect_data(get_run_params())
