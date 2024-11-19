import csv
import numpy as np
import pandas as pd
import re
from datetime import datetime

from radar.radarprocessing.TDData import TDData

def extract_timestamp_from_filename(filename):
    """
    Extract the last timestamp from a file or folder path.
    If multiple timestamps are found, the last one is returned.
    """
    # Regex pattern for timestamps with optional milliseconds
    timestamp_pattern = r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}(?:\.\d{3})?)'

    # Find all matches for the timestamp pattern
    matches = re.findall(timestamp_pattern, filename)
    if matches:
        # Get the last match (or the second one explicitly, if needed)
        timestamp_str = matches[-1]  # Change to matches[1] if you want the second explicitly
        
        # Replace underscores with spaces to match datetime format
        timestamp_str = timestamp_str.replace('_', ' ')
        
        # Parse the timestamp (check if milliseconds are included)
        if '.' in timestamp_str:
            dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H-%M-%S.%f')
        else:
            dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H-%M-%S')
        
        # Convert to Pandas Timestamp
        return pd.Timestamp(dt)
    else:
        raise ValueError(f"No valid timestamp found in path: {filename}")

def read_columns(file_path) -> TDData:
    columns = {
        '<I1>': [],
        '<Q1>': [],
        '<I2>': [],
        '<Q2>': []
    }
    td_data = None
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
        td_data = TDData(mag_data, timestamp=timestamp)
    return td_data

if __name__ == '__main__':
    # Example usage
    file_path = 'data/radar/run1-TD/TD-Data_2024-08-14_13-33-18.376.txt'
    data = read_columns(file_path)
    print(data)