from collections import deque
from cfar import CfarType, cfar_single, cfar_required_cells
from range_bin_calculator import get_range_bins
from resources.FDDataMatrix import FDDataMatrix, FDSignalType
from config import RunParams, CFARParams

import numpy as np
import pandas as pd
from datetime import timedelta

from resources.FDDetectionMatrix import FDDetectionMatrix # type: ignore

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class StoredData():
    def __init__(self, raw_data: FDDataMatrix, relativeTime: int, detection_data: FDDetectionMatrix):
        self.raw_data = raw_data
        self.relativeTime = relativeTime
        self.detection_data = detection_data

class RadarDataWindow():
    def __init__(self, cfar_params=CFARParams, duration_seconds=None):
        self.deque = deque()
        self.creation_time = pd.Timestamp.now()
        self.duration = timedelta(seconds=duration_seconds) if duration_seconds else None
        
        # Cfar params
        self.cfar_params = cfar_params
        self.index_to_eval = cfar_params.num_train + cfar_params.num_guard
        self.required_cells_cfar = cfar_required_cells(cfar_params)

    def add_record(self, record : FDDataMatrix):
        """
        Add a record to the deque.
        Ensure the deque doesn't exceed the capacity set
        """
        current_time = pd.Timestamp.now()
        
        # Remove records based on time window if duration is specified
        if self.duration:
            while self.deque and (current_time - self.deque[0].raw_data.timestamp > self.duration):
                self.deque.popleft()
        # Remove records based on capacity if capacity is specified
        elif self.capacity and len(self.deque) == self.capacity:
            self.deque.popleft()
        
        # Add to the deque a tuple of "FDDataMatrix, RelativeTime in Seconds"
        relative_time_since_start = current_time - self.creation_time
        detection_data = self.process_new_data(record.timestamp)
        self.deque.append(StoredData(record, relative_time_since_start.total_seconds(), detection_data))
        
    def get_records(self):
        return self.deque
    
    def process_new_data(self, timeStamp: pd.Timestamp) -> FDDetectionMatrix:
        if len(self.deque) < self.required_cells_cfar:
            # Not enough data to run CFAR
            return FDDetectionMatrix(np.zeros((512, 8)), timeStamp)

        num_bins = 512  # Assuming 512 range bins
        signals = [FDSignalType.I1, FDSignalType.Q1, FDSignalType.I2, FDSignalType.Q2]
        detection_matrix = np.zeros((num_bins, 8))
        
        relevate_deque_data = list(self.deque)[-self.required_cells_cfar:]

        for i in range(num_bins):  # Each range bin
            for idx, signal in enumerate(signals):
                data = np.array([item.raw_data.fd_data[i][signal.value] for item in relevate_deque_data])
                detection_matrix[i, idx*2], detection_matrix[i, idx*2+1] = cfar_single(data, 
                                                                                       index_CUT=self.index_to_eval,
                                                                                       cfar_params=self.cfar_params)

        return FDDetectionMatrix(detection_matrix, timeStamp)
    
    def get_signal_for_bin(self, bin_index, signalType: FDSignalType):
        """
        Get the signal for a particular bin index.
        return: signal values, 
        """
        # Initialize lists to store timestamps and I1 values
        time_since_start = []
        raw_values = []
        detections = []
        thresholds = []

        # Single loop to collect both time stamps, frequency values, detections and thresholds
        if signalType.value < 4:
            for stored_data in self.deque:
                time_since_start.append(stored_data.relativeTime)
                raw_values.append(stored_data.raw_data.fd_data[bin_index, signalType.value])  # Adjusted for correct access to desired column
                detections.append(stored_data.detection_data.dectections[bin_index, signalType.value*2])
                thresholds.append(stored_data.detection_data.dectections[bin_index, signalType.value*2+1])
        # For plotting the Rx Phase, and View Angles
        else:
            for stored_data in self.deque:
                time_since_start.append(stored_data.relativeTime)
                raw_values.append(stored_data.raw_data.fd_data[bin_index, signalType.value])  # Adjusted for correct access to desired column
            

        return raw_values, time_since_start, detections, thresholds
    
    def get_signal_for_bins(self, signalType: FDSignalType):
        """
        Get the signal for all range bins for the current window
        return: Signal across all range bins as a function of time
        """
        time_since_start = [] # Array length n, of each relative time entry when data was logged
        radar_signal_for_bins = [] # Array of length n, which contans array of length 512. Each value of the 512 is a dBm value. Otherwise the index represents the range the value is assocaite to
        detections_for_bins = [] # Array of length n, which contans array of length 512. Each value is a 1 or 0 for a detection
        range_bins_as_dist = get_range_bins(0.27) # The 512 range bins, ranging from approx 0.270 to 273 at 0.270 increments
        
        # I want a heatmap with the x-axis to be from 0 to the highest range_bins value
        # I watn the y-value to be from the lowest time, to the highest time
        # I want the values, to be the value of the radar signal in dBm
        # I want the radar_signal_for_bins's 512 values to essentially be plotted along the x axis according to their respective range bin
        
        # Skip non-frequency data
        if signalType.value < 4:
            for stored_data in self.deque:
                time_since_start.append(stored_data.relativeTime)
                radar_signal_for_bins.append(stored_data.raw_data.fd_data[:, signalType.value])
                detections_for_bins.append(stored_data.detection_data.dectections[:, signalType.value*2])
            
        # radar_signal_for_bins = np.array(radar_signal_for_bins)
    
        # min_bin = 0 # in meters
        # max_bin_size = 120 # in meters
        # valid_indices = get_range_bin_indexes(min_bin, max_bin_size, 0.27)
        
        # selected_bins = radar_signal_for_bins[:,valid_indices]
        
        # plt.figure(figsize=(15, 8))
        # plt.imshow(selected_bins, aspect='auto', cmap='jet', origin='lower', extent=[0, valid_indices[-1]*0.27, min(time_since_start), max(time_since_start)])
        # plt.colorbar(label='Signal Power Ratio (dBm)')
        # plt.ylabel('Measurement Time (s)')
        # plt.xlabel('Slant Range (m)')
        # plt.title('Raw Radar Data Heatmap')
        # plt.show()
        
        # For the whole thing
        #  for stored_data in self.deque:
        #     time_since_start.append(stored_data.relativeTime)
        #     radar_signal_for_bins.append(stored_data.raw_data.fd_data[:, signalType.value])
            
        # radar_signal_for_bins = np.array(radar_signal_for_bins)
        # plt.figure(figsize=(15, 8))
        # plt.imshow(radar_signal_for_bins, aspect='auto', cmap='jet', extent=[0, range_bins_as_dist[-1], min(time_since_start), max(time_since_start)])
        # plt.colorbar(label='Signal Power Ratio (dBm)')
        # plt.ylabel('Measurement Time (s)')
        # plt.xlabel('Slant Range (m)')
        # plt.title('Raw Radar Data Heatmap')
        # plt.show()
        
        return np.array(radar_signal_for_bins), np.array(time_since_start), np.array(detections_for_bins)
            
        
