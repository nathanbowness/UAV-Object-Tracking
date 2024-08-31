import numpy as np

from config import get_cfar_params
from radar_object_tracking.configuration.CFARType import CfarType
from radar_object_tracking.configuration.CFARParams import CFARParams
    
def cfar_required_cells(cfar_params: CFARParams = get_cfar_params()):
    if cfar_params.cfar_type == CfarType.CASO:
        return 2*(cfar_params.num_train + cfar_params.num_guard) + 1
    elif cfar_params.cfar_type == CfarType.LEADING_EDGE:
        return (cfar_params.num_train + cfar_params.num_guard)+1
    
def cfar_single(data, index_CUT, cfar_params: CFARParams = get_cfar_params()):
    if cfar_params.cfar_type == CfarType.CASO:
        return caso_cfar_single(data, index_CUT, cfar_params)
    elif cfar_params.cfar_type == CfarType.LEADING_EDGE:
        return leading_edge_cfar_single(data, index_CUT, cfar_params)
    
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

    
