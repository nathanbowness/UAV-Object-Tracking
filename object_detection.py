import numpy as np
import matplotlib.pyplot as plt

def smooth_signal(x, window_size):
    """
    Smooths the signal using a moving average filter.
    
    x: Input signal array.
    window_size: Number of samples over which to average.
    """
    window = np.ones(int(window_size)) / float(window_size)
    return np.convolve(x, window, 'same')

def detect_peaks(x, num_train, num_guard, rate_fa):
    num_cells = x.size
    num_train_half = round(num_train / 2)
    num_guard_half = round(num_guard / 2)
    num_side = num_train_half + num_guard_half

    alpha = num_train * (rate_fa ** (-1 / num_train) - 1)  # threshold factor

    peak_at = []
    for i in range(num_side, num_cells - num_side):
        # Extract segments to calculate noise level and threshold
        start_train = i - num_side
        end_train = i + num_side + 1
        start_guard = i - num_guard_half
        end_guard = i + num_guard_half + 1
        
        # Compute the sum of the training cells excluding guard cells
        training_cells = np.r_[x[start_train:start_guard], x[end_guard:end_train]]
        p_noise = np.mean(training_cells)
        threshold = alpha * p_noise

        # Detect peaks considering both positive
        if (x[i] > p_noise + threshold):
            peak_at.append(i)

    return np.array(peak_at, dtype=int)

def detect_peaks_faster(x, num_train, num_guard, rate_fa):
    num_cells = x.size
    num_train_half = num_train // 2
    num_guard_half = num_guard // 2
    num_side = num_train_half + num_guard_half

    alpha = num_train * (rate_fa ** (-1 / num_train) - 1)  # threshold factor

    peak_at = []

    # Use a rolling window to calculate the noise level for each cell
    training_cells = np.array([np.concatenate((x[max(0, i - num_side):max(0, i - num_guard_half)], x[min(num_cells, i + num_guard_half + 1):min(num_cells, i + num_side + 1)])) for i in range(num_side, num_cells - num_side)])
    
    p_noise = np.mean(training_cells, axis=1)
    thresholds = alpha * p_noise

    # Detect peaks considering positive deviations
    for i in range(num_side, num_cells - num_side):
        if x[i] > p_noise[i - num_side] + thresholds[i - num_side]:
            peak_at.append(i)

    return np.array(peak_at, dtype=int)

def cfar_using_peak(input_signal, num_guard_cells, num_training_cells, rate_fa, show_caso=False, plot_graph=True):
    num_cells = len(input_signal)
    output_signal = np.zeros_like(input_signal)

    # Detect peaks using the provided method
    peak_indices = detect_peaks_faster(input_signal, num_training_cells, num_guard_cells, rate_fa)
    
    for i in range(num_cells):
        if i in peak_indices:
            output_signal[i] = input_signal[i]
        else:
            if show_caso:
                lagging_cells = input_signal[max(0, i - num_training_cells - num_guard_cells):i - num_guard_cells]
                leading_cells = input_signal[i + num_guard_cells + 1:min(num_cells, i + num_training_cells + num_guard_cells + 1)]

                mean_lagging = np.mean(lagging_cells) if len(lagging_cells) > 0 else 0
                mean_leading = np.mean(leading_cells) if len(leading_cells) > 0 else 0

                smallest_mean = min(mean_lagging, mean_leading)
                output_signal[i] = smallest_mean
            else:
                output_signal[i] = -50
                
    if plot_graph:
        plt.figure(figsize=(10, 6))
        plt.plot(input_signal, label='Input Signal')
        
        # Plot only the valid detections as 'x' markers
        valid_detections = [i for i in range(num_cells) if output_signal[i] > -50]
        plt.scatter(valid_detections, [output_signal[i] for i in valid_detections], color='red', marker='x', label='Detections')

        plt.title('Input Signal For Range Bin vs Detections')
        plt.xlabel('Sample Index')
        plt.ylabel('Signal Power Ratio (dBm)')
        plt.legend()
        plt.grid(True)
        plt.show()

    return output_signal

def caso_cfar(input_signal, num_guard_cells, num_training_cells, threshold_factor, show_caso=True):
    num_cells = len(input_signal)
    half_window_size = num_guard_cells + num_training_cells
    output_signal = np.zeros_like(input_signal)

    for i in range(half_window_size, num_cells - half_window_size):
        lagging_cells = input_signal[i - half_window_size:i - num_guard_cells]
        leading_cells = input_signal[i + num_guard_cells + 1:i + half_window_size + 1]

        mean_lagging = np.mean(lagging_cells)
        mean_leading = np.mean(leading_cells)

        smallest_mean = min(mean_lagging, mean_leading)
        threshold = smallest_mean + threshold_factor

        if input_signal[i] > threshold:
            output_signal[i] = input_signal[i]
        else:
            if show_caso:
                output_signal[i] = smallest_mean
            else:
                output_signal[i] = -50

    return output_signal

# Perform object detection on a stream of data, not implemented yet
def object_detection_on_stream():
    return None

# Perform object detection on fully in memory data
def object_detection_on_dict(data : dict):
    
    return None

