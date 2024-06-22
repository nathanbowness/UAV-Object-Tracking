from enum import Enum
import numpy as np

class CfarType(Enum):
    CASO = 0,
    LEADING_EDGE = 1
    
def cfar_required_cells(num_train: int, num_guard: int, cfar_type: CfarType = CfarType.CASO):
    if cfar_type == CfarType.CASO:
        return 2*(num_train+num_guard) + 1
    elif cfar_type == CfarType.LEADING_EDGE:
        return (num_train+num_guard)+1
    
def cfar_single(data , num_train: int, num_guard: int, index_CUT:int, threshold:float=10.0, cfar_type: CfarType = CfarType.CASO):
    if cfar_type == CfarType.CASO:
        return caso_cfar_single(data, num_train, num_guard, index_CUT, threshold)
    elif cfar_type == CfarType.LEADING_EDGE:
        return leading_edge_cfar_single(data, num_train, num_guard, index_CUT, threshold)
    
def caso_cfar_single(data, num_train, num_guard, index_CUT, threshold):
    n = len(data)

    # Ensure the index has enough data around it to calculate
    if index_CUT < num_train + num_guard or index_CUT >= n - num_train - num_guard:
        return 0, 0  # Not enough data to perform CFAR at this index

    # Extract training cells around the CUT, excluding guard cells
    leading_train_cells = data[index_CUT - num_train - num_guard:index_CUT - num_guard]
    trailing_train_cells = data[index_CUT + num_guard + 1:index_CUT + num_guard + num_train + 1]

    # Calculate the average noise levels for leading and trailing training cells
    noise_level_leading = np.mean(leading_train_cells)
    noise_level_trailing = np.mean(trailing_train_cells)

    # Use the smaller of the two noise levels
    noise_level = min(noise_level_leading, noise_level_trailing)

    # Define the threshold
    threshold_factor = 1.4  # Adjustable based on required false alarm rates
    threshold = noise_level + threshold

    # Determine if the CUT exceeds the threshold
    signal_level = data[index_CUT]
    detection = 1 if signal_level > threshold else 0

    return detection, threshold
    
def leading_edge_cfar_single(data, num_train, num_guard, index_CUT, threshold):
    n = len(data)
    
    # Ensure the index has enough data around it to calculate
    if index_CUT < num_train + num_guard:
        return 0, 0  # Not enough data to perform CFAR at this index

    # Extract training cells before the CUT, excluding guard cells
    training_cells = data[index_CUT - num_train - num_guard:index_CUT - num_guard]

    # Calculate the average noise level from the training cells
    noise_level = np.mean(training_cells)

    # Define the threshold directly using the fixed dBm value
    threshold = noise_level + threshold

    # Determine if the CUT exceeds the threshold
    signal_level = data[index_CUT]
    detection = 1 if signal_level > threshold else 0
    
    return detection, threshold

    
