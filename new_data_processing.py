
import pandas as pd
from older_experiments_to_delete.get_all_sensor_data import get_fd_data_from_radar
from plots.PlotPolarDynamic import PlotPolarDynamic
from plots.PlottingLiveData import PlottingLiveData

from configuration import RunParams
from config import RunParams, get_run_params, get_plot_config
from config import get_radar_module

import numpy as np

import matplotlib.pyplot as plt

from plots.PlotDetectionsDynamic import PlotDetectionsDynamic
from cfar import get_range_bin_for_indexs
from radarprocessing.FDDataMatrix import FDSignalType
from radarprocessing.RadarDataWindow import RadarDataWindow
from configuration.RunType import RunType

plotts = PlotDetectionsDynamic(bin_size=0.27, plot_titles=["Rx1 Detections", "Rx2 Detections"], max_steps=50, interval=50, max_bins=20)
polarPlot = PlotPolarDynamic(max_distance=5,interval=50)

def object_tracking(latest_detection_data, raw_records):
    
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

def data_processing(run_params: RunParams, radar_window : RadarDataWindow, plotting_live: PlottingLiveData):
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
        if(len(radar_window.get_raw_records()) < run_params.data_window_size):
            continue
        
        # DO SOME OBJECT Tracking - based off the most recent detection
        detect_data = radar_window.detection_records[-1]
        raw_records = radar_window.raw_records[-1]
        
        object_tracking(detect_data, raw_records)
        plotting_live.plot_all_configured_live_data(raw_records, detect_data, radar_window)
        

if __name__ == "__main__":
    run_params = get_run_params()
    plotting_live = PlottingLiveData(config = get_plot_config())
    radar_data_window = RadarDataWindow(cfar_params=run_params.cfar_params, 
                                        start_time=pd.Timestamp.now())
    
    data_processing(run_params, radar_data_window, plotting_live=plotting_live)
    print("test")