import numpy as np

from radar.configuration.CFARType import CfarType
from radar.configuration.CFARParams import CFARParams
    
def cfar_required_cells(cfar_params: CFARParams):
    if cfar_params.cfar_type == CfarType.CASO:
        return 2*(cfar_params.num_train + cfar_params.num_guard) + 1
    elif cfar_params.cfar_type == CfarType.LEADING_EDGE:
        return (cfar_params.num_train + cfar_params.num_guard)+1
    
def cfar_single(data, index_CUT, cfar_params: CFARParams):
    if cfar_params.cfar_type == CfarType.CASO:
        return caso_cfar_single(data, index_CUT, cfar_params)
    elif cfar_params.cfar_type == CfarType.LEADING_EDGE:
        return leading_edge_cfar_single(data, index_CUT, cfar_params)
    
def ca_cfar_detector(signal, num_training_cells, num_guard_cells, threshold_factor):
    """
    Cell-Averaging CFAR Detector.
    Equivalent to MATLAB phased.CFARDetector with 'Method', 'CA'.
    
    Parameters:
    - signal: 1D numpy array, the input radar signal.
    - num_training_cells: int, number of training cells on each side of the CUT.
    - num_guard_cells: int, number of guard cells on each side of the CUT.
    - threshold_factor: float, the scaling factor applied to the noise level to set the threshold.

    Returns:
    - cfar_detection: 1D boolean array, True where detections are found.
    - cfar_threshold: 1D array, threshold values for each CUT position.
    - noise_estimate: 1D array, estimated noise power from the training cells for each CUT.
    """
    num_cells = len(signal)
    cfar_threshold = np.zeros(num_cells)
    cfar_detection = np.zeros(num_cells, dtype=bool)
    noise_estimate = np.zeros(num_cells)

    # Loop over each cell to apply CA-CFAR
    for i in range(num_training_cells + num_guard_cells, num_cells - num_training_cells - num_guard_cells):
        # Define training cells on each side of the CUT
        leading_cells = signal[i + num_guard_cells + 1 : i + num_guard_cells + 1 + num_training_cells]
        lagging_cells = signal[i - num_guard_cells - num_training_cells : i - num_guard_cells]

        # Estimate noise by averaging the training cells
        noise_level = np.mean(np.concatenate((leading_cells, lagging_cells)))
        noise_estimate[i] = noise_level  # Store noise estimate for output
        threshold = threshold_factor * noise_level

        cfar_threshold[i] = threshold
        cfar_detection[i] = np.abs(signal[i]) > threshold  # Detection if CUT exceeds threshold

    return cfar_detection, cfar_threshold, noise_estimate

def cfar_ca_2(signal, num_training_cells=10, num_guard_cells=4, custom_threshold_factor=4):
    """
    Perform CA-CFAR detection on the given signal.

    Parameters:
        signal (numpy.ndarray): The input signal (power or amplitude).
        num_training_cells (int): Number of training cells used to estimate the noise.
        num_guard_cells (int): Number of guard cells to skip around the cell under test.
        custom_threshold_factor (float): The multiplier to adjust the detection threshold.

    Returns:
        detections (numpy.ndarray): Array indicating detected targets (1 if detected, 0 otherwise).
        threshold (numpy.ndarray): Calculated threshold for each cell under test.
        noise_estimate (numpy.ndarray): Estimated noise power for each cell under test.
    """
    num_cells = len(signal)
    num_side_cells = num_training_cells // 2
    cfar_window_size = num_training_cells + num_guard_cells
    
    # Initialize output arrays
    detections = np.zeros(num_cells)
    threshold = np.zeros(num_cells)
    noise_estimate = np.zeros(num_cells)
    
    # Loop over each cell under test (CUT)
    for i in range(num_side_cells + num_guard_cells, num_cells - num_side_cells - num_guard_cells):
        # Define the training cells excluding the guard cells around the CUT
        training_cells_left = signal[i - num_side_cells - num_guard_cells:i - num_guard_cells]
        training_cells_right = signal[i + num_guard_cells + 1:i + num_guard_cells + 1 + num_side_cells]
        training_cells = np.concatenate((training_cells_left, training_cells_right))
        
        # Estimate the noise power (average of training cells)
        noise_power = np.mean(training_cells)
        
        # Calculate the threshold
        threshold[i] = noise_power * custom_threshold_factor
        
        # Store the noise estimate
        noise_estimate[i] = noise_power
        
        # Detect if the CUT is above the threshold
        if signal[i] > threshold[i]:
            detections[i] = 1
    
    return detections, threshold, noise_estimate

