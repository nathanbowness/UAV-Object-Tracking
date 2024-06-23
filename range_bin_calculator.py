import numpy as np

def get_range_bin_for_index(index, bin_size):
    return index * bin_size

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

