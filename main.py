from plot_captured_radar_data import read_data_from_csv, plot_fd_range_bins_in_grid, plot_heatmap, plot_comparison_heatmaps
from object_detection import caso_cfar, caso_cfar_absolute_value_comparison

def object_tracking_on_incoming_signal():
    return None

def main():
    raw_data = read_data_from_csv("samples.csv")
    
    gaurd_cells = 5
    subgroup = 25
    threshold_db = 15
    threshold_linear = 15
    
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
        
        # i1_output = caso_cfar(I1_signal, gaurd_cells, subgroup, threshold_db)
        # q1_output = caso_cfar(Q1_signal, gaurd_cells, subgroup, threshold_db)
        # i2_output = caso_cfar(I2_signal, gaurd_cells, subgroup, threshold_db)
        # q2_output = caso_cfar(Q2_signal, gaurd_cells, subgroup, threshold_db)
        i1_output = caso_cfar_absolute_value_comparison(I1_signal, gaurd_cells, subgroup, threshold_linear)
        q1_output = caso_cfar_absolute_value_comparison(Q1_signal, gaurd_cells, subgroup, threshold_linear)
        i2_output = caso_cfar_absolute_value_comparison(I2_signal, gaurd_cells, subgroup, threshold_linear)
        q2_output = caso_cfar_absolute_value_comparison(Q2_signal, gaurd_cells, subgroup, threshold_linear)
        
        if time_sample not in cfar_data:
            cfar_data[time_sample] = {}

        for idx, range_bin_index in enumerate(sorted(raw_data[time_sample])):
            cfar_data[time_sample][range_bin_index] = [
                i1_output[idx], 
                q1_output[idx], 
                i2_output[idx], 
                q2_output[idx]
            ]
            
    # Plot the CFAR results
    # plot_fd_range_bins_in_grid(cfar_data, 0, 2)  # Adjust min_bin and max_bin as needed
    
    # plot_heatmap(raw_data, 0, 100)
    plot_comparison_heatmaps(raw_data, cfar_data, 0, 5)

    print("test")

if __name__ == "__main__":
    main()