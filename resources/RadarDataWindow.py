from collections import deque
from cfar import CfarType, cfar_single, cfar_required_cells
from constants import SPEED_LIGHT
from resources.FDDataMatrix import FDDataMatrix, FDSignalType
from config import RunParams, CFARParams

import numpy as np
import pandas as pd
from datetime import timedelta

from scipy.signal import stft

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
    """
    timestamps -> timestamp
    raw_records -> np array (512, 7) [range_bins, I1, Q1, I2, Q2, Rx1 Phase, Rx2 Phase, View Angle]
    detection_records -> np array (512, 8) [range_bins, I1 Det, I1_Thresh, Q1 Det, Q1_Thresh, I2 Det, I2_Thresh, Q2 Det, Q2_Thresh]
    """
    def __init__(self, cfar_params: CFARParams, start_time: pd.Timestamp, capacity: int = 1000, duration_seconds=None):
        self.creation_time = start_time
        
        self.timestamps = deque()
        self.raw_records = deque()
        self.detection_records = deque()
        self.velocity_records = deque()
        self.capacity = capacity
        self.duration = timedelta(seconds=duration_seconds) if duration_seconds else None
        
        # Cfar params
        self.cfar_params = cfar_params
        self.index_to_eval = cfar_params.num_train + cfar_params.num_guard
        self.required_cells_cfar = cfar_required_cells(cfar_params)

    def remove_old_records(self):
        current_time = pd.Timestamp.now()
        
        # Remove records based on time window if duration is specified
        if self.duration:
            while self.timestamps and (current_time - self.timestamps[0] > self.duration):
                self.timestamps.popleft()
                self.raw_records.popleft()
                self.detection_records.popleft()
        # Remove records based on capacity if capacity is specified
        elif self.capacity and len(self.raw_records) == self.capacity:
            self.timestamps.popleft()
            self.raw_records.popleft()
            self.detection_records.popleft()
    
    def add_raw_record(self, record : FDDataMatrix):
        """
        Add a record to the deque.
        Ensure the deque doesn't exceed the capacity set
        """
        self.timestamps.append(record.timestamp)
        self.raw_records.append(record.fd_data)
        
    def calculate_detections(self, record_timestamp: pd.Timestamp):
        detection_data = self.process_new_data()
        velocity = self.velocity_calcs()
        self.detection_records.append(detection_data)
        
    def get_raw_records(self):
        return self.raw_records
    
    def get_detection_records(self):
        return self.detection_records
    
    def velocity_calcs(self):
        
        if len(self.timestamps) < 2:
            return None

        f_c = (24000*(10**6)) + (600 / 2)*(10**6) # Central frequency in Hz - Conversion from Mhz to 
        last_record = self.raw_records[-1]
        second_last_record = self.raw_records[-2]
        
        delta_phase_Rx1 = last_record[:,FDSignalType.RX1_PHASE.value] - second_last_record[:,FDSignalType.RX1_PHASE.value]
        
        delta_phase_Rx1_unwrapped = np.unwrap(delta_phase_Rx1, axis=0)
        
        measurement_rate = 5  # Number of measurements per second (adjust to your radar's measurement rate)
        f_D = delta_phase_Rx1_unwrapped * measurement_rate / (2 * np.pi)

        # Compute the velocity for micro-Doppler analysis
        velocity = f_D * SPEED_LIGHT / (2 * f_c)
        
        f, t, Zxx = stft(velocity, fs=measurement_rate, nperseg=256, noverlap=128)
        
        # plt.figure(figsize=(10, 5))
        # plt.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
        # plt.title('Micro-Doppler Time-Frequency Analysis')
        # plt.xlabel('Range Bins')
        # plt.ylabel('Frequency (Hz)')
        # plt.colorbar(label='Magnitude')
        # plt.show()
        
        return None
    
    def process_new_data(self):
        if len(self.raw_records) < self.required_cells_cfar:
            # Not enough data to run CFAR
            return np.zeros((512, 8))

        num_bins = 512  # Assuming 512 range bins
        signals = [FDSignalType.I1, FDSignalType.Q1, FDSignalType.I2, FDSignalType.Q2]
        detection_matrix = np.zeros((num_bins, 8))
        
        relevate_deque_data = list(self.raw_records)[-self.required_cells_cfar:]
        
        # relevate_deque_data = list(itertools.islice(self.raw_records, len(self.raw_records) - self.required_cells_cfar, len(self.raw_records)))
        # relevant_data_np = np.concatenate(relevate_deque_data)

        for i in range(num_bins):  # Each range bin
            for idx, signal in enumerate(signals):
                data = np.array([item[i][signal.value] for item in relevate_deque_data])
                detection_matrix[i, idx*2], detection_matrix[i, idx*2+1] = cfar_single(data, 
                                                                                       index_CUT=self.index_to_eval,
                                                                                       cfar_params=self.cfar_params)
        return detection_matrix
    
    def get_signal_for_bin(self, bin_index, signalType: FDSignalType):
        """
        Retrieve the timestamp, raw signal values, and detection values for a specific bin and signal across all records.
        
        Parameters:
            bin_index (int): The index of the bin (0 to 511).
            signal_index (int): The index of the signal in the array structure for raw data.
            detection_index (int): The index of the signal in the array structure for detection data (may differ from signal_index).

        Returns:
            list of tuples: Each tuple contains (timestamp, raw value, detection value).
        """
        
        signals = []
        timestamps = []
        detections = []
        thresholds = []
        
        # Single loop to collect both time stamps, frequency values, detections and thresholds
        if signalType.value < 4:
            for i in range(len(self.timestamps)):
                timestamps.append((self.timestamps[i] - self.creation_time).total_seconds())
                signals.append(self.raw_records[i][bin_index, signalType.value])
                detections.append(self.detection_records[i][bin_index, signalType.value*2])
                thresholds.append(self.detection_records[i][bin_index, signalType.value*2+1])
        # For plotting the Rx Phase, and View Angles
        else:
            for i in range(len(self.timestamps)):
                timestamps.append((self.timestamps[i] - self.creation_time).total_seconds())
                signals.append(self.raw_records[i][bin_index, signalType.value])
        return signals, timestamps, detections, thresholds
    
    def get_signal_for_bins(self, signalType: FDSignalType):
        """
        Get the signal for all range bins for the current window
        return: Signal across all range bins as a function of time
        """
        signals = []
        timestamps = []
        detections = []
        
        # Skip non-frequency data
        if signalType.value < 4:
            for i in range(len(self.timestamps)):
                # Array length n, of each relative time entry when data was logged
                timestamps.append((self.timestamps[i] - self.creation_time).total_seconds())
                # Array of length n, which contans array of length 512. Each value of the 512 is a dBm value. Otherwise the index represents the range the value is assocaite to
                signals.append(self.raw_records[i][:, signalType.value])
                # Array of length n, which contans array of length 512. Each value is a 1 or 0 for a detection
                detections.append(self.detection_records[i][:, signalType.value*2])
    
        return np.array(signals), np.array(timestamps), np.array(detections)
    
    def get_all_detections_Rx1(self, signalType: FDSignalType):
        timestamps = []
        detections = []
        
        for i in range(len(self.timestamps)):
                # Array length n, of each relative time entry when data was logged
                timestamps.append((self.timestamps[i] - self.creation_time).total_seconds())
                # Array of length n, which contans array of length 512. Each value is a 1 or 0 for a detection
                detections.append(self.detection_records[i][:, FDSignalType*2])
                
        return np.array(timestamps), np.append(detections)
        
