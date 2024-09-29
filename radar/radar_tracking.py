import os
import pandas as pd
import numpy as np

import multiprocessing as mp

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
                 radar_data_queue: mp.Queue = None, 
                 plot_data_queue: mp.Queue = None):
        
        self.config = radar_configuration
        self.radar_data_queue = radar_data_queue
        self.plot_data_queue = plot_data_queue
        self.start_time = start_time
        # output directory will be the given folder, with a timestamp and 'radar' appended to it
        self.output_dir = os.path.join(self.config.output_path, self.start_time.strftime('%Y-%m-%d_%H-%M-%S'), 'radar')
        
        self.radar_module = self.config.connect_get_radar_module()
        self.bin_size_meters = self.radar_module.sysParams.tic / 1000000
        
        self.radar_window = RadarDataWindow(cfar_params=self.config.cfar_params, 
                                            start_time=self.start_time,
                                            capacity=self.config.processing_window,
                                            run_velocity_measurements=False)

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
            print(f"Running radar tracking on live data. Recording raw results to folder: {self.config.output_path}")
            os.makedirs(self.output_dir, exist_ok=True)
            self.export_radar_config_to_file(self.output_dir)
        else:
            print("Running radar tracking on live data. Not recording results.")
            
        # TODO - Print a single file will all the run configuration settings.
        
        
        while not stop_event.is_set():
            voltage_data = get_td_data_voltage(self.radar_module)
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
        txt_files = [f for f in files if f.startswith(('trial', 'TD')) and f.endswith('.txt')]
        txt_files.sort()
        
        # Process each file one by one
        for file_name in txt_files:
            file_path = os.path.join(directory_to_process, file_name)
            new_td_data = read_columns(file_path)
            self.process_time_domain_data(new_td_data)
            
        print("Completed all processing of radar data from the folder.")
            
    def process_time_domain_data(self, td_data):
        
        # TODO - convert the TDData to FDDataMatrix, for processing.. Need FD for this (or do it in the RadarWindow itself)
        # self.radar_window.add_raw_record(td_data)
        # self.radar_window.calculate_detections(record_timestamp=td_data.timestamp)
            
        # Until we have enough records for CFAR or analysis, just continue 
        if(len(self.radar_window.get_raw_records()) < self.radar_window.required_cells_cfar):
            return
        
        # Handle the object tracking, and send the data to the radar queue
        # self.handle_object_tracking()
    
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
            f"Number of Samples:\t512\n"
            f"Bin Size [Hz]:\t{sysParmas.freq_bin}\n"
            f"Zero Pad Factor:\t{sysParmas.zero_pad}\n"
            f"Normalization:\t{sysParmas.norm}\n"
            f"Active Channels:\tI1, Q1, I2, Q2\n"
        )
        
        # Write the report to the specified output file
        file_to_write = os.path.join(output_dir, output_file)
        with open(file_to_write, 'w') as file:
            file.write(report_content)
    

    def add_plot_data_to_queue(self, timestamp, detectionsRx1, detectionsRx2, raw_records):
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
        
        self.add_plot_data_to_queue(timestamp, detectionsRx1, detectionsRx2, raw_records)
        
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
    