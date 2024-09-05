import numpy as np

import matplotlib
matplotlib.use('Qt5Agg')  # Use Qt5Agg backend for GUI support
import matplotlib.pyplot as plt
plt.ion()
from matplotlib.animation import FuncAnimation

import numpy as np
from radar_object_tracking.cfar import get_range_bins

class PlotDetectionsDynamic:
    def __init__(self, bin_size=0.27, num_plots=2, plot_titles=["Plot1", "Plot2"], max_steps=50, x_axis_values=512, max_bins=512, interval=1000):
        self.num_plots = num_plots
        self.max_steps = max_steps
        self.x_axis_values = x_axis_values
        self.range_bins = get_range_bins(bin_size)
        
        # Initialize data arrays based on the number of plots
        self.data = [np.zeros((max_steps, x_axis_values)) for _ in range(num_plots)]
        
        # Set up the plotting environment
        self.fig, self.axes = plt.subplots(num_plots, 1, figsize=(13, 7 * num_plots), squeeze=False)
        self.axes = self.axes.flatten()  # Flatten in case of a single subplot to keep indexing consistent
        self.scatters = []
        
        for i, ax in enumerate(self.axes):
            ax.set_xlim(0, max_bins)
            ax.set_ylim(0, max_steps)
            ax.set_xlabel('Range (m)', fontsize=12)
            ax.set_ylabel('Measurement Time (steps)', fontsize=12)
            ax.set_title(f'{plot_titles[i]}', fontsize=18)
            
            # Set x-axis ticks and labels to range bins
            ax.set_xticks(np.arange(0, max_bins, step=max_bins//10))
            ax.set_xticklabels([f'{self.range_bins[idx]:.1f}' for idx in range(0, max_bins, max_bins//10)])
            
            scatter = ax.scatter([], [], marker='x', color='red' if i == 0 else 'blue')
            self.scatters.append(scatter)
        
        # Initialize the animation
        self.anim = FuncAnimation(self.fig, self.update_plot, init_func=self.init_plot, interval=interval, blit=True, cache_frame_data=True)
        plt.show(block=False)
        plt.ion()

    def init_plot(self):
        for scatter in self.scatters:
            scatter.set_offsets(np.empty((0, 2)))
        return self.scatters

    def update_data(self, new_data):
        # Update data for each plot
        for i, data in enumerate(new_data):
            self.data[i] = np.roll(self.data[i], -1, axis=0)
            self.data[i][-1, :] = data

    def update_plot(self, frame):
        results = []
        for i, (scatter, data) in enumerate(zip(self.scatters, self.data)):
            y, x = np.where(data == 1)
            scatter.set_offsets(np.c_[x, self.max_steps - 1 - y])
            results.append(scatter)
        return results