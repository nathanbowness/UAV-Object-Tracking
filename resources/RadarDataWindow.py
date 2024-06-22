from collections import deque
from resources.FDDataMatrix import FDDataMatrix, FDSignalType
from RadarDevKit.RadarModule import RadarModule, GetRadarModule
from get_all_sensor_data import get_fd_data_from_radar
from config import RunParams
import matplotlib.pyplot as plt

import pandas as pd
from datetime import timedelta

class RadarDataWindow():

    def __init__(self, capacity, duration_seconds=None):
        self.data = deque()
        self.creation_time = pd.Timestamp.now() 
        self.duration = timedelta(seconds=duration_seconds) if duration_seconds else None
        self.capacity = capacity

    def add_record(self, record : FDDataMatrix):
        """
        Add a record to the deque.
        Ensure the deque doesn't exceed the capacity set
        """
        current_time = pd.Timestamp.now()
        
        # Remove records based on time window if duration is specified
        if self.duration:
            while self.data and (current_time - self.data[0][0].timestamp > self.duration):
                self.data.popleft()
        # Remove records based on capacity if capacity is specified
        elif self.capacity and len(self.data) == self.capacity:
            self.data.popleft()
        
        # Add to the deque a tuple of "FDDataMatrix, RelativeTime in Seconds"
        relative_time_since_start = current_time - self.creation_time
        self.data.append((record, relative_time_since_start.total_seconds()))
        
    def update_window_data(self, run_params: RunParams, 
                           radar_module: RadarModule):
        """
        Grab new FD data from the radar, add it to the deque
        """
        self.add_record(get_fd_data_from_radar(run_params, radar_module))
        
    def get_records(self):
        return self.data
    
    def get_signal_for_bin(self, bin_index, signalType: FDSignalType):
        """
        Get the I1 signals for a particular bin index.
        return: i1_values, 
        """
        # Initialize lists to store timestamps and I1 values
        time_since_start = []
        values = []

        # Single loop to collect both timestamps and I1 values
        for (record, time_delta) in self.data:
            time_since_start.append(time_delta)
            values.append(record.fd_data[bin_index, signalType.value])  # Adjusted for correct access to desired column

        return values, time_since_start
