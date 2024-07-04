import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class PlotDetectionsDynamic:
    def __init__(self, num_plots=2, plot_titles=["Plot1", "Plot2"], max_steps=50, x_axis_values=512, interval=1000):
        self.num_plots = num_plots
        self.max_steps = max_steps
        self.x_axis_values = x_axis_values
        
        # Initialize data arrays based on the number of plots
        self.data = [np.zeros((max_steps, x_axis_values)) for _ in range(num_plots)]
        
        # Set up the plotting environment
        self.fig, self.axes = plt.subplots(num_plots, 1, figsize=(15, 8 * num_plots), squeeze=False)
        self.axes = self.axes.flatten()  # Flatten in case of a single subplot to keep indexing consistent
        self.scatters = []
        
        for i, ax in enumerate(self.axes):
            ax.set_xlim(0, x_axis_values)
            ax.set_ylim(0, max_steps)
            ax.set_xlabel('Range Bins')
            ax.set_ylabel('Measurement Time (steps)')
            ax.set_title(f'{plot_titles[i]}')
            scatter = ax.scatter([], [], marker='x', color='red' if i == 0 else 'blue')
            self.scatters.append(scatter)
        
        # Initialize the animation
        self.anim = FuncAnimation(self.fig, self.update_plot, init_func=self.init_plot, interval=interval, blit=True, cache_frame_data=True)

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