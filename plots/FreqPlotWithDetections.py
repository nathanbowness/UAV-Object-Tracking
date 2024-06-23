import matplotlib.pyplot as plt
import numpy as np

from resources.FDDataMatrix import FDSignalType

class FreqSignalPlotWithDetections:
    def __init__(self, bin_index, fdDataType, smoothing_window: int = 0):
        plt.ion()  # Turn on interactive plotting mode
        self.fig, self.ax = plt.subplots()
        self.raw_signal_line, = self.ax.plot([], [], 'r-', label='Raw Signal')
        # Initialize detections line differently, we'll update markers only when needed
        self.detections_line, = self.ax.plot([], [], 'bx', label='Detections')  # Use 'x' marker
        self.threshold_line, = self.ax.plot([], [], 'g-', label='Threshold')
        self.smoothing_window = smoothing_window
        
        # self.ax.set_xlim(xlim)
        # self.ax.set_ylim(ylim)
        self.ax.set_xlabel('Relative Time Since Start (s)')
        self.ax.set_ylabel(f'{fdDataType.name} Signal Amplitude')
        self.ax.set_title(f'Real-time {fdDataType.name} Signals and Detections Using CFAR at Bin Index {bin_index}')
        self.ax.legend()
        self.bin_index = bin_index

    def update_plot(self, raw_signals, plot_timedelta, detections, threshold):
        if self.smoothing_window:
            raw_signals = self.smooth_signal(raw_signals, self.smoothing_window)

        # Raw signals
        self.raw_signal_line.set_xdata(plot_timedelta)
        self.raw_signal_line.set_ydata(raw_signals)
        
        # Thresholds
        self.threshold_line.set_xdata(plot_timedelta)
        self.threshold_line.set_ydata(threshold)
        
        # Update detections with markers only where detections are 1
        detected_indices = [i for i, x in enumerate(detections) if x == 1]
        self.detections_line.set_xdata([plot_timedelta[i] for i in detected_indices])
        self.detections_line.set_ydata([raw_signals[i] for i in detected_indices])
        
        self.ax.relim()  # Re-compute the data limits
        self.ax.autoscale_view()  # Automatically adjust the scale view to the data
        self.fig.canvas.draw()  # Redraw the figure
        self.fig.canvas.flush_events()
        plt.pause(0.01)  # Short pause to allow for GUI events

    def close(self):
        plt.ioff()  # Turn off interactive plotting mode
        plt.close(self.fig)
        
    @staticmethod
    def smooth_signal(x, window_size):
        """
        Smooths the signal using a moving average filter.
        
        x: Input signal array.
        window_size: Number of samples over which to average.
        """
        window = np.ones(int(window_size)) / float(window_size)
        return np.convolve(x, window, 'same')

# class FreqSignalPlotWithDetections:
#     def __init__(self, bin_index, fdDataType: FDSignalType, ylim=(-1, 1), xlim=(0, 512)):
#         plt.ion()  # Turn on interactive plotting mode
#         self.fig, self.ax = plt.subplots()
#         self.raw_signal_line, = self.ax.plot([], [], 'r-', label='Raw Signal')
#         self.detections_line, = self.ax.plot([], [], 'b-', label='Detections')  
#         self.threshold_line, = self.ax.plot([], [], 'g-', label='Threshold')  
#         # self.ax.set_xlim(xlim)  # Set x-axis limit
#         # self.ax.set_ylim(ylim)  # Set y-axis limit
#         self.ax.set_xlabel('Relative Time Since Start (s)')
#         self.ax.set_ylabel(f'{fdDataType.name} Signal Amplitude')
#         self.ax.set_title(f'Real-time {fdDataType.name} Signals and Detections Using CFAR at Bin Index {bin_index}')
#         self.ax.legend() 
#         self.bin_index = bin_index

#     def update_plot(self, raw_signals, plot_timedelta, detections, threshold):
#         # Raw signals
#         self.raw_signal_line.set_xdata(plot_timedelta)
#         self.raw_signal_line.set_ydata(raw_signals)
#         # Detections
#         self.detections_line.set_xdata(plot_timedelta) 
#         self.detections_line.set_ydata(detections)
#         # Thresholds
#         self.threshold_line.set_xdata(plot_timedelta) 
#         self.threshold_line.set_ydata(threshold)
        
#         self.ax.relim()  # Re-compute the data limits
#         self.ax.autoscale_view()  # Automatically adjust the scale view to the data
#         self.fig.canvas.draw()  # Redraw the figure
#         self.fig.canvas.flush_events()
#         plt.pause(0.01)  # Short pause to allow for GUI events

#     def close(self):
#         plt.ioff()  # Turn off interactive plotting mode
#         plt.close(self.fig)