from radarprocessing.FDDataMatrix import FDSignalType

class PlotConfig():
    def __init__(self):
        self.plot_raw_fd_smooth_signal = 0
        self.raw_fd_signal_to_plot = FDSignalType.I1
        self.plot_raw_fd_with_threshold_signal = False
        self.plot_raw_fd_heatmap = True
        self.plot_fd_detections = False