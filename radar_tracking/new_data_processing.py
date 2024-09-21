
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from plots.PlotDetectionsDynamic import PlotDetectionsDynamic
from plots.PlotPolarDynamic import PlotPolarDynamic
from plots.PlottingLiveData import PlottingLiveData

from radar_tracking.configuration import RadarRunParams
from config import RadarRunParams, get_run_params, get_plot_config, get_radar_module

from radar_tracking.cfar import get_range_bin_for_indexs
from radarprocessing.FDDataMatrix import FDSignalType
from radarprocessing.RadarDataWindow import RadarDataWindow
from radarprocessing.get_all_sensor_data import get_fd_data_from_radar
from configuration.RunType import RunType
from tracking.ObjectTracking import ObjectTrackingExtendedObjectGNN

plotts = PlotDetectionsDynamic(bin_size=0.27, plot_titles=["Rx1 Detections", "Rx2 Detections"], max_steps=50, interval=50, max_bins=20)
polarPlot = PlotPolarDynamic(max_distance=5,interval=50)

def handle_object_tracking(object_tracking, latest_detection_data, raw_records, timestamp):
    
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
    
    # Convert the angles to radians, so we can then get the x, y coordinates
    angles_in_radians = np.radians(detectionsAngle)
    x_coord_detections = detectionsDistanceArray * np.cos(angles_in_radians)
    y_coord_detections = detectionsDistanceArray * np.sin(angles_in_radians)
    x_vel = np.full(x_coord_detections.shape, 1)
    y_vel = np.full(y_coord_detections.shape, 1)
    
    detection_array = np.column_stack((x_coord_detections, x_vel, y_coord_detections, y_vel))
    object_tracking.update_tracks(detection_array, timestamp)
    object_tracking.show_tracks_plot()
    
    plt.pause(0.1)  # Allow time for GUI to update

def data_processing(run_params: RadarRunParams, radar_window : RadarDataWindow, object_tracking: ObjectTrackingExtendedObjectGNN, plotting_live: PlottingLiveData):
    radar_module = get_radar_module()
    
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
        if(len(radar_window.get_raw_records()) < radar_window.required_cells_cfar):
            continue
        
        # DO SOME OBJECT Tracking - based off the most recent detection
        detect_data = radar_window.detection_records[-1]
        raw_records = radar_window.raw_records[-1]
        timestamp = radar_window.timestamps[-1]
        
        handle_object_tracking(object_tracking, detect_data, raw_records, timestamp)
        plotting_live.plot_all_configured_live_data(raw_records, detect_data, radar_window)

if __name__ == "__main__":
    run_params = get_run_params()
    
    # Time when we started tracking
    tracking_start_time = pd.Timestamp.now().replace(microsecond=0)
    # Max number of records we need to keep in the window
    max_records_to_keep = run_params.data_window_size
    
    # Object to plot, track and process data
    plotting_live = PlottingLiveData(config = get_plot_config())
    object_tracking = ObjectTrackingExtendedObjectGNN(tracking_start_time, capacity=max_records_to_keep)
    
    radar_data_window = RadarDataWindow(cfar_params=run_params.cfar_params, 
                                        start_time=tracking_start_time,
                                        capacity=max_records_to_keep)
    
    data_processing(run_params, radar_data_window, object_tracking=object_tracking, plotting_live=plotting_live)
    print("test")