# CFAR detection on the entire signal, including edge cells
def cfar_ca_full(signal, num_training_cells=10, num_guard_cells=4, custom_threshold_factor=4):
    """
    Perform CA-CFAR detection on the entire signal, including edge cells.

    Parameters:
        signal (numpy.ndarray): The input signal (power or amplitude).
        num_training_cells (int): Number of training cells used to estimate the noise.
        num_guard_cells (int): Number of guard cells to skip around the cell under test.
        custom_threshold_factor (float): The multiplier to adjust the detection threshold.

    Returns:
        detections (numpy.ndarray): Array indicating detected targets (1 if detected, 0 otherwise).
        threshold (numpy.ndarray): Calculated threshold for each cell under test.
        noise_estimate (numpy.ndarray): Estimated noise power for each cell under test.
    """
    num_cells = len(signal)
    cfar_window_size = num_training_cells + num_guard_cells

    # Initialize output arrays
    detections = np.zeros(num_cells)
    threshold = np.zeros(num_cells)
    noise_estimate = np.zeros(num_cells)

    # Loop over each cell under test (CUT)
    for i in range(num_cells):
        # Dynamically determine the number of available training cells on each side
        start_idx_left = max(0, i - num_training_cells // 2 - num_guard_cells)
        end_idx_left = max(0, i - num_guard_cells)
        
        start_idx_right = min(num_cells, i + num_guard_cells + 1)
        end_idx_right = min(num_cells, i + num_guard_cells + 1 + num_training_cells // 2)

        # Gather training cells from both sides
        training_cells_left = signal[start_idx_left:end_idx_left]
        training_cells_right = signal[start_idx_right:end_idx_right]
        training_cells = np.concatenate((training_cells_left, training_cells_right))
        
        # Estimate the noise power (average of training cells)
        if len(training_cells) > 0:
            noise_power = np.mean(training_cells)
        else:
            noise_power = 0
        
        # Calculate the threshold for the current CUT
        threshold[i] = noise_power * custom_threshold_factor
        noise_estimate[i] = noise_power

        # Perform detection
        if signal[i] > threshold[i]:
            detections[i] = 1

    return detections, threshold, noise_estimate

def caso_cfar(signal, num_training_cells, num_guard_cells, threshold_factor):
    """
    CASO CFAR Detection.
    signal: Input signal (1D array) to apply CFAR on.
    num_training_cells: Number of training cells on each side of the CUT.
    num_guard_cells: Number of guard cells on each side of the CUT.
    threshold_factor: Scaling factor for CFAR threshold.
    """
    num_cells = len(signal)
    cfar_threshold = np.zeros(num_cells)
    cfar_detection = np.zeros(num_cells, dtype=bool)

    # Loop over each cell to apply CASO CFAR
    for i in range(num_training_cells + num_guard_cells, num_cells - num_training_cells - num_guard_cells):
        # Define leading and lagging training cells
        leading_cells = signal[i + num_guard_cells + 1 : i + num_guard_cells + 1 + num_training_cells]
        lagging_cells = signal[i - num_guard_cells - num_training_cells : i - num_guard_cells]

        # Use the smaller of the two averages for CASO CFAR
        smallest_noise = min(np.mean(leading_cells), np.mean(lagging_cells))
        threshold = threshold_factor * smallest_noise

        cfar_threshold[i] = threshold
        if np.abs(signal[i]) > threshold:
            cfar_detection[i] = True

    return cfar_detection, cfar_threshold


# The functions below here may never be used, but are kept for reference
def caso_cfar_single(data, index_CUT, cfar_params: CFARParams):
    n = len(data)

    # Ensure the index has enough data around it to calculate
    if index_CUT < cfar_params.num_train + cfar_params.num_guard or index_CUT >= n - cfar_params.num_train - cfar_params.num_guard:
        return 0, 0  # Not enough data to perform CFAR at this index

    # Extract training cells around the CUT, excluding guard cells
    leading_train_cells = data[index_CUT - cfar_params.num_train - cfar_params.num_guard:index_CUT - cfar_params.num_guard]
    trailing_train_cells = data[index_CUT + cfar_params.num_guard + 1:index_CUT + cfar_params.num_guard + cfar_params.num_train + 1]

    # Calculate the average noise levels for leading and trailing training cells
    noise_level_leading = np.mean(leading_train_cells)
    noise_level_trailing = np.mean(trailing_train_cells)

    # Use the smaller of the two noise levels
    noise_level = min(noise_level_leading, noise_level_trailing)

    # Define the threshold
    if (cfar_params.threshold_is_percentage):
        threshold = noise_level + (abs(noise_level) * cfar_params.threshold)
    else:
        threshold = noise_level + cfar_params.threshold

    # Determine if the CUT exceeds the threshold
    signal_level = data[index_CUT]
    detection = 1 if signal_level > threshold else 0

    return detection, threshold
    
def leading_edge_cfar_single(data, index_CUT, cfar_params: CFARParams):
    n = len(data)
    
    # Ensure the index has enough data around it to calculate
    if index_CUT < cfar_params.num_train + cfar_params.num_guard:
        return 0, 0  # Not enough data to perform CFAR at this index

    # Extract training cells before the CUT, excluding guard cells
    training_cells = data[index_CUT - cfar_params.num_train - cfar_params.num_guard:index_CUT - cfar_params.num_guard]

    # Calculate the average noise level from the training cells
    noise_level = np.mean(training_cells)

    # Define the threshold directly using the fixed dBm value
    if (cfar_params.threshold_is_percentage):
        threshold = noise_level + (abs(noise_level) * cfar_params.threshold)
    else:
        threshold = noise_level + cfar_params.threshold

    # Determine if the CUT exceeds the threshold
    signal_level = data[index_CUT]
    detection = 1 if signal_level > threshold else 0
    
    return detection, threshold

def get_range_bin_for_index(index, bin_size):
    return index * bin_size

def get_range_bin_for_indexs(indexArray, bin_size):
    resultArray = None
    if indexArray is not None and indexArray.size > 0:
        resultArray = indexArray * bin_size
    return resultArray

def get_range_bins(bin_size):
    range_bins = np.arange(1, 513) * bin_size
    return range_bins

def get_range_bins_for_distance(min_bin_distance, max_bin_distance, bin_size):
    range_bins = get_range_bins(bin_size)
    selected_bins = [rb for rb in range_bins if min_bin_distance <= rb <= max_bin_distance]
    return selected_bins

def get_range_bin_indexes(min_bin_distance, max_bin_distance, bin_size):
    range_indexs = np.arange(1, 513)
    selected_indexes = [rb for rb in range_indexs if min_bin_distance <= rb*bin_size <= max_bin_distance]
    return np.array(selected_indexes)
