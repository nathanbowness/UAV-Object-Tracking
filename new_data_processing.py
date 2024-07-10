
import pandas as pd
from get_all_sensor_data import get_fd_data_from_radar
from plots.FreqPlotWithDetections import FreqSignalPlotWithDetections
from plots.FrequencySignalPlot import FreqSignalPlot

from config import RunParams, get_run_params, get_plot_config
from config import get_radar_module
import matplotlib.pyplot as plt
import numpy as np

from plots.PlotDetectionsDynamic import PlotDetectionsDynamic
from plots.PolarPlotDynamic import PolarPlotDynamic
from plots.RadarFrequencyHeatMap import RadarFrequencyHeatMap
from range_bin_calculator import get_range_bin_for_indexs
from resources.FDDataMatrix import FDSignalType
from resources.RadarDataWindow import RadarDataWindow
from resources.RunType import RunType

plotts = PlotDetectionsDynamic(bin_size=0.27, plot_titles=["Rx1 Detections", "Rx2 Detections"], max_steps=50, interval=50, max_bins=20)
polarPlot = PolarPlotDynamic(max_distance=5,interval=50)

def object_tracking(latest_detection_data, raw_records, update_counter):
    
    detectionsRx1 = np.logical_or(latest_detection_data[:,FDSignalType.I1.value*2], latest_detection_data[:,FDSignalType.Q1.value*2]).astype(int)
    detectionsRx2 = np.logical_or(latest_detection_data[:,FDSignalType.I2.value*2], latest_detection_data[:,FDSignalType.Q2.value*2]).astype(int)
    
    # Mask any detections that have an angle of -90 or 90 -- not valid objects, or out of frame.
    angles = raw_records[:,FDSignalType.VIEW_ANGLE.value]
    angles_mask = np.where((angles == 90) | (angles == -90))
    detectionsRx1[angles_mask] = 0
    detectionsRx2[angles_mask] = 0
    
    # Get the total detections now after the masking, and their indexes
    detectionsTotal = np.logical_or(detectionsRx1, detectionsRx2).astype(int)
    detectionIndexes = np.where(detectionsTotal == 1)[0]
    
    # Get the actual detections to plot
    detectionsDistanceArray = get_range_bin_for_indexs(detectionIndexes, 0.27)
    detectionsAngle = raw_records[:,FDSignalType.VIEW_ANGLE.value][detectionIndexes]
    
    plotts.update_data([detectionsRx1, detectionsRx2])
    polarPlot.update_data(detectionsDistanceArray, detectionsAngle, clear=True)
    
    plt.pause(0.1)  # Allow time for GUI to update

def data_processing(run_params: RunParams, radar_window : RadarDataWindow):
    plot_config = get_plot_config()
    radar_module = get_radar_module()
    bin_index = 1
    max_distance_plotted = 120
    
    if plot_config.plot_raw_fd_signal:
        plotter = FreqSignalPlot(bin_index, plot_config.raw_fd_signal_to_plot, smoothing_window=plot_config.plot_raw_fd_smooth_signal)  # Create a plotter instance
        
    if plot_config.plot_raw_fd_with_threshold_signal:
        plotter_2 = FreqSignalPlotWithDetections(bin_index, plot_config.raw_fd_signal_to_plot)  # Create a plotter instance
    
    # if plot_config.plot_raw_fd_heatmap:
    # plotter_3 = RadarFrequencyHeatMap(title="Raw FD Data Heatmap",max_distance=max_distance_plotted)
    # plotter_3.show()
        
    if plot_config.plot_fd_detections:
        plotter_4 = RadarFrequencyHeatMap(title="FD Calculated Detections Heatmap", max_distance=max_distance_plotted)
        plotter_4.show()
    
    update_counter = 0
    
    # Infinite loop
    while True:
        # If this is a re-run, use existing data to similar a "LIVE"
        if(run_params.runType == RunType.RERUN):
          exit("Re-runs not implemented yet - but coming soon.")
        
        # Grab new data, add it to the window of saved data
        new_fd_data = get_fd_data_from_radar(run_params, radar_module)
        radar_window.add_raw_record(new_fd_data)
        radar_window.calculate_detections(record_timestamp=new_fd_data.timestamp)
        
        # Until we have enough records for CFAR or analysis, just continue 
        if(len(radar_window.get_raw_records()) < run_params.data_window_size):
            continue
        
        # DO SOME OBJECT Tracking - based off the most recent detection
        detect_data = radar_window.detection_records[-1]
        raw_records = radar_window.raw_records[-1]
        object_tracking(detect_data, raw_records, update_counter)
        
        if plot_config.plot_raw_fd_signal:
            signals, plot_timedelta, _, _= radar_window.get_signal_for_bin(bin_index, plot_config.raw_fd_signal_to_plot)
            plotter.update_plot(signals, plot_timedelta)
            
        if plot_config.plot_raw_fd_with_threshold_signal:
            signals, plot_timedelta, detections, thresholds = radar_window.get_signal_for_bin(bin_index, plot_config.raw_fd_signal_to_plot)
            plotter_2.update_plot(signals, plot_timedelta, detections, thresholds)
        
        # Update the frequency heatmap less frequently
        # if update_counter % 10 == 0:
        #     signal = raw_records
        #     signal_to_plot = signal[:, plot_config.raw_fd_signal_to_plot.value]
        #     new_time = (radar_window.timestamps[-1] - radar_window.creation_time).total_seconds()
        #     plotter_3.update_data(new_time, signal_to_plot)
        #     plt.pause(0.02)  # Allow time for GUI to update
            
        #     # Every 10 times, check if there are any records to remove
        #     radar_window.remove_old_records()
            
        #     signals, plot_times, detections = radar_window.get_signal_for_bins(plot_config.raw_fd_signal_to_plot)
        #     if plot_config.plot_raw_fd_heatmap:
        #         plotter_3.update_data(plot_times, signals)
            
        #     if plot_config.plot_fd_detections:
        #         plotter_4.update_data(plot_times, detections)
        
        update_counter += 1

if __name__ == "__main__":
    run_params = get_run_params()
    radar_data_window = RadarDataWindow(cfar_params=run_params.cfar_params, 
                                        start_time=pd.Timestamp.now())
    
    data_processing(run_params, radar_data_window)
    print("test")