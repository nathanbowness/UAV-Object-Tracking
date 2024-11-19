from collections import deque
from tracking.DetectionsAtTime import DetectionDetails, DetectionsAtTime
from radar.cfar import ca_cfar_detector, cfar_ca_full, cfar_single, cfar_required_cells
from radar.radarprocessing.FDDataMatrix import FDSignalType
from radar.configuration.CFARParams import CFARParams
from radar.radarprocessing.TDData import TDData
from scipy.signal import spectrogram

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
    velocity_records -> np array (512, 2) [frequency, velocity]s
    """
    def __init__(self, 
                 cfar_params: CFARParams, 
                 start_time: pd.Timestamp, 
                 bin_size: float = 199.939e-3,
                 f_c: float = 24.35e9,
                 capacity: int = 200,
                 duration_seconds=None, 
                 run_velocity_measurements=False):
        
        self.creation_time = start_time
        
        self.timestamps = deque()
        self.raw_records = deque()
        self.records_fft = deque()
        
        self.detection_records = deque()
        self.movement_records = deque()
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
        
        # Spectrogram
        self.movement_mask = True
        self.spectrogram_cfar = CFARParams(num_guard=2, num_train=5, threshold=2.8)
        self.spectrogram_num_elements = 5
        self.distance_grace_multiplier = 1.2
        
        # Window to apply window, optionally can use a kaiser window as well
        # beta = 6.5  # Adjust this to control sidelobe levels vs. main lobe width
        # self.window = np.kaiser(1024, beta)
        self.window = np.hamming(1024)
        
        self.total_time = 0
        self.total_time_entries = 0

    def add_raw_record(self, record : TDData):
        """
        Add a record to the deque.
        Ensure the deque doesn't exceed the capacity set
        """
        self.timestamps.append(record.timestamp)
        self.raw_records.append(record.td_data)
        
        # Calculate the difference between the current record coming in and the previous record
        if len(self.raw_records) > 1:
            self.diff_records.append(record.td_data - self.raw_records[-1])
            dif = record.timestamp - self.timestamps[-2]
            self.total_time += dif.total_seconds()
            self.total_time_entries += 1
        
        # Apply the Hanning window to each channel before FFT
        I1_windowed = record.td_data[:, 0] * self.window
        Q1_windowed = record.td_data[:, 1] * self.window
        I2_windowed = record.td_data[:, 2] * self.window
        Q2_windowed = record.td_data[:, 3] * self.window
        
        # Calculate the FFT of the record
        I1_fft = np.fft.fft(I1_windowed)[:512]
        Q1_fft = np.fft.fft(Q1_windowed)[:512]
        I2_fft = np.fft.fft(I2_windowed)[:512]
        Q2_fft = np.fft.fft(Q2_windowed)[:512]
        
        self.records_fft.append(np.array([I1_fft, Q1_fft, I2_fft, Q2_fft]))
        self.remove_old_records()
    
    def remove_old_records(self):
        # Remove records based on capacity if capacity is specified
        if self.capacity and len(self.raw_records) == self.capacity:
            self.timestamps.popleft()
            self.raw_records.popleft()
            self.records_fft.popleft()
            self.detection_records.popleft()
            # self.movement_records.popleft()
        
        # Remove records based on time window if duration is specified
        elif self.duration:
            current_time = pd.Timestamp.now().replace(microsecond=0)
            while self.timestamps and (current_time - self.timestamps[0] > self.duration):
                self.timestamps.popleft()
                self.raw_records.popleft()
                self.records_fft.popleft()
                self.detection_records.popleft()
                # self.movement_records.popleft()
    
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

        # Set the first 3 values to 0
        I1_fft[0] = Q1_fft[0] = I2_fft[0] = Q2_fft[0] = 0
        I1_fft[1] = Q1_fft[1] = I2_fft[1] = Q2_fft[1] = 0

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
        
        # Apply masks based on movement
        mask = self.get_indexes_with_movement_only_Rx1(detected_distances_Rx1)
        detected_angles_Rx1 = detected_angles_Rx1[mask]
        detected_distances_Rx1 = detected_distances_Rx1[mask]
        
        # Calculate detected distances and angles for Rx2
        rx2_indexes_with_detections = np.where(cfar_detection_Rx2)[0]
        detected_distances_Rx2 = rx2_indexes_with_detections * self.bin_size
        detected_angles_Rx2 = angles[rx2_indexes_with_detections]
        
        # Apply masks based on movement
        mask = self.get_indexes_with_movement_only_Rx1(detected_distances_Rx2)
        detected_angles_Rx2 = detected_angles_Rx2[mask]
        detected_distances_Rx2 = detected_distances_Rx2[mask]
        
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
        
        # Mask detections, that have movement found in them
        mask = self.get_indexes_with_movement_only_Rx1(detected_distances_combined)
        detected_distances_combined = detected_distances_combined[mask]
        detected_angles_combined = detected_angles_combined[mask]
        
        # Convert polar coordinates to Cartesian coordinates for combined detections
        x_combined = detected_distances_combined * np.cos(np.radians(detected_angles_combined))
        y_combined = detected_distances_combined * np.sin(np.radians(detected_angles_combined))
        
        # Add detection details for combined detections
        for x, y in zip(x_combined, y_combined):
            detections.append(DetectionDetails("Rx1", [x, 0.2, y, 0.2]))
        
        return DetectionsAtTime(timestamps, RADAR_DETECTION_TYPE, detections)

    
    def get_indexes_with_movement_only_Rx1(self, current_detections_and_distances):
        
        # If the mask shouldn't be applied, just return here
        if not self.movement_mask:
            return np.arange(len(current_detections_and_distances))
        
        if (len(self.raw_records) >= self.spectrogram_num_elements):
        
            Rxs1 = []

            # Loop through the last spectrogram_num_elements of the deque
            for i in range(self.spectrogram_num_elements):
                record_index = -1 - i
                I1, Q1, I2, Q2 = self.raw_records[record_index].T
                Rx1 = I1 + 1j * Q1
                Rxs1.append(Rx1)

            avg_sample_time_sec = self.total_time / self.total_time_entries
            if avg_sample_time_sec == 0:
                avg_sample_time_sec = 0.241 # This is the normal avg time between entries

            # Convert Rxs1 to an array if needed
            Rxs = np.array(Rxs1)
            Fs = 1024/avg_sample_time_sec
            
            f1, t1, Sxx1 = spectrogram(Rxs.flatten(), fs=Fs, nperseg=1024, noverlap=512)
            # self.movement_records.append(np.array([f1, t1, Sxx1])) # For now, this isn't used so no point in adding it
            
            avg_power1 = np.mean(np.abs(Sxx1), axis=1)
            cfar_mask, _, _= ca_cfar_detector(avg_power1, 
                                              self.spectrogram_cfar.num_train, 
                                              self.spectrogram_cfar.num_guard, 
                                              self.spectrogram_cfar.threshold)
            
            cfar_mask[0] = cfar_mask[1] = 0
            # Highlight detected peaks with CFAR
            detected_freqs = f1[cfar_mask == 1]
            detected_freqs_hz = detected_freqs  # Detected beat frequencies in Hz

            # Convert the beat frequencies to range (distance), subtract
            m_w = ( (self.f_c - 24e9) * 2 / avg_sample_time_sec)
            ranges = (SPEED_LIGHT * detected_freqs_hz) / (2 * m_w)
            distances_with_doppler = abs(ranges)
            
            diffs = np.abs(current_detections_and_distances[:, np.newaxis] - distances_with_doppler)
            
            mask_dif_size = self.bin_size * self.distance_grace_multiplier
            mask = np.any(diffs <= mask_dif_size, axis=1)
            
            # Return indexes of current detections within 1.2 of the bin size
            indexes = np.where(mask)[0]
            return indexes
        else:
            return np.full(len(current_detections_and_distances), False, dtype=bool)