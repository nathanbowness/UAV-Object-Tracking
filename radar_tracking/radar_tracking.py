import os
import time
import pandas as pd
import numpy as np

import multiprocessing as mp

from radar_tracking.cfar import get_range_bin_for_indexs
from radar_tracking.configuration.RunType import RunType
from radar_tracking.configuration.RadarRunParams import RadarRunParams
from radar_tracking.radarprocessing.FDDataMatrix import FDSignalType
from radar_tracking.radarprocessing.RadarDataWindow import RadarDataWindow
from radar_tracking.radarprocessing.radar_fd_textdata_parser import read_columns

class RadarTracking():
    def __init__(self, radar_run_params: RadarRunParams, radar_data_queue: mp.Queue = None, plot_data_queue: mp.Queue = None):
        self.radar_run_params = radar_run_params
        self.radar_data_queue = radar_data_queue
        self.plot_data_queue = plot_data_queue
        
        self.tracking_start_time = pd.Timestamp.now().replace(microsecond=0)
        self.radar_window = RadarDataWindow(cfar_params=self.radar_run_params.cfar_params, 
                                            start_time=self.tracking_start_time,
                                            capacity=self.radar_run_params.data_window_size,
                                            run_velocity_measurements=self.radar_run_params.run_velocity_measurements)

    def object_tracking(self, stop_event):
        
        # If this is a rerun, read the data from the folder until it's completed
        if self.radar_run_params.runType == RunType.RERUN:
            # Read the data from the file
            print(f"Run radar tracking on data in folder: {self.radar_run_params.recordedDataFolder}")
            self.process_data_from_folder()

        # If this is a live run, keep reading the data from the radar until the stop event is set
        
        elif self.radar_run_params.runType == RunType.LIVE:
            while not stop_event.is_set():
                print("LIVE - radar tracking")
        
        self.radar_data_queue.put("DONE")  # Put the result into the queue

    def handle_object_tracking(self):
        latest_detection_data = self.radar_window.detection_records[-1] # (512, 8)
        raw_records = self.radar_window.raw_records[-1] # (513, 8)
        timestamp = self.radar_window.timestamps[-1]
        
        # TODO -- ensure the algorithm, and masking for this is correct... Seems like something might be off
        
        detectionsRx1 = np.logical_or(latest_detection_data[:,FDSignalType.I1.value*2], latest_detection_data[:,FDSignalType.Q1.value*2]).astype(int)
        # detectionsRx1 = latest_detection_data[:,FDSignalType.I1.value*2].astype(int)
        detectionsRx2 = np.logical_or(latest_detection_data[:,FDSignalType.I2.value*2], latest_detection_data[:,FDSignalType.Q2.value*2]).astype(int)

        # Mask any detections that have an angle of -90 or 90 -- not valid objects, or out of frame.
        angles = raw_records[1:,FDSignalType.VIEW_ANGLE.value] # Skip the first record, since it's length 513
        angles_mask = np.where((angles == 90) | (angles == -90))
        detectionsRx1[angles_mask] = 0
        detectionsRx2[angles_mask] = 0
        
        # Get the total detections now after the masking, and their indexes
        detectionsTotal = np.logical_or(detectionsRx1, detectionsRx2).astype(int)
        detectionIndexes = np.where(detectionsTotal == 1)[0]
        
        # Get the actual detections to plot
        detectionsDistanceArray = get_range_bin_for_indexs(detectionIndexes, 0.199861)
        detectionsAngleDeg = raw_records[:,FDSignalType.VIEW_ANGLE.value][detectionIndexes]
        
        # If the plot_data_queue is not None, then send the data to the queue
        if self.plot_data_queue is not None:
            plot_data = {'type': 'detections', 'time': timestamp, 'data': {'Rx1': detectionsRx1, 'Rx2': detectionsRx2}}
            self.plot_data_queue.put(plot_data)
            
            new_time = (self.radar_window.timestamps[-1] - self.radar_window.creation_time).total_seconds()
            plot_data = {'type': 'magnitude', 'relativeTimeSec': new_time, 'data': raw_records[1:,FDSignalType.I1.value]}
            self.plot_data_queue.put(plot_data)
            
            if self.radar_run_params.run_velocity_measurements:
                plot_data_micro = {'type': 'microFreq', 'relativeTimeSec': new_time, 'data': self.radar_window.velocity_records[-1][:,0]}
                self.plot_data_queue.put(plot_data_micro)
                
                plot_data_velo = {'type': 'velocity', 'relativeTimeSec': new_time, 'data': self.radar_window.velocity_records[-1][:,1]}
                self.plot_data_queue.put(plot_data_velo)
            
        
        if len(detectionsAngleDeg) > 0 and (len(detectionsDistanceArray) == len(detectionsAngleDeg)):
            # Convert angles from degrees to radians
            detectionsAngleRad = np.radians(detectionsAngleDeg)

            # Calculate x and y coordinates
            x_coords = detectionsDistanceArray * np.cos(detectionsAngleRad)
            y_coords = detectionsDistanceArray * np.sin(detectionsAngleRad)
            array_data = [{'x': x, 'y': y, 'x_v': '1', 'y_v':'1'} for x, y in zip(x_coords, y_coords)]
            detections = {'time': timestamp, 'type': 'radar', 'data': array_data}
            
            # Send data to the radar_queue --- {'x', 'y', 'type', 'time'}
            self.radar_data_queue.put(detections)
        
    def process_data_from_folder(self):
        directory_to_process = self.radar_run_params.recordedDataFolder
        
        # List all files in the directory
        files = os.listdir(directory_to_process)
        
        # Filter the files based on the naming convention
        txt_files = [f for f in files if f.startswith('trial') and f.endswith('.txt')]
        
        # Sort the files if needed (optional)
        txt_files.sort()
        
        # Process each file one by one
        for file_name in txt_files:
            file_path = os.path.join(directory_to_process, file_name)
            
            # print(f"Processing file: {file_path}")
            new_fd_data = read_columns(file_path)
            
            self.radar_window.add_raw_record(new_fd_data)
            self.radar_window.calculate_detections(record_timestamp=new_fd_data.timestamp)
            
            # Until we have enough records for CFAR or analysis, just continue 
            if(len(self.radar_window.get_raw_records()) < self.radar_window.required_cells_cfar):
                continue
            
            self.handle_object_tracking()
            
            time.sleep(self.radar_run_params.recordedProcessingDelaySec)
        
        print("Completed all processing of radar data from the folder.")
            
    