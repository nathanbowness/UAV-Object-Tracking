from constants import SAVED_CSV_FILE_NAME

import matplotlib.pyplot as plt
import csv
import numpy as np

def read_data_from_csv(input_file):
    data = {}
    
    with open(input_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        
        for row in reader:
            timestamp = float(row[0])
            range_bin_index = float(row[1])
            data_columns = list(map(float, row[2:6]))
            
            if timestamp not in data:
                data[timestamp] = {}
            
            data[timestamp][range_bin_index] = data_columns
    return data

def plot_fd_range_bins_in_grid(data, min_bin, max_bin):
    first_timestamp = next(iter(data))
    range_bins = list(data[first_timestamp].keys()) # Get the range_bins from the first data sample
    
    selected_bins = [rb for rb in range_bins if min_bin <= rb <= max_bin]
    num_bins = min(20, len(selected_bins))  # Ensure we only plot up to 20 bins

    num_rows = (num_bins + 4) // 5  # Calculate number of rows needed
    fig, axs = plt.subplots(num_rows, 5, figsize=(28, 4 * num_rows))  # Adjust height based on rows
    
    # Flatten axs array for easy iteration and handle cases where axs is not a 2D array
    if num_bins == 1:
        axs = [axs]
    else:
        axs = axs.flatten()

    for i, rb in enumerate(selected_bins[:num_bins]):
        # Prepare data for plotting
        times = []
        values = {1: [], 2: [], 3: [], 4: []}

        for timestamp in data:
            if rb in data[timestamp]:
                fd_values = data[timestamp][rb]
                times.append(timestamp)
                for ch in range(4):
                    values[ch + 1].append(fd_values[ch])
        
        # Plot the data for this range bin
        title = f"FD for Range Bin {rb} meters"
        if values[1]:
            axs[i].plot(times, values[1], label="I1")
        if values[2]:
            axs[i].plot(times, values[2], label="Q1")
        if values[3]:
            axs[i].plot(times, values[3], label="I2")
        if values[4]:
            axs[i].plot(times, values[4], label="Q2")
        axs[i].set_title(title)
        axs[i].set_xlabel("Time (s)")
        axs[i].set_ylabel("Magnitude [dBm]")
        axs[i].legend()
        axs[i].grid(True)
    
    # Hide any unused subplots
    for j in range(num_bins, len(axs)):
        fig.delaxes(axs[j])

    plt.tight_layout()
    plt.show()   

def prepare_heatmap_data(data, min_bin, max_bin):
    timestamps = sorted(data.keys())
    range_bins = sorted(data[timestamps[0]].keys())
    
    selected_bins = [rb for rb in range_bins if min_bin <= rb <= max_bin]
    num_bins = len(selected_bins)
    num_timestamps = len(timestamps)
    
    heatmap_data = np.zeros((num_timestamps, num_bins))
    
    for t_idx, timestamp in enumerate(timestamps):
        for r_idx, range_bin in enumerate(selected_bins):
            if range_bin in data[timestamp]:
                # heatmap_data[t_idx, r_idx] = data[timestamp][range_bin][0]  # Use I1 signal for example
                heatmap_data[t_idx, r_idx] = max(data[timestamp][range_bin][0], data[timestamp][range_bin][1], data[timestamp][range_bin][2], data[timestamp][range_bin][3])  # Max of all datapoints
    
    return heatmap_data, timestamps, selected_bins

def plot_heatmap(data, min_bin, max_bin):
    heatmap_data, timestamps, selected_bins = prepare_heatmap_data(data, min_bin, max_bin)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    cax = ax.imshow(heatmap_data, aspect='auto', cmap='jet', origin='lower', extent=[min_bin, max_bin, timestamps[0], timestamps[-1]])
    ax.set_title('Raw Radar Data Heatmap')
    ax.set_xlabel('Slant Range (m)')
    ax.set_ylabel('Measurement Time (s)')
    fig.colorbar(cax, ax=ax, label='Signal Power Ratio (dBm)')
    
    plt.tight_layout()
    plt.show()
    
def plot_comparison_heatmaps(raw_data, processed_data, min_bin, max_bin):
    raw_heatmap_data, timestamps, selected_bins = prepare_heatmap_data(raw_data, min_bin, max_bin)
    processed_heatmap_data, _, _ = prepare_heatmap_data(processed_data, min_bin, max_bin)
    
    fig, axs = plt.subplots(1, 2, figsize=(24, 8))

    # Plot raw data heatmap
    c1 = axs[0].imshow(raw_heatmap_data, aspect='auto', cmap='jet', origin='lower', extent=[min_bin, max_bin, timestamps[0], timestamps[-1]])
    axs[0].set_title('Raw Radar Data')
    axs[0].set_xlabel('Slant Range (m)')
    axs[0].set_ylabel('Measurement Time (s)')
    fig.colorbar(c1, ax=axs[0], label='Signal Power Ratio (dBm)')

    # Plot processed data heatmap
    c2 = axs[1].imshow(processed_heatmap_data, aspect='auto', cmap='jet', origin='lower', extent=[min_bin, max_bin, timestamps[0], timestamps[-1]])
    axs[1].set_title('Processed Radar Data')
    axs[1].set_xlabel('Slant Range (m)')
    axs[1].set_ylabel('Measurement Time (s)')
    fig.colorbar(c2, ax=axs[1], label='Signal Power Ratio (dBm)')

    plt.tight_layout()
    plt.show()
    
if __name__ == "__main__":
    raw_data = read_data_from_csv(SAVED_CSV_FILE_NAME)
    min_bin = 0
    max_bin = 2
    
    plot_fd_range_bins_in_grid(raw_data, 0, 3)  # Adjust min_range_bin, max_rang_bin sizes
    plot_heatmap(raw_data, 0, 6)
    print("Finished plotting the data.")