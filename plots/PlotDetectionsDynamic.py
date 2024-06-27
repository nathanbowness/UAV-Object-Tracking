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
        self.anim = FuncAnimation(self.fig, self.update_plot, init_func=self.init_plot, interval=interval, blit=True, cache_frame_data=False)

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


# class PlotDetectionsPerReciever:
#     def __init__(self, max_steps=50, x_axis_values = 512, interval=1000):
#         self.max_steps = max_steps
#         self.data1 = np.zeros((max_steps, x_axis_values))  # Store the latest 50 data entries for the first subplot
#         self.data2 = np.zeros((max_steps, x_axis_values))  # Same for the second subplot

#         # Set up the plotting environment
#         self.fig, self.axes = plt.subplots(2, 1, figsize=(15, 16))  # Use two subplots
#         for ax in self.axes:
#             ax.set_xlim(0, x_axis_values)  # 512 range bins
#             ax.set_ylim(0, max_steps)  # Display up to 50 time steps
#             ax.set_xlabel('Range Bins')
#             ax.set_ylabel('Measurement Time (steps)')

#         self.scat1 = self.axes[0].scatter([], [], marker='x', color='red')
#         self.scat2 = self.axes[1].scatter([], [], marker='x', color='blue')
#         self.axes[0].set_title('Rx1 Detections')
#         self.axes[1].set_title('Rx2 Detections')

#         # Initialize the animation
#         self.anim = FuncAnimation(self.fig, self.update_plot, init_func=self.init_plot, interval=interval, blit=True, cache_frame_data=False)

#     def init_plot(self):
#         # Initial empty setup for scatter plots
#         self.scat1.set_offsets(np.empty((0, 2)))
#         self.scat2.set_offsets(np.empty((0, 2)))
#         return self.scat1, self.scat2

#     def update_data(self, new_data1, new_data2):
#         # Roll the data to make room for new entries
#         self.data1 = np.roll(self.data1, -1, axis=0)
#         self.data2 = np.roll(self.data2, -1, axis=0)
#         self.data1[-1, :] = new_data1
#         self.data2[-1, :] = new_data2

#     def update_plot(self, frame):
#         # Find indices where data is 1 and update scatter plot offsets
#         y, x = np.where(self.data1 == 1)
#         self.scat1.set_offsets(np.c_[x, self.max_steps - 1 - y])  # Update scatter plot for data1
#         y, x = np.where(self.data2 == 1)
#         self.scat2.set_offsets(np.c_[x, self.max_steps - 1 - y])  # Update scatter plot for data2
#         return self.scat1, self.scat2


# class PlotDetectionsPerReciever:
#     def __init__(self, max_steps=50, interval=100):
#         """
#         Initializes the real-time plotter with two subplots.
#         :param max_steps: Number of time steps to display on the y-axis.
#         :param interval: Time interval in milliseconds between updates.
#         """
#         self.max_steps = max_steps
#         self.interval = interval
#         self.data1 = np.zeros((max_steps, 512), dtype=int)
#         self.data2 = np.zeros((max_steps, 512), dtype=int)

#         # Set up the plotting environment
#         plt.ion()
#         self.fig, self.axes = plt.subplots(2, 1, figsize=(10, 8))
#         for ax in self.axes:
#             ax.set_xlim(0, 511)
#             ax.set_ylim(0, self.max_steps)
#             ax.set_xlabel('Range Bins')
#             ax.set_ylabel('Time Steps')
        
#         # Initialize plots
#         self.img1 = self.axes[0].imshow(self.data1, aspect='auto', origin='lower', ) # extent=[0, 511, 0, self.max_steps]
#         self.img2 = self.axes[1].imshow(self.data2, aspect='auto', origin='lower', ) # extent=[0, 511, 0, self.max_steps]
#         self.axes[0].set_title('Data 1')
#         self.axes[1].set_title('Data 2')

#         # Start the animation
#         self.ani = FuncAnimation(self.fig, self.update_plot, interval=self.interval)

#     def update_data(self, new_data1, new_data2):
#         """
#         Updates the data buffers with new data.
#         :param new_data1: New data for the first subplot (shape (512,)).
#         :param new_data2: New data for the second subplot (shape (512,)).
#         """
#         # Roll the data to make room for the new data
#         self.data1 = np.roll(self.data1, -1, axis=0)
#         self.data2 = np.roll(self.data2, -1, axis=0)

#         # Insert the new data
#         self.data1[-1, :] = new_data1
#         self.data2[-1, :] = new_data2

#     def update_plot(self, frame):
#         """
#         Update function for the FuncAnimation.
#         """
#         # Update scatter plot data
#         y, x = np.where(self.data1 == 1)
#         self.scat1.set_offsets(np.column_stack((x, y)))
#         y, x = np.where(self.data2 == 1)
#         self.scat2.set_offsets(np.column_stack((x, y)))
#         return self.scat1, self.scat2
    
#     def show(self):
#         # Show the plot without blocking.
#         plt.show(block=False)

#     def close(self):
#         """
#         Closes the plot and stops the animation.
#         """
#         plt.ioff()
#         plt.close(self.fig)