from radarprocessing.FDDataMatrix import FDDataMatrix
from RadarDevKit.Interfaces.Ethernet.EthernetConfig import EthernetParams
from RadarDevKit.RadarModule import RadarModule, GetRadarModule
from RadarDevKit.ConfigClasses import SysParams
from config import get_radar_module, get_radar_params, get_ethernet_config, get_run_params
from config import RunParams
from constants import SPEED_LIGHT, DIST_BETWEEN_ANTENNAS
from configuration.RunType import RunType

import numpy as np

def get_td_data_voltage(run_params: RunParams, 
                 radar_module: RadarModule):
    """
    Get the TD in units of Voltage.
    (4, 1024) -- I1, Q1, I2, Q2
    """
    radar_module.GetTdData(measurement=run_params.ramp_type)
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
    
    print(td_data_voltage.shape)
    return td_data_voltage

def get_td_data_voltage_T(run_params: RunParams, 
                 radar_module: RadarModule):
    """
    Get the TD in units of Voltage.
    (1024, 4) -- I1, Q1, I2, Q2
    """
    return get_td_data_voltage(run_params, radar_module).T
    
def calculate_phase_data_and_view_angle(fc, raw_phase_data_iq25):
    
    max_iq25 = 2**25
    phase_data_radians = (raw_phase_data_iq25 / (max_iq25))
    
    iq_data = np.array(phase_data_radians).reshape(-1, 512).T  # Reshape into Nx4 where each row is [I1, Q1, I2, Q2]

    I1_phase = iq_data[:, 0]
    Q1_phase = iq_data[:, 1]
    I2_phase = iq_data[:, 2]
    Q2_phase = iq_data[:, 3]
        
    # complex_signal_1 = I1_phase + 1j * Q1_phase
    # complex_signal_2 = I2_phase + 1j * Q2_phase
    
    # phase1 = np.angle(complex_signal_1)
    # phase2 = np.angle(complex_signal_2)
    # # Apply phase unwrapping
    # phase_1_unwrapped = np.unwrap(phase1)
    # phase_2_unwrapped = np.unwrap(phase2)
    
    # phase_differences_unwrapped = phase_1_unwrapped - phase_2_unwrapped
        
    # If phase data needs to be calculated from I and Q (uncomment if needed)
    phase1 = np.arctan(Q1_phase / I1_phase)
    phase2 = np.arctan(Q2_phase / I2_phase)
    # phase1 = np.arctan2(Q1_phase, I1_phase) # ? This is old - remove it eventuall
    # phase2 = np.arctan2(Q2_phase, I2_phase) # ? This is old - remove it eventuall
    # phase1 = np.arctan2(Q1, I1) ? This is old - remove it eventually
    
    # phase_differences = np.unwrap([phase1, phase2], axis=0)[1] - np.unwrap([phase1, phase2], axis=0)[0]
    phase_differences = I2_phase - I1_phase
    phase_differences_unwrapped = np.unwrap([phase_differences])[0]

    # Calculate the view angle
    sin_alpha = (phase_differences_unwrapped * SPEED_LIGHT) / (2 * np.pi * fc * DIST_BETWEEN_ANTENNAS)
    
    # Ensure sin_alpha is within the valid range for arcsin
    sin_alpha = np.clip(sin_alpha, -1, 1)
        
    alpha = np.arcsin(sin_alpha)
    alpha_degrees = np.degrees(alpha)  # Convert from radians to degrees
    
    # An array of measured data - [Rx1 Phase [Rad], Rx2 Phase [Rad], Phase_Diff, Estimated View Angle [Deg]] (512 x 4)
    return np.vstack((phase1, phase2, phase_differences_unwrapped, alpha_degrees)).T

