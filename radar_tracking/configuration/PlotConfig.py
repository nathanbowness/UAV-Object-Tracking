from radar_tracking.radarprocessing.FDDataMatrix import FDSignalType

class PlotConfig():
    def __init__(self):
        self.should_plot_raw_fd_signal = False
        self.plot_raw_fd_smooth_signal = 0
        self.raw_fd_signal_to_plot = FDSignalType.I1
        self.should_plot_raw_fd_with_threshold_signal = False
        self.should_plot_raw_fd_heatmap = False
        self.should_plot_fd_detections = False
        
        # Configuration for the plots
        self.bin_index_to_plot = 1
        self.max_distance_plotted = 120