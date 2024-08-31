import os
import random
import time
import pandas as pd

import multiprocessing as mp

from radar_object_tracking.configuration.RunType import RunType
from radar_object_tracking.configuration.RadarRunParams import RadarRunParams
from radar_object_tracking.radarprocessing.RadarDataWindow import RadarDataWindow
from radar_object_tracking.radarprocessing.radar_fd_textdata_parser import read_columns

class RadarTracking():
    def __init__(self, radar_run_params: RadarRunParams, radar_data_queue: mp.Queue = None):
        self.radar_run_params = radar_run_params
        self.radar_data_queue = radar_data_queue
        
        tracking_start_time = pd.Timestamp.now().replace(microsecond=0)
        radar_data_window = RadarDataWindow(cfar_params=self.radar_run_params.cfar_params, 
                                            start_time=tracking_start_time,
                                            capacity=self.radar_run_params.data_window_size)

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
        
        self.radar_data_queue.put("I finished processing.")  # Put the result into the queue
        
    def process_data_from_folder(self):
        directory_to_process = self.radar_run_params.recordedDataFolder
        
        # List all files in the directory
        files = os.listdir(directory_to_process)
        
        # Filter the files based on the naming convention
        txt_files = [f for f in files if f.startswith('trial_') and f.endswith('.txt')]
        
        # Sort the files if needed (optional)
        txt_files.sort()
        
        # Process each file one by one
        for file_name in txt_files:
            file_path = os.path.join(directory_to_process, file_name)
            data = read_columns(file_path)
            time.sleep(self.radar_run_params.recordedProcessingDelaySec)
            print(f"Processing file: {file_path}")
    