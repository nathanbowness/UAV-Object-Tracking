from collections import deque
from tracking.DetectionsAtTime import DetectionDetails, DetectionsAtTime
from radar.cfar import ca_cfar_detector, caso_cfar, cfar_ca_2, cfar_ca_full, cfar_single, cfar_required_cells
from radar.radarprocessing.FDDataMatrix import FDSignalType
from radar.configuration.CFARParams import CFARParams
from radar.radarprocessing.TDData import TDData

import numpy as np
import pandas as pd
from datetime import timedelta
from constants import RADAR_DETECTION_TYPE, SPEED_LIGHT, DIST_BETWEEN_ANTENNAS

class RadarDataWindow():
    """
    timestamps -> timestamp of when each record was recorded
    raw_records -> np array (1024, 4) [I1, Q1, I2, Q2] (all in Volts)
    records_fft -> np array (512, 4) [I1, Q1, I2, Q2] (in frequency domain)
    detection_records -> np array (512, 8) [Rx1_amp, Rx1_Threshold, Rx1 Detection, Rx1 Angle, Rx2_amp, Rx2_Threshold, Rx2 Detection, Rx2 Angle]
    velocity_records -> np array (512, 2) [frequency, velocity]
    """
    def __init__(self, 
                 cfar_params: CFARParams, 
                 start_time: pd.Timestamp, 
                 bin_size: float = 199.939e-3,
                 f_c: float = 24.35e9,
                 capacity: int = 1000,
                 duration_seconds=None, 
                 run_velocity_measurements=False):
        
        self.creation_time = start_time
        
        self.timestamps = deque()
        self.raw_records = deque()
        self.records_fft = deque()
        
        self.detection_records = deque()
        self.velocity_records = deque()
        self.diff_records = deque()
        self.capacity = capacity
        self.duration = timedelta(seconds=duration_seconds) if duration_seconds else None
        self.run_velocity_measurements = run_velocity_measurements
        
        # Cfar params
        self.cfar_params = cfar_params
        self.index_to_eval = cfar_params.num_train + cfar_params.num_guard
        self.required_cells_cfar = cfar_required_cells(cfar_params)
        
        # Center frequncy
        self.f_c = f_c
        self.bin_size = bin_size
        
        # Generate SFC gain curve
        self.range_vector = np.arange(512) * bin_size
        self.SFC_gain = self.range_vector ** 2

    def add_raw_record(self, record : TDData):
        """
        Add a record to the deque.
        Ensure the deque doesn't exceed the capacity set
        """
        self.timestamps.append(record.timestamp.replace(microsecond=0))
        # Calculate the difference between the current record coming in and the previous record
        if len(self.raw_records) > 1:
            self.diff_records.append(record.td_data - self.raw_records[-1])
        self.raw_records.append(record.td_data)
        
        # Calculate the FFT of the record
        I1_fft = np.fft.fft(record.td_data[:, 0])[:512]
        Q1_fft = np.fft.fft(record.td_data[:, 1])[:512]
        I2_fft = np.fft.fft(record.td_data[:, 2])[:512]
        Q2_fft = np.fft.fft(record.td_data[:, 3])[:512]
        
        self.records_fft.append(np.array([I1_fft, Q1_fft, I2_fft, Q2_fft]))
        self.remove_old_records()
    
    def remove_old_records(self):
        # Remove records based on capacity if capacity is specified
        if self.capacity and len(self.raw_records) == self.capacity:
            self.timestamps.popleft()
            self.raw_records.popleft()
            self.records_fft.popleft()
            self.detection_records.popleft()
        
        # Remove records based on time window if duration is specified
        elif self.duration:
            current_time = pd.Timestamp.now().replace(microsecond=0)
            while self.timestamps and (current_time - self.timestamps[0] > self.duration):
                self.timestamps.popleft()
                self.raw_records.popleft()
                self.records_fft.popleft()
                self.detection_records.popleft()
    
    def process_data(self):
        """
        Process the data in the window (potentially multiple records eventually, with micro doppler??)
        """
        I1_fft, Q1_fft, I2_fft, Q2_fft = self.records_fft[-1]
        angles = self.calculate_angles(I1_fft, Q1_fft, I2_fft, Q2_fft)

        I1_fft *= self.SFC_gain
        Q1_fft *= self.SFC_gain
        I2_fft *= self.SFC_gain
        Q2_fft *= self.SFC_gain

        I1_fft[0] = Q1_fft[0] = I2_fft[0] = Q2_fft[0] = 0

        I1_amp = np.abs(I1_fft)
        I1_phase = np.degrees(np.angle(I1_fft))
        Q1_amp = np.abs(Q1_fft)
        Q1_phase = np.degrees(np.angle(Q1_fft))
        I2_amp = np.abs(I2_fft)
        I2_phase = np.degrees(np.angle(I2_fft))
        Q2_amp = np.abs(Q2_fft)
        Q2_phase = np.degrees(np.angle(Q2_fft))

        Rx1 = I1_amp * np.exp(1j * np.radians(I1_phase)) + Q1_amp * np.exp(1j * np.radians(Q1_phase))
        Rx2 = I2_amp * np.exp(1j * np.radians(I2_phase)) + Q2_amp * np.exp(1j * np.radians(Q2_phase))

        Rx1_amp = np.abs(Rx1)
        Rx2_amp = np.abs(Rx2)
        
        cfar_detection_Rx1, cfar_threshold_Rx1, _ = cfar_ca_full(Rx1_amp, self.cfar_params.num_train, self.cfar_params.num_guard, self.cfar_params.threshold)
        cfar_detection_Rx2, cfar_threshold_Rx2, _ = cfar_ca_full(Rx2_amp, self.cfar_params.num_train, self.cfar_params.num_guard, self.cfar_params.threshold)
        
        detection_vector = np.column_stack((Rx1_amp, cfar_threshold_Rx1, cfar_detection_Rx1, angles, Rx2_amp, cfar_threshold_Rx2, cfar_detection_Rx2, angles))
        self.detection_records.append(detection_vector)
        
    def get_latest_detection(self):
        return self.detection_records[-1]
    
    def calculate_angles(self, I1_fft, Q1_fft, I2_fft, Q2_fft):
        """
        Calculate the angles of arrival of the signals
        """
        phase_diff_1 = np.angle(I1_fft * np.conj(I2_fft))
        # Option: we could use the average of the two phase differences
        phase_diff_2 = np.angle(Q1_fft * np.conj(Q2_fft))
        phase_diff = (phase_diff_1 + phase_diff_2) / 2
        sin_arg = (phase_diff * SPEED_LIGHT) / (2 * np.pi * DIST_BETWEEN_ANTENNAS * self.f_c)
        sin_arg = np.clip(sin_arg, -1, 1)  # Clip values to the valid range for arcsin
        angles = np.degrees(np.arcsin(sin_arg))
        return np.clip(angles, -90, 90)
    
    def get_detections_split_xy(self, index = -1) -> DetectionsAtTime:
        """
        Determine the most recent detections at the certain time.
        By default returns the most recent detections, but an index can be specified to return detections at a different time.
        """
        detections = []
        timestamps = self.timestamps[-1]
        _, _, cfar_detection_Rx1, angles, _, _, cfar_detection_Rx2, _ = self.detection_records[index].T
        
        # Calculate detected distances and angles for Rx1
        rx1_indexes_with_detections = np.where(cfar_detection_Rx1)[0]
        detected_angles_Rx1 = angles[rx1_indexes_with_detections]
        detected_distances_Rx1 = rx1_indexes_with_detections * self.bin_size
        
        # Calculate detected distances and angles for Rx2
        rx2_indexes_with_detections = np.where(cfar_detection_Rx2)[0]
        detected_distances_Rx2 = rx2_indexes_with_detections * self.bin_size
        detected_angles_Rx2 = angles[rx2_indexes_with_detections]
        
        # Convert polar coordinates to Cartesian coordinates for Rx1 and Rx2
        x_Rx1 = detected_distances_Rx1 * np.cos(np.radians(detected_angles_Rx1))
        y_Rx1 = detected_distances_Rx1 * np.sin(np.radians(detected_angles_Rx1))
        x_Rx2 = detected_distances_Rx2 * np.cos(np.radians(detected_angles_Rx2))
        y_Rx2 = detected_distances_Rx2 * np.sin(np.radians(detected_angles_Rx2))

        for x, y in zip(x_Rx1, y_Rx1):
            detections.append(DetectionDetails("Rx1", [x, 0.2, y, 0.2]))
    
        # Add detection details for Rx2
        for x, y in zip(x_Rx2, y_Rx2):
            detections.append(DetectionDetails("Rx2", [x, 0.2, y, 0.2]))
        
        return DetectionsAtTime(timestamps, RADAR_DETECTION_TYPE, detections)
    
    def get_detections_combined_xy(self, index = -1) -> DetectionsAtTime:
        """
        Determine the most recent detections at the certain time
        By default returns the most recent detections, but an index can be specified to return detections at a different time.
        """
        detections = []
        timestamps = self.timestamps[-1]
        _, _, cfar_detection_Rx1, angles, _, _, cfar_detection_Rx2, _ = self.detection_records[index].T
        
        # Ensure the CFAR detection arrays are boolean
        cfar_detection_Rx1 = cfar_detection_Rx1.astype(bool)
        cfar_detection_Rx2 = cfar_detection_Rx2.astype(bool)
        
        # Combine CFAR detections using logical OR
        combined_cfar_detection = cfar_detection_Rx1 | cfar_detection_Rx2
        
        # Calculate detected distances and angles for combined detections
        combined_indexes_with_detections = np.where(combined_cfar_detection)[0]
        detected_angles_combined = angles[combined_indexes_with_detections]
        detected_distances_combined = combined_indexes_with_detections * self.bin_size
        
        # Convert polar coordinates to Cartesian coordinates for combined detections
        x_combined = detected_distances_combined * np.cos(np.radians(detected_angles_combined))
        y_combined = detected_distances_combined * np.sin(np.radians(detected_angles_combined))
        
        # Add detection details for combined detections
        for x, y in zip(x_combined, y_combined):
            detections.append(DetectionDetails("Rx1", [x, 0.2, y, 0.2]))
        
        return DetectionsAtTime(timestamps, RADAR_DETECTION_TYPE, detections)

    
    
    
    
    
    
    # MORE TODO
    
    
    
    
    
    def calculate_detections(self):
        # We the raw TD data, and we have the FFT data.... Should be able to do everything now!!!! Need to pass in the f_c though 
        
        print("detect")

    def calculate_detections(self, record_timestamp: pd.Timestamp):
        detection_data = self.process_new_data()
        
        if self.run_velocity_measurements:
            if len(self.raw_records) < 10:
                return self.velocity_records.append(np.array([0, 0]))
            else:
                self.micro_doppler_velocity_analysis()
                
        self.detection_records.append(detection_data)
        
    def get_raw_records(self):
        return self.raw_records
    
    def get_detection_records(self):
        return self.detection_records
    
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







    # def get_signal_for_bin(self, bin_index, signalType: FDSignalType):
    #     """
    #     Retrieve the timestamp, raw signal values, and detection values for a specific bin and signal across all records.
        
    #     Parameters:
    #         bin_index (int): The index of the bin (0 to 511).
    #         signal_index (int): The index of the signal in the array structure for raw data.
    #         detection_index (int): The index of the signal in the array structure for detection data (may differ from signal_index).

    #     Returns:
    #         list of tuples: Each tuple contains (timestamp, raw value, detection value).
    #     """
        
    #     signals = []
    #     timestamps = []
    #     detections = []
    #     thresholds = []
        
    #     # Single loop to collect both time stamps, frequency values, detections and thresholds
    #     if signalType.value < 4:
    #         for i in range(len(self.timestamps)):
    #             timestamps.append((self.timestamps[i] - self.creation_time).total_seconds())
    #             signals.append(self.raw_records[i][bin_index, signalType.value])
    #             detections.append(self.detection_records[i][bin_index, signalType.value*2])
    #             thresholds.append(self.detection_records[i][bin_index, signalType.value*2+1])
    #     # For plotting the Rx Phase, and View Angles
    #     else:
    #         for i in range(len(self.timestamps)):
    #             timestamps.append((self.timestamps[i] - self.creation_time).total_seconds())
    #             signals.append(self.raw_records[i][bin_index, signalType.value])
    #     return signals, timestamps, detections, thresholds
    
    # def get_signal_for_bins(self, signalType: FDSignalType):
    #     """
    #     Get the signal for all range bins for the current window
    #     return: Signal across all range bins as a function of time
    #     """
    #     signals = []
    #     timestamps = []
    #     detections = []
        
    #     # Skip non-frequency data
    #     if signalType.value < 4:
    #         for i in range(len(self.timestamps)):
    #             # Array length n, of each relative time entry when data was logged
    #             timestamps.append((self.timestamps[i] - self.creation_time).total_seconds())
    #             # Array of length n, which contans array of length 512. Each value of the 512 is a dBm value. Otherwise the index represents the range the value is assocaite to
    #             signals.append(self.raw_records[i][:, signalType.value])
    #             # Array of length n, which contans array of length 512. Each value is a 1 or 0 for a detection
    #             detections.append(self.detection_records[i][:, signalType.value*2])
    
    #     return np.array(signals), np.array(timestamps), np.array(detections)
    
    # def get_all_detections_Rx1(self, signalType: FDSignalType):
    #     timestamps = []
    #     detections = []
        
    #     for i in range(len(self.timestamps)):
    #             # Array length n, of each relative time entry when data was logged
    #             timestamps.append((self.timestamps[i] - self.creation_time).total_seconds())
    #             # Array of length n, which contans array of length 512. Each value is a 1 or 0 for a detection
    #             detections.append(self.detection_records[i][:, FDSignalType*2])
                
    #     return np.array(timestamps), np.append(detections)        
