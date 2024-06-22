import matplotlib.pyplot as plt
import numpy as np

from resources.FDDataMatrix import FDSignalType

class FreqSignalPlot:
    def __init__(self, bin_index, fdDataType: FDSignalType, ylim=(-1, 1), xlim=(0, 512)):
        plt.ion()  # Turn on interactive plotting mode
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'r-')  # Initialize an empty line plot
        # self.ax.set_xlim(xlim)  # Set x-axis limit
        # self.ax.set_ylim(ylim)  # Set y-axis limit
        self.ax.set_xlabel('Relative Time Since Start (s)')
        self.ax.set_ylabel(f'{fdDataType.name} Signal Amplitude')
        self.ax.set_title(f'Real-time {fdDataType.name} Signals at Bin Index {bin_index}')
        self.bin_index = bin_index

    def update_plot(self, signals, plot_timedelta):
        self.line.set_xdata(plot_timedelta)  # Update x data
        self.line.set_ydata(signals)  # Update y data
        self.ax.relim()  # Re-compute the data limits
        self.ax.autoscale_view()  # Automatically adjust the scale view to the data
        self.fig.canvas.draw()  # Redraw the figure
        self.fig.canvas.flush_events()
        plt.pause(0.01)  # Short pause to allow for GUI events

    def close(self):
        plt.ioff()  # Turn off interactive plotting mode
        plt.close(self.fig)