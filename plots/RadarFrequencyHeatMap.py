import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from range_bin_calculator import get_range_bin_indexes

class RadarFrequencyHeatMap:
    def __init__(self, title, min_distance=0, max_distance=None, range_bin_size=0.2499, max_steps=50):
        self.title = title
        self.fig, self.ax = plt.subplots(figsize=(15, 8))
        self.max_steps = max_steps
        self.time_since_start = np.zeros(max_steps)
        self.range_increment = range_bin_size
        
        if max_distance is None:
            max_distance = 512 * range_bin_size
        
        self.valid_indices = get_range_bin_indexes(min_distance, max_distance, range_bin_size)
        self.radar_signal_for_bins = np.zeros((max_steps, len(self.valid_indices)))
        self.range_bins = self.valid_indices * range_bin_size
        self.anim = FuncAnimation(self.fig, self.update_plot, init_func=self.init_plot, interval=1000, cache_frame_data=False)

    def init_plot(self):
        # This sets up an initial blank image
        self.im = self.ax.imshow(np.zeros((self.max_steps, len(self.valid_indices))), aspect='auto', cmap='jet', origin='lower')
        self.ax.set_ylabel('Measurement Time (s)')
        self.ax.set_xlabel('Slant Range (m)')
        self.ax.set_title(self.title)
        plt.colorbar(self.im, ax=self.ax, label='Signal Power Ratio (dBm)')
        return self.im,

    def update_data(self, new_time, new_signal):
        # Roll the data to make room for new entries
        self.time_since_start = np.roll(self.time_since_start, -1)
        self.time_since_start[-1] = new_time
        self.radar_signal_for_bins = np.roll(self.radar_signal_for_bins, -1, axis=0)
        self.radar_signal_for_bins[-1] = new_signal[self.valid_indices]

    def update_plot(self, frame):
        if self.radar_signal_for_bins.size > 0:
            self.im.set_data(self.radar_signal_for_bins)
            self.im.set_clim(vmin=self.radar_signal_for_bins.min(), vmax=self.radar_signal_for_bins.max())
            self.im.set_extent([0, self.range_bins[-1], self.time_since_start[0], self.time_since_start[-1]])
        return self.im,

    def show(self):
        plt.show(block=False)