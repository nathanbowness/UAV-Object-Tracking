import numpy as np

# Cell-Averaging Smallest-Of Constant False Alarm Rate (CASO-CFAR) algorithm
# with a threshold derived from the smallest average of leading or lagging cells
# Output is the detected values above the threshold, 
def caso_cfar(input_signal, num_guard_cells, num_training_cells, threshold_db):
    num_cells = len(input_signal)
    half_window_size = num_guard_cells + num_training_cells
    output_signal = np.zeros_like(input_signal)
    
    # Convert the dB threshold to a linear scale
    threshold_factor = 10 ** (threshold_db / 20.0)

    for i in range(half_window_size, num_cells - half_window_size):
        lagging_cells = input_signal[i - half_window_size:i - num_guard_cells]
        leading_cells = input_signal[i + num_guard_cells + 1:i + half_window_size + 1]

        mean_lagging = np.mean(lagging_cells)
        mean_leading = np.mean(leading_cells)

        smallest_mean = min(mean_lagging, mean_leading)
        threshold = smallest_mean + threshold_db  # Add the relative dB threshold

        if input_signal[i] > threshold:
            output_signal[i] = input_signal[i]
        else:
            output_signal[i] = smallest_mean

    # Handle boundary cells by assigning the smallest available mean in the first and last sections
    for i in range(half_window_size):
        # Handle the beginning boundary
        if i < half_window_size - num_guard_cells:
            lagging_cells = input_signal[:i + num_training_cells]
            leading_cells = input_signal[i + num_guard_cells + 1:i + half_window_size + 1]
            smallest_mean = min(np.mean(lagging_cells), np.mean(leading_cells))
            threshold = smallest_mean + threshold_db
            output_signal[i] = input_signal[i] if input_signal[i] > threshold else smallest_mean

        # Handle the ending boundary
        end_index = num_cells - 1 - i
        if end_index >= num_cells - half_window_size + num_guard_cells:
            lagging_cells = input_signal[end_index - half_window_size:end_index - num_guard_cells]
            leading_cells = input_signal[end_index + num_guard_cells + 1:] if end_index + num_guard_cells + 1 < num_cells else []
            smallest_mean = min(np.mean(lagging_cells), np.mean(leading_cells)) if leading_cells else np.mean(lagging_cells)
            threshold = smallest_mean + threshold_db
            output_signal[end_index] = input_signal[end_index] if input_signal[end_index] > threshold else smallest_mean

    return output_signal

# TODO - Not sure this is right anymore based on the piece above
# Cell-Averaging Smallest-Of Constant False Alarm Rate (CASO-CFAR) algorithm
# with a threshold derived from the smallest average of leading or lagging cells
# Output is 1 if above the threshold, or 0 if below
def caso_cfar_absolute(input_signal, num_guard_cells, num_training_cells, threshold_factor):
    """
    Perform CASO-CFAR on input signal.

    Parameters:
    input_signal (array-like): The radar range bins input signal.
    num_guard_cells (int): Number of guard cells.
    num_training_cells (int): Number of training cells in each subgroup.
    threshold_factor (float): The scaling factor for threshold.

    Returns:
    array-like: CFAR output signal.
    """
    # Initialize output signal
    output_signal = np.zeros_like(input_signal)
    
    # Calculate the number of cells to be used
    num_cells = len(input_signal)
    half_window_size = num_guard_cells + num_training_cells

    for i in range(half_window_size, num_cells - half_window_size):
        # Define the lagging and leading subgroups
        lagging_cells = input_signal[i - half_window_size:i - num_guard_cells]
        leading_cells = input_signal[i + num_guard_cells + 1:i + half_window_size + 1]

        # Calculate the arithmetic mean of each subgroup
        mean_lagging = np.mean(lagging_cells)
        mean_leading = np.mean(leading_cells)

        # Determine the smallest arithmetic mean
        smallest_mean = min(mean_lagging, mean_leading)

        # Calculate the threshold
        threshold = smallest_mean * threshold_factor

        # Apply the threshold to the cell under test (CUT)
        if input_signal[i] > threshold:
            output_signal[i] = 1
        else:
            output_signal[i] = 0
            
    # Handle boundary cells by assigning the smallest available mean in the first and last sections
    if half_window_size > 0:
        for i in range(half_window_size):
            # Handle the beginning boundary
            if i < half_window_size - num_guard_cells:
                lagging_cells = input_signal[:i + num_training_cells]
                leading_cells = input_signal[i + num_guard_cells + 1:i + half_window_size + 1]
                smallest_mean = min(np.mean(lagging_cells), np.mean(leading_cells))
                threshold = smallest_mean * threshold_factor
                output_signal[i] = 1 if input_signal[i] > threshold else 0
            
            # Handle the ending boundary
            end_index = num_cells - 1 - i
            if end_index >= num_cells - half_window_size + num_guard_cells:
                lagging_cells = input_signal[end_index - half_window_size:end_index - num_guard_cells]
                leading_cells = input_signal[end_index + num_guard_cells + 1:] if end_index + num_guard_cells + 1 < num_cells else []
                smallest_mean = min(np.mean(lagging_cells), np.mean(leading_cells)) if leading_cells else np.mean(lagging_cells)
                threshold = smallest_mean * threshold_factor
                output_signal[end_index] = 1 if input_signal[end_index] > threshold else 0

    return output_signal


# Perform object detection on a stream of data, not implemented yet
def object_detection_on_stream():
    return None

# Perform object detection on fully in memory data
def object_detection_on_dict(data : dict):
    
    return None

