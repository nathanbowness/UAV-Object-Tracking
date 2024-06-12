from plot_captured_radar_data import read_data_from_csv, plot_fd_range_bins_in_grid, plot_heatmap, plot_comparison_heatmaps
from object_detection import caso_cfar, detect_peaks, smooth_signal, detect_peaks, cfar_using_peak
from constants import SAVED_CSV_FILE_NAME

import numpy as np
import matplotlib.pyplot as plt

def object_tracking_on_incoming_signal():
    return None

# Process the data across the time samples, looking at frequecy range across range bins
def process_data_across_samples(raw_data, guard_cells, subgroup, threshold_factor, use_peak: bool =True):
    
    cfar_data = {}

    # For each of the time_samples, perform the object detection
    for time_sample in raw_data:
        I1_signal = []
        Q1_signal = []
        I2_signal = []
        Q2_signal = []
        
        # For each of the range bins, pull them into an array
        for range_bin in raw_data[time_sample]:
            I1_signal.append(raw_data[time_sample][range_bin][0])
            Q1_signal.append(raw_data[time_sample][range_bin][1])
            I2_signal.append(raw_data[time_sample][range_bin][2])
            Q2_signal.append(raw_data[time_sample][range_bin][3])
            
        I1_signal = np.array(I1_signal)
        Q1_signal = np.array(Q1_signal)
        I2_signal = np.array(I2_signal)
        Q2_signal = np.array(Q2_signal)
        
        if use_peak:
            i1_output = cfar_using_peak(I1_signal, guard_cells, subgroup, threshold_factor)
            q1_output = cfar_using_peak(Q1_signal, guard_cells, subgroup, threshold_factor)
            i2_output = cfar_using_peak(I2_signal, guard_cells, subgroup, threshold_factor)
            q2_output = cfar_using_peak(Q2_signal, guard_cells, subgroup, threshold_factor)
        else:
            i1_output = caso_cfar(I1_signal, guard_cells, subgroup, threshold_factor, False)
            q1_output = caso_cfar(Q1_signal, guard_cells, subgroup, threshold_factor, False)
            i2_output = caso_cfar(I2_signal, guard_cells, subgroup, threshold_factor, False)
            q2_output = caso_cfar(Q2_signal, guard_cells, subgroup, threshold_factor, False)
        
        if time_sample not in cfar_data:
            cfar_data[time_sample] = {}

        for idx, range_bin_index in enumerate(sorted(raw_data[time_sample])):
            cfar_data[time_sample][range_bin_index] = [
                i1_output[idx], 
                q1_output[idx], 
                i2_output[idx], 
                q2_output[idx]
            ]
    return cfar_data

def process_data_across_bins(raw_data, guard_cells, subgroup, threshold_factor, use_peak: bool = True):
    
    cfar_data = {}

    # Get all range bins
    first_timestamp = next(iter(raw_data))
    range_bins = sorted(raw_data[first_timestamp].keys())

    for range_bin in range_bins:
        for i in range(4):
            signal_over_time = []

            for time_sample in sorted(raw_data.keys()):
                if range_bin in raw_data[time_sample]:
                    signal_over_time.append(raw_data[time_sample][range_bin][i])  # Use I1 signal for example

            signal_over_time = np.array(signal_over_time)
            
            if use_peak:
                # signal_over_time = smooth_signal(signal_over_time, 2)
                cfar_output = cfar_using_peak(signal_over_time, guard_cells, subgroup, threshold_factor)
            else:
                cfar_output = caso_cfar(signal_over_time, guard_cells, subgroup, threshold_factor, False)
                # cfar_output = caso_cfar(signal_over_time, guard_cells, subgroup, threshold_factor, False)
            
            for idx, time_sample in enumerate(sorted(raw_data.keys())):
                if time_sample not in cfar_data:
                    cfar_data[time_sample] = {}
                if range_bin not in cfar_data[time_sample]:
                    cfar_data[time_sample][range_bin] = [[] for _ in range(4)]
                cfar_data[time_sample][range_bin][i] = cfar_output[idx]
            
    return cfar_data

def main():
    raw_data = read_data_from_csv(SAVED_CSV_FILE_NAME)
    use_caso_cfar = True
    
    
    if use_caso_cfar:
        # Using Cell Averaging - Smallest Of
        guard_cells = 5
        subgroup = 20
        threshold_factor = 10
        
        # cfar_data = process_data_across_samples(raw_data, guard_cells, subgroup, threshold_factor, False)
        cfar_data = process_data_across_bins(raw_data, guard_cells, subgroup, threshold_factor, False)
    else:
        # Using Cell-Averaging CFAR
        guard_cells = 5
        subgroup = 20
        threshold_factor = 1.5    
        
        # cfar_data = process_data_across_samples(raw_data, guard_cells, subgroup, threshold_factor)
        cfar_data = process_data_across_bins(raw_data, guard_cells, subgroup, threshold_factor)
    
    # plot_heatmap(raw_data, 0, 100)
    plot_comparison_heatmaps(raw_data, cfar_data, 0, 60)

    print("test")

if __name__ == "__main__":
    main()