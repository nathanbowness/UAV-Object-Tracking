import os
import sys
from typing import List
import pandas as pd
import numpy as np
from datetime import datetime

import multiprocessing as mp
import time

from constants import RADAR_DETECTION_TYPE
from tracking.DetectionsAtTime import DetectionDetails, DetectionsAtTime
from radar.cfar import get_range_bin_for_indexs
from radar.configuration.RunType import RunType

from radar.configuration.RadarConfiguration import RadarConfiguration

from radar.radarprocessing.FDDataMatrix import FDSignalType
from radar.radarprocessing.RadarDataWindow import RadarDataWindow
from radar.dataparsing.td_textdata_parser import read_columns

from radar.radarprocessing.get_td_sensor_data import get_td_data_voltage

class RadarTracking():
    def __init__(self, 
                 radar_configuration: RadarConfiguration,
                 start_time: pd.Timestamp = pd.Timestamp.now(),
                 radar_data_queue: mp.Queue = None):
        
        self.config = radar_configuration
        self.radar_data_queue = radar_data_queue
        self.start_time = start_time
        # output directory will be the given folder, with a timestamp and 'radar' appended to it
        self.output_dir = os.path.join(self.config.output_path, self.start_time.strftime('%Y-%m-%d_%H-%M-%S'), 'radar')
        
        if self.config.run_type == RunType.LIVE:
            self.radar_module = self.config.connect_get_radar_module()
            if (not self.radar_module.connected):
                print("Radar module is NOT connected. Exiting.")
                sys.exit("Could not connect to radar module. Please check the connection, or disable the radar with the '--skip-radar' flag.")
            self.bin_size_meters = self.radar_module.sysParams.tic / 1000000
        
        self.radar_window = RadarDataWindow(cfar_params=self.config.cfar_params, 
                                            start_time=self.start_time,
                                            bin_size=self.config.bin_size_meters,
                                            f_c=self.config.f_c,
                                            capacity=self.config.processing_window,
                                            run_velocity_measurements=False)
        self.count_between_processing = 5

    def object_tracking(self, stop_event):
        # If this is a rerun, read the data from the folder until it's completed
        if self.config.run_type == RunType.RERUN:
            self.process_data_from_folder()

        # If this is a live run, keep reading the data from the radar until the stop event is set
        elif self.config.run_type == RunType.LIVE:
            self.process_live_data(stop_event)
        
    def process_live_data(self, stop_event):
        """
        Process the radar data from the radar module until the stop event is set.
        """
        if self.config.record_data:
            print(f"Running radar tracking on live data. Recording raw results to folder: {self.output_dir}")
            os.makedirs(self.output_dir, exist_ok=True)
            self.export_radar_config_to_file(self.output_dir)
        else:
            print("Running radar tracking on live data. Not recording results.")
            
        while not stop_event.is_set():
            voltage_data = get_td_data_voltage(self.radar_module)
            if voltage_data is None:
                # There was likely an error - reset error code, try again
                self.radar_module.error = False
                continue
                 
            if self.config.record_data:
                voltage_data.print_data_to_file(self.output_dir)
            
            self.process_time_domain_data(voltage_data)
            
    def process_data_from_folder(self):
        """
        Process the radar data from the folder specified in the configuration.
        """
        directory_to_process = self.config.source_path
        print(f"Processing prerecorded radar data from folder {directory_to_process}.")
        
        # List all files in the directory
        files = os.listdir(directory_to_process)
        
        # Filter the files based on the naming convention, and sort them
        txt_files = [f for f in files if f.endswith('.txt')]
        txt_files.sort()
        
        # Process each file one by one
        for file_name in txt_files:
            file_path = os.path.join(directory_to_process, file_name)
            new_td_data = read_columns(file_path)
            
            # Simulate the timestamp as the current time to we can use the real-time windowing.
            # Add a 0.08 second delay between processing since we expect it to take roughly that long to get the radar data
            new_td_data.timestamp = pd.Timestamp.now()
            self.process_time_domain_data(new_td_data)
            time.sleep(0.08)
            
        print("Completed all processing of radar data from the folder.")
            
    def process_time_domain_data(self, td_data):
        # Add the raw TD record to the radar window
        self.radar_window.add_raw_record(td_data)
        # Call method to process the latest data
        self.radar_window.process_data()
        
        # detections = self.radar_window.get_most_recent_detections_split_xy()
        detections = self.radar_window.get_most_recent_detections_combined_xy()
        self.send_object_tracks_to_queue(detectionsAtTime=detections) # Send the object tracks to the queue
    
    def export_radar_config_to_file(self, output_dir, output_file="RadarConfigurationReport.txt"):
        """
        Exports the radar configuration settings to a text file in a formatted structure.

        Args:
            output_file (str): The name of the file to write the radar configuration report.
        """
        current_date = self.start_time.strftime("%Y-%m-%d")
        start_time = self.start_time.now().strftime("%H:%M:%S.%f")[:-3]
        sysParmas = self.radar_module.sysParams
         # Format the bin size to three decimal points
        formatted_bin_size_mm = f"{(self.bin_size_meters*1000):.3f}"

        report_content = (
            f"Date:\t{current_date}\n"
            f"Start Time:\t{start_time}\n"
            f"Interface:\tEthernet\n"
            f"Start-Frequency [MHz]:\t{self.config.minimum_frequency_mhz}\n"
            f"Stop-Frequency [MHz]:\t{self.config.maximum_frequency_mhz}\n"
            f"Ramp Time [ms]:\t{self.config.ramp_time_fmcw_chirp}\n"
            f"Attenuation [dB]:\t{sysParmas.atten}\n"
            f"Bin Size [mm]:\t{formatted_bin_size_mm}\n"
            f"Number of Samples:\t1024\n"
            f"Bin Size [Hz]:\t{sysParmas.freq_bin}\n"
            f"Zero Pad Factor:\t{sysParmas.zero_pad}\n"
            f"Normalization:\t{sysParmas.norm}\n"
            f"Active Channels:\tI1, Q1, I2, Q2\n"
        )
        
        # Write the report to the specified output file
        file_to_write = os.path.join(output_dir, output_file)
        with open(file_to_write, 'w') as file:
            file.write(report_content)
            
    def send_object_tracks_to_queue(self, detectionsAtTime: DetectionsAtTime):
        """
        Push the detections to the Queue
        """
        if self.radar_data_queue is not None:
            self.radar_data_queue.put(detectionsAtTime)
    