def get_FD_data_angle(radarModule: RadarModule, radarParams: SysParams):
    fc = (radarParams.minFreq*(10**6)) + (radarParams.manualBW / 2)*(10**6) # Central frequency in Hz - Conversion from Mhz to Hz
    
    if radarModule.sysParams.FFT_data_type == 3:  # magnitudes/object angle
        fd_data = radarModule.FD_Data.data      
        mag_data = [fd_data[n] for n in range(0, len(fd_data), 2)]
        angle_data_iq25 = np.array([fd_data[n] for n in range(1, len(fd_data), 2)])
        angle_data_iq25 = np.array(angle_data_iq25)
    else:
        return None
    
    angle_data_deg = angle_data_iq25 * (180 / (2**25 * np.pi))
    
    # Convert to dBm
    min_dbm = -60  # [dBm]
    for n in range(len(mag_data)):
        try:
            # Conversion of the amplitude to relative frequency per milivolt is given in Appendix and used below
            mag_data[n] = 20 * np.log10(mag_data[n] / 2.**21)
        except:
            mag_data[n] = min_dbm
            
    fd_data = []
    angle_data = []
    n = 0
    for ch in range(4):  # maximum possible channels = 4
        if radarModule.sysParams.active_RX_ch & (1 << ch):
            ind1 = n * radarModule.FD_Data.nSamples
            ind2 = ind1 + radarModule.FD_Data.nSamples
            n += 1
            fd_data.append(mag_data[ind1:ind2])
            angle_data.append(angle_data_deg[ind1:ind2])
        else:
            fd_data.append([0] * radarModule.FD_Data.nSamples)
    
    fd_data = np.array(fd_data)
    
    # print(fd_data.shape)
    angle_data = np.array(angle_data)
    # print(angle_data.shape)
    # print("----")
    return np.vstack((fd_data, angle_data))

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
        
    elif radarModule.sysParams.FFT_data_type == 1: # magnitudes/phase [I1, I1 Phase, Q1, Q1 Phase, I2, I2 Phase, ...]
        # Central frequency to go from phase to angles
        fd_data = radarModule.FD_Data.data
        mag_data = [fd_data[n] for n in range(0, len(fd_data), 2)]
        raw_phase_data_iq25 = np.array([fd_data[n] for n in range(1, len(fd_data), 2)])
    
    # Convert to dBm
    min_dbm = -60  # [dBm]
    for n in range(len(mag_data)):
        try:
            # Conversion of the amplitude to relative frequency per milivolt is given in Appendix and used below
            mag_data[n] = 20 * np.log10(mag_data[n] / 2.**21)
        except:
            mag_data[n] = min_dbm
            
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
    
    mag_data = np.array(mag_data)
    fd_data = np.array(fd_data)
    
    return fd_data

# Get the FD data from the Radar
def get_FD_data_phase_data(radarModule: RadarModule, radarParams: SysParams) -> FDDataMatrix:

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
        raw_phase_data_iq25 = np.array([fd_data[n] for n in range(1, len(fd_data), 2)])
        
        # An array of measured data - [Rx1 Phase [Rad], Rx2 Phase [Rad], Phase_Diff, Estimated View Angle [Deg]] (512x4)
        phase_data = calculate_phase_data_and_view_angle(fc, raw_phase_data_iq25)
    
    # Convert to dBm
    min_dbm = -60  # [dBm]
    for n in range(len(mag_data)):
        try:
            # Conversion of the amplitude to relative frequency per milivolt is given in Appendix and used below
            mag_data[n] = 20 * np.log10(mag_data[n] / 2.**21)
        except:
            mag_data[n] = min_dbm
            
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
    
    mag_data = np.array(mag_data)
    fd_data = np.array(fd_data).T
    
    # Create the FDDataMatrix of measured data with a timestamp - [512, 7] => [I1, Q1, I2, Q2, Rx1 Phase, Rx2 Phase, Estimated View Angle]
    return FDDataMatrix(np.hstack((fd_data, phase_data)))

def get_fd_data_with_angles_from_radar(run_params: RunParams, 
                           radar_module: RadarModule,
                           radar_sys_params: SysParams = get_radar_params()):
    # Collect data
    radar_module.GetFdData(run_params.ramp_type)
    fd_data = get_FD_data_angle(radarModule=radar_module, radarParams=radar_sys_params)
    
    # Print the FD data
    # if run_params.runType == RunType.LIVE_RECORD:
    #     fd_data.print_data_to_file(run_params.recordedDataFolder)
    
    return fd_data

def get_fd_data_from_radar(run_params: RunParams, 
                           radar_module: RadarModule,
                           radar_sys_params: SysParams = get_radar_params()) -> FDDataMatrix:
    # Collect data
    radar_module.GetFdData(run_params.ramp_type)
    fd_data = get_FD_data_phase_data(radar_module, radarParams=radar_sys_params)
    
    # Print the FD data
    if run_params.runType == RunType.LIVE_RECORD:
        fd_data.print_data_to_file(run_params.recordedDataFolder)
    
    return fd_data

if __name__ == "__main__":  
    test = get_fd_data_from_radar(get_run_params(), get_radar_module())
    print("test")
