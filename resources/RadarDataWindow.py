from collections import deque
from cfar import CfarType, cfar_single, cfar_required_cells
from resources.FDDataMatrix import FDDataMatrix, FDSignalType
from RadarDevKit.RadarModule import RadarModule, GetRadarModule
from get_all_sensor_data import get_fd_data_from_radar
from config import RunParams, CFARParams
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

    def __init__(self, cfar_params=CFARParams, duration_seconds=None):
        self.deque = deque()
        self.creation_time = pd.Timestamp.now() 
        self.duration = timedelta(seconds=duration_seconds) if duration_seconds else None
        
        # Cfar params
        self.cfar_params = cfar_params
        self.index_to_eval = cfar_params.num_train + cfar_params.num_guard
        self.required_cells_cfar = cfar_required_cells(cfar_params.num_train, cfar_params.num_guard, cfar_type=cfar_params.cfar_type)

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
                                                                                       self.cfar_params.num_train, 
                                                                                       self.cfar_params.num_guard, 
                                                                                       index_CUT=self.index_to_eval, 
                                                                                       threshold=self.cfar_params.threshold,
                                                                                       cfar_type=self.cfar_params.cfar_type)

        return FDDetectionMatrix(detection_matrix, timeStamp)
    
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
