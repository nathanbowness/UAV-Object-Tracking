import csv
import numpy as np
import pandas as pd
import re
from datetime import datetime

from config import get_radar_params
from constants import SPEED_LIGHT, DIST_BETWEEN_ANTENNAS
from radar_tracking.radarprocessing.FDDataMatrix import FDDataMatrix


def extract_timestamp_from_filename(filename):
    # Try to extract the timestamp part from the filename using regex with milliseconds
    match = re.search(r'trial\d?_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.\d{3})', filename)
    if match:
        timestamp_str = match.group(1)
        # Replace underscores with spaces to match the format
        timestamp_str = timestamp_str.replace('_', ' ')
        # Parse the timestamp string using datetime
        dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H-%M-%S.%f')
    else:
        # Try to extract the timestamp part from the filename using regex without milliseconds
        match = re.search(r'trial\d?_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})', filename)
        if match:
            timestamp_str = match.group(1)
            # Replace underscores with spaces to match the format
            timestamp_str = timestamp_str.replace('_', ' ')
            # Parse the timestamp string using datetime
            dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H-%M-%S')
        else:
            raise ValueError(f"Filename does not match the expected format: {filename}")
    
    # Convert to pd.Timestamp
    timestamp = pd.Timestamp(dt)
    return timestamp



def determine_phase_angle(I1_phase: np.array, 
                          Q1_phase: np.array, 
                          I2_phase: np.array, 
                          Q2_phase: np.array):
    """
    Determine the phase angle of the signal based on the phase of the I and Q components of the signal.
    All signals should be in radaians
    """
    radarParams = get_radar_params()
    fc = (radarParams.minFreq*(10**6)) + (radarParams.manualBW / 2)*(10**6)
    
    # Calculate phases for Rx1 and Rx2
    theta_Rx1 = np.unwrap(np.arctan2(I1_phase, Q1_phase))
    theta_Rx2 = np.unwrap(np.arctan2(I2_phase, Q2_phase))
    
    # Phase difference between Rx1 and Rx2
    delta_theta = theta_Rx2 - theta_Rx1
    
    # Calculate object angle (in radians)
    object_angle_radians = (delta_theta * SPEED_LIGHT) / (2 * np.pi * fc * DIST_BETWEEN_ANTENNAS)
    
    alpha = np.arcsin(np.clip(object_angle_radians, -1, 1))
    
    # conver names
    alpha_degrees = np.degrees(alpha)
    phase_differences_unwrapped = delta_theta
    phase1 = np.degrees(theta_Rx1)
    phase2 = np.degrees(theta_Rx2)

    # OLD CALCULATION METHOD
    # epsilon = 1e-10
    # phase1 = np.arctan(Q1_phase / (I1_phase + epsilon))
    # phase2 = np.arctan(Q2_phase / (I2_phase + epsilon))
    
    # phase_differences = phase2 - phase1
    # phase_differences = I1_phase - I2_phase
    
    # # phase_differences = I2_phase - I1_phase
    # phase_differences_unwrapped = np.unwrap([phase_differences])[0]
    
    # sin_alpha = (phase_differences_unwrapped * SPEED_LIGHT) / (2 * np.pi * fc * DIST_BETWEEN_ANTENNAS)
    
    # sin_alpha = np.clip(sin_alpha, -1, 1)
        
    # alpha = np.arcsin(sin_alpha)
    # alpha_degrees = np.degrees(alpha)  # Convert from radians to degrees
    
    # An array of measured data - [Rx1 Phase [Rad], Rx2 Phase [Rad], Phase_Diff, Estimated View Angle [Deg]] (512 x 4)
    return np.vstack((phase1, phase2, phase_differences_unwrapped, alpha_degrees)).T

def read_columns(file_path):
    columns = {
        '<Mag. I1>': [],
        '<Phase I1>': [],
        '<Mag. Q1>': [],
        '<Phase Q1>': [],
        '<Mag. I2>': [],
        '<Phase I2>': [],
        '<Mag. Q2>': [],
        '<Phase Q2>': []
    }
    
    calcs = {
        'Rx1Phase': [],
        'Rx2Phase': [],
        'EstAngle': []
    }  
    
    fd_data_matrix = None
    with open(file_path, 'r') as file:
        # Skip lines until the delimiter line is found
        for line in file:
            if line.strip() == '=======================================================':
                break
        
        # Read the header
        reader = csv.DictReader(file, delimiter='\t')
        
        # Print the column names to debug
        # print("Column names in file:", reader.fieldnames)
        
        for row in reader:
            for col in columns:
                if col in row:
                    columns[col].append(float(row[col]))
                else:
                    print(f"Warning: Column '{col}' not found in row.")
        
        phase_angles_calcs = determine_phase_angle(np.radians(np.array(columns['<Phase I1>'])), 
                                                   np.radians(np.array(columns['<Phase Q1>'])), 
                                                   np.radians(np.array(columns['<Phase I2>'])),
                                                   np.radians(np.array(columns['<Phase Q2>'])))
        mag_data = np.vstack((np.array(columns['<Mag. I1>']), np.array(columns['<Mag. Q1>']), np.array(columns['<Mag. I2>']), np.array(columns['<Mag. Q2>']))).T
        
        # Extract timestamp from filename
        timestamp = extract_timestamp_from_filename(file_path)              
        fd_data_matrix = FDDataMatrix(np.hstack((mag_data, phase_angles_calcs)), timestamp=timestamp)
    return fd_data_matrix

if __name__ == '__main__':
    # Example usage
    file_path = 'data/radar/FD/trial_2024-08-14_13-33-18.376.txt'
    data = read_columns(file_path)
    print(data)