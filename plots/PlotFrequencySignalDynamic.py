import matplotlib.pyplot as plt
import numpy as np

from radarprocessing.FDDataMatrix import FDSignalType

class PlotFreqSignalDynamic:
    def __init__(self, bin_index, fdDataType: FDSignalType, smoothing_window: int = 0):
        plt.ion()  # Turn on interactive plotting mode
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'r-')  # Initialize an empty line plot
        # self.ax.set_xlim(xlim)  # Set x-axis limit
        # self.ax.set_ylim(ylim)  # Set y-axis limit
        self.smoothing = smoothing_window
        self.ax.set_xlabel('Relative Time Since Start (s)')
        self.ax.set_ylabel(f'{fdDataType.name} Signal Amplitude')
        self.ax.set_title(f'Real-time {fdDataType.name} Signals at Bin Index {bin_index}')
        self.bin_index = bin_index

    def update_plot(self, signals, plot_timedelta):
        if self.smoothing:
            signals = self.smooth_signal(signals, self.smoothing)
        
        self.line.set_xdata(plot_timedelta)  # Update x data
        self.line.set_ydata(signals)  # Update y data
        self.ax.relim()  # Re-compute the data limits
        self.ax.autoscale_view()  # Automatically adjust the scale view to the data
        self.fig.canvas.draw()  # Redraw the figure
        self.fig.canvas.flush_events()
        plt.pause(0.01)  # Short pause to allow for GUI events
        
    @staticmethod
    def smooth_signal(x, window_size):
        """
        Smooths the signal using a moving average filter.
        
        x: Input signal array.
        window_size: Number of samples over which to average.
        """
        window = np.ones(int(window_size)) / float(window_size)
        return np.convolve(x, window, 'same')

    def close(self):
        plt.ioff()  # Turn off interactive plotting mode
        plt.close(self.fig)