from RadarDevKit.RadarModule import RadarModule, GetRadarModule
from RadarDevKit.ConfigClasses import SysParams
from config import get_radar_params, get_ethernet_config
from older_contstants import SAVED_CSV_FILE_NAME
import time

import numpy as np
import csv

# Calculate the number of range bins the radar will return data for 
# and the range they correspond to                
def get_range_bins(radarModule: RadarModule):
    return [radarModule.sysParams.tic*n/radarModule.sysParams.zero_pad/1.0e6 for n in range(radarModule.sysParams.freq_points)]

# Get the FD data from the Radar
def get_FD_data(radarModule: RadarModule):
    # Process the FD data based on the data type
    if radarModule.sysParams.FFT_data_type == 0:  # only magnitudes were transmitted
        mag_data = radarModule.FD_Data.data
    elif radarModule.sysParams.FFT_data_type == 2:  # real/imaginary 
        comp_data = [complex(float(radarModule.FD_Data.data[n]), float(radarModule.FD_Data.data[n + 1])) for n in range(0, len(radarModule.FD_Data.data), 2)]
        mag_data = np.abs(comp_data)
    elif radarModule.sysParams.FFT_data_type in [1, 3]:  # magnitudes/phase or magnitudes/object angle
        mag_data = [radarModule.FD_Data.data[n] for n in range(0, len(radarModule.FD_Data.data), 2)]
    
    # Convert to dBm
    min_dbm = -60  # [dBm]
    for n in range(len(mag_data)):
        try:
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

    
# Colect FD data for a period of time, and write the results to a csv file
def collect_save_freq_data(radarModule: RadarModule, 
                           output_file: str = "samples.csv",
                           measurementType: str = "UP-Ramp", 
                           collectionDurationSec: int = 45):
    if not radarModule.connected:
        exit("Please connect radar module.")

    range_bins = get_range_bins(radarModule=radarModule)
    print("Collecting Data...")
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
    
        # Collect data for a period of time, and write results to a csv
        start_time = time.time()
        while time.time() - start_time < collectionDurationSec:
            radarModule.GetFdData(measurementType)
            timestamp = time.time() - start_time
            
            fd_data = get_FD_data(radarModule)
                    
            # Write data to a CSV in the following format
            # timestamp, range bin value, I1, Q1, I2, Q2 (the last 4 entries are the FD Magnitudes)
            for rb_index in range(len(range_bins)):
                row = [timestamp, range_bins[rb_index]]
                for ch in range(4):
                    row.append(fd_data[ch][rb_index])
                writer.writerow(row)
    
    print("Finished collecting data, written to {}", output_file)

def collect_data():
    # Collect data
    radarModule = GetRadarModule(updatedRadarParams=get_radar_params(), 
                                updatedEthernetConfig=get_ethernet_config())
    # radarModule = GetRadarModule(updatedEthernetConfig=get_ethernet_config())
    collect_save_freq_data(radarModule=radarModule, output_file=SAVED_CSV_FILE_NAME, collectionDurationSec=30)

if __name__ == "__main__":
    collect_data()