from radarprocessing.FDDetectionMatrix import FDDetectionMatrix
from configuration.PlotConfig import PlotConfig
from .PlotFrequencySignalDynamic import PlotFreqSignalDynamic
from .PlotFreqWithDetectionsDynamic import PlotFreqSignalWithDetectionsDynamic
from .PlotRadarFrequencyHeatMapDynamic import PlotRadarFrequencyHeatMapDynamic

import matplotlib.pyplot as plt

class PlottingLiveData():
    def __init__(self, config: PlotConfig):
        self.config = config
        self.update_counter = 0
        self.bin_index_to_plot = config.bin_index_to_plot
        self.max_distance_plotted = config.max_distance_plotted
        self.plot_raw_fd = None
        self.plot_raw_fd_with_threshold = None
        self.plot_raw_fd_heatmap = None
        self.plot_fd_detections_heatmap = None
        
        if self.config.should_plot_raw_fd_signal:
            self.plot_raw_fd = PlotFreqSignalDynamic(self.bin_index_to_plot, self.config.raw_fd_signal_to_plot, smoothing_window=self.config.plot_raw_fd_smooth_signal)
        
        if config.should_plot_raw_fd_with_threshold_signal:
            self.plot_raw_fd_with_threshold = PlotFreqSignalWithDetectionsDynamic(self.bin_index_to_plot, config.raw_fd_signal_to_plot)  # Create a plotter instance
        
        if config.should_plot_raw_fd_heatmap:
            self.plot_raw_fd_heatmap  = PlotRadarFrequencyHeatMapDynamic(title="Raw FD Data Heatmap", max_distance=self.max_distance_plotted)
            self.plot_raw_fd_heatmap.show()
            
        if config.should_plot_fd_detections:
            self.plot_fd_detections_heatmap  = PlotRadarFrequencyHeatMapDynamic(title="FD Calculated Detections Heatmap", max_distance=self.max_distance_plotted)
            self.plot_fd_detections_heatmap.show()
        
    def plot_all_configured_live_data(self, latest_raw_data, latest_detection_date, radar_window):
        if self.config.should_plot_raw_fd_signal:
            signals, plot_timedelta, _, _= radar_window.get_signal_for_bin(self.bin_index_to_plot, self.config.raw_fd_signal_to_plot)
            self.plot_raw_fd.update_plot(signals, plot_timedelta)
            
        if self.config.should_plot_raw_fd_with_threshold_signal:
            signals, plot_timedelta, detections, thresholds = radar_window.get_signal_for_bin(self.bin_index_to_plot, self.config.raw_fd_signal_to_plot)
            self.plot_raw_fd_with_threshold.update_plot(signals, plot_timedelta, detections, thresholds)
        
        # Update the frequency heatmap less frequently
        if self.update_counter % 1 == 0:
            signal = latest_raw_data
            signal_to_plot = signal[:, self.config.raw_fd_signal_to_plot.value]
            new_time = (radar_window.timestamps[-1] - radar_window.creation_time).total_seconds()
            
            if self.config.should_plot_raw_fd_heatmap:
                self.plot_raw_fd_heatmap.update_data(new_time, signal_to_plot)
                plt.pause(0.1)  # Allow time for GUI to update
            
            if self.config.should_plot_fd_detections:
                detections = latest_detection_date[:, self.config.raw_fd_signal_to_plot.value*2]
                self.plot_fd_detections_heatmap.update_data(new_time, detections)
                plt.pause(0.1)
        
        self.update_counter += 1                
