import csv
import numpy as np
import pandas as pd
import re
from datetime import datetime

from radar_object_tracking.radarprocessing.TDDataMatrix import TDDataMatrix

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
            raise ValueError(f"Filename does not match the expected format: {filename}, ")
    
    # Convert to pd.Timestamp
    timestamp = pd.Timestamp(dt)
    return timestamp

def read_columns(file_path):
    columns = {
        '<I1>': [],
        '<Q1>': [],
        '<I2>': [],
        '<Q2>': []
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
        
        mag_data = np.vstack((np.array(columns['<I1>']), np.array(columns['<Q1>']), np.array(columns['<I2>']), np.array(columns['<Q2>']))).T
        
        # Extract timestamp from filename
        timestamp = extract_timestamp_from_filename(file_path)          
        fd_data_matrix = TDDataMatrix(mag_data, timestamp=timestamp)
    return fd_data_matrix

if __name__ == '__main__':
    # Example usage
    file_path = 'data/radar/run1-TD/TD-Data_2024-08-14_13-33-18.376.txt'
    data = read_columns(file_path)
    print(data)