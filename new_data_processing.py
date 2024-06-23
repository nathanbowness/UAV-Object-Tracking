
from get_all_sensor_data import get_fd_data_from_radar
from plots.FreqPlotWithDetections import FreqSignalPlotWithDetections
from plots.FrequencySignalPlot import FreqSignalPlot

from config import RunParams, get_run_params, get_plot_config
from config import get_radar_module
import matplotlib.pyplot as plt

from plots.RadarFrequencyHeatMap import RadarFrequencyHeatMap
from resources.RadarDataWindow import RadarDataWindow
from resources.RunType import RunType

def data_processing(run_params: RunParams, radar_window : RadarDataWindow):
    
    plot_config = get_plot_config()
    radar_module = get_radar_module()
    bin_index = 1
    
    if plot_config.plot_raw_fd_signal:
        plotter = FreqSignalPlot(bin_index, plot_config.raw_fd_signal_to_plot)  # Create a plotter instance
        
    if plot_config.plot_raw_fd_with_threshold_signal:
        plotter_2 = FreqSignalPlotWithDetections(bin_index, plot_config.raw_fd_signal_to_plot)  # Create a plotter instance
    
    if plot_config.plot_raw_fd_heatmap:
        plotter_3 = RadarFrequencyHeatMap(max_distance=5)
        plotter_3.show()
        
    if plot_config.plot_fd_detections:
        plotter_4 = RadarFrequencyHeatMap(max_distance=5)
        plotter_4.show()
    
    update_counter = 0
    
    # Infinite loop
    while True:
        # If this is a re-run, use existing data to similar a "LIVE"
        if(run_params.runType == RunType.RERUN):
          exit("Re-runs not implemented yet - but coming soon.")
        
        # Grab new data, add it to the window of saved data
        new_fd_data = get_fd_data_from_radar(run_params, radar_module)
        radar_window.add_record(new_fd_data)
        
        # Until we have enough records for CFAR or analysis, just continue 
        if(len(radar_window.get_records()) < run_params.data_window_size):
            continue
        
        if plot_config.plot_raw_fd_signal:
            signals, plot_timedelta = radar_window.get_signal_for_bin(bin_index, plot_config.raw_fd_signal_to_plot)
            plotter.update_plot(signals, plot_timedelta)
            
        if plot_config.plot_raw_fd_with_threshold_signal:
            signals, plot_timedelta, detections, thresholds = radar_window.get_signal_for_bin(bin_index, plot_config.raw_fd_signal_to_plot)
            plotter_2.update_plot(signals, plot_timedelta, detections, thresholds)
        
        # Update the frequency heatmap less frequently
        if update_counter % 10 == 0:
            
            signals, plot_times, detections = radar_window.get_signal_for_bins(plot_config.raw_fd_signal_to_plot)
            if plot_config.plot_raw_fd_heatmap:
                plotter_3.update_data(plot_times, signals)
            
            if plot_config.plot_fd_detections:
                plotter_4.update_data(plot_times, detections)
            plt.pause(0.02)  # Allow time for GUI to update
        
        update_counter += 1

if __name__ == "__main__":
    run_params = get_run_params()
    radar_data_window = RadarDataWindow(cfar_params=run_params.cfar_params,
                                        duration_seconds=30)
    
    data_processing(run_params, radar_data_window)
    print("test")