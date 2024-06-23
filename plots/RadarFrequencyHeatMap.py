import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from range_bin_calculator import get_range_bin_indexes

class RadarFrequencyHeatMap():
    def __init__(self, min_distance=0, max_distance=None, range_bin_size=0.2499):
        self.fig, self.ax = plt.subplots(figsize=(15, 8))
        self.im = None
        self.time_since_start = []
        self.radar_signal_for_bins = []
        self.range_increment = range_bin_size
        
        if (max_distance is None):
            max_distance = 512*range_bin_size
        
        self.valid_indices = get_range_bin_indexes(min_distance, max_distance, range_bin_size)
        self.range_bins = self.valid_indices * range_bin_size
        self.anim = FuncAnimation(self.fig, self.update_plot, init_func=self.init_plot, interval=1000, cache_frame_data=False)

    def init_plot(self):
        # This sets up an initial blank image
        self.im = self.ax.imshow(np.zeros((1, 512)), aspect='auto', cmap='jet', origin='lower')
        self.ax.set_ylabel('Measurement Time (s)')
        self.ax.set_xlabel('Slant Range (m)')
        self.ax.set_title('Radar Signal Heatmap')
        plt.colorbar(self.im, ax=self.ax, label='Signal Power Ratio (dBm)')
        return self.im,

    def update_data(self, new_time_since_start, new_radar_signal_for_bins):
        self.time_since_start = new_time_since_start
        self.radar_signal_for_bins = new_radar_signal_for_bins[:,self.valid_indices]

    def update_plot(self, frame):
        if len(self.radar_signal_for_bins) > 0 and len(self.time_since_start) > 0:
            radar_signal_array = np.array(self.radar_signal_for_bins)
            
            # Update the heatmap
            self.im.set_data(radar_signal_array)
            self.im.set_clim(vmin=radar_signal_array.min(), vmax=radar_signal_array.max())
            self.im.set_extent([0, self.range_bins [-1], self.time_since_start[0], self.time_since_start[-1]])

        return self.im,

    def show(self):
        # Show the plot without blocking.
        plt.show(block=False)