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
    
    
data = read_data_from_csv('samples.csv')
plot_fd_range_bins_in_grid(data, 0, 2)  # Adjust min_range_bin, max_rang_bin sizes
print("Finished plotting the data.")