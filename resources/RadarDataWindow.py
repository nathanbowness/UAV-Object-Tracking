from collections import deque
from resources.FDDataMatrix import FDDataMatrix, FDSignalType
from RadarDevKit.RadarModule import RadarModule, GetRadarModule
from get_all_sensor_data import get_fd_data_from_radar
from config import RunParams
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
from datetime import timedelta

from resources.FDDetectionMatrix import FDDetectionMatrix # type: ignore

class StoredData():
    def __init__(self, raw_data: FDDataMatrix, relativeTime: int, detection_data: FDDetectionMatrix):
        self.raw_data = raw_data
        self.relativeTime = relativeTime
        self.detection_data = detection_data

class RadarDataWindow():

    def __init__(self, num_train, num_guard, duration_seconds=None):
        self.deque = deque()
        self.creation_time = pd.Timestamp.now() 
        self.duration = timedelta(seconds=duration_seconds) if duration_seconds else None
        self.capacity = (2*num_guard) + (2*num_train) + 1
        
        self.last_cfar_index = -1  # Tracks where the last CFAR calculation ended
        self.num_train = num_train
        self.num_guard = num_guard

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
        if len(self.deque) < self.capacity:
            # Not enough data to run CFAR
            return FDDetectionMatrix(np.zeros((512, 8)), timeStamp)

        num_bins = 512  # Assuming 512 range bins
        signals = [FDSignalType.I1, FDSignalType.Q1, FDSignalType.I2, FDSignalType.Q2]
        detection_matrix = np.zeros((num_bins, 8))
        
        relevate_deque_data = list(self.deque)[-self.capacity:]
        
        index_to_eval = self.num_train + self.num_guard  # Index of the CUT in the deque after sufficient data is gathered

        for i in range(num_bins):  # Each range bin
            for idx, signal in enumerate(signals):
                data = np.array([item.raw_data.fd_data[i][signal.value] for item in relevate_deque_data])
                detection_matrix[i, idx*2], detection_matrix[i, idx*2+1] = self.caso_cfar_single(data, self.num_train, self.num_guard, index_to_eval)

        return FDDetectionMatrix(detection_matrix, timeStamp)
    
    def caso_cfar_single(self, data, num_train, num_guard, index_CUT):
        n = len(data)
    
        # Ensure the index has enough data around it to calculate
        if index_CUT < num_train + num_guard or index_CUT >= n - num_train - num_guard:
            return 0, 0  # Not enough data to perform CFAR at this index

        # Extract training cells around the CUT, excluding guard cells
        leading_train_cells = data[index_CUT - num_train - num_guard:index_CUT - num_guard]
        trailing_train_cells = data[index_CUT + num_guard + 1:index_CUT + num_guard + num_train + 1]

        # Calculate the average noise levels for leading and trailing training cells
        noise_level_leading = np.mean(leading_train_cells)
        noise_level_trailing = np.mean(trailing_train_cells)

        # Use the smaller of the two noise levels
        noise_level = min(noise_level_leading, noise_level_trailing)

        # Define the threshold
        threshold_factor = 1.4  # Adjustable based on required false alarm rates
        threshold = noise_level * threshold_factor

        # Determine if the CUT exceeds the threshold
        signal_level = data[index_CUT]
        detection = 1 if signal_level > threshold else 0

        return detection, threshold

    def caso_cfar_single_old(self, data, num_train, num_guard, index_CUT):
        # Check the CFAR condition for a single data point at 'index'
        if len(data) >= 2 * (num_train + num_guard) + 1:
            # Extract training data excluding guard cells and CUT
            train_data = np.concatenate([
                data[index_CUT - num_train - num_guard : index_CUT - num_guard],
                data[index_CUT + num_guard + 1 : index_CUT + num_guard + num_train + 1]
            ])
            noise_level = np.mean(train_data)
            threshold = noise_level * 1.2  # Adjust factor based on desired false alarm rate
            
            signal_level = data[index_CUT]
            detection_status = 1 if signal_level > threshold else 0
            return detection_status, threshold
        else:
            return 0, 0  # Return zero detection and threshold if insufficient data
    
    def get_signal_for_bin(self, bin_index, signalType: FDSignalType):
        """
        Get the I1 signals for a particular bin index.
        return: i1_values, 
        """
        # Initialize lists to store timestamps and I1 values
        time_since_start = []
        raw_values = []
        detections = []
        thresholds = []

        # Single loop to collect both timestamps and I1 values
        for stored_data in self.deque:
            time_since_start.append(stored_data.relativeTime)
            raw_values.append(stored_data.raw_data.fd_data[bin_index, signalType.value])  # Adjusted for correct access to desired column
            detections.append(stored_data.detection_data.dectections[bin_index, signalType.value*2])
            thresholds.append(stored_data.detection_data.dectections[bin_index, signalType.value*2+1])

        return raw_values, time_since_start, detections, thresholds
