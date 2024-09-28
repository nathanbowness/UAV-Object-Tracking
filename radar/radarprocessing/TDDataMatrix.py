from enum import Enum
import pandas as pd
import os

class TDDataMatrix():
    def __init__(self, td_data, timestamp = None):
        """
        Initialize the FDDataMatrix with data and an optional timestamp of when it was recorded.
        If no timestamp is provided, the current time is used.
        
        Parameters:
            fd_data (np.ndarray): The numerical data for the matrix. [512 x 4] Matrix Containing --> 
            I1 [V], Q1 [V], I2[V], Q@ [V]
            timestamp (time.time, optional): The timestamp for the data.
        """
        self.td_data = td_data
        self.timestamp = timestamp if timestamp else pd.Timestamp.now()
        
    def __str__(self):
        """
        String representation of batch matrices with a single timestamp.
        """
        return f"Batch Timestamp: {self.timestamp}\nMatrices Data: {self.fd_data.shape}"
    
    def print_data_to_file(self, folder_location: str):
        # Create the directory if it doesn't exist
        os.makedirs(folder_location, exist_ok=True)

        # Format the timestamp to a safe and standard file name format
        timestamp_str = self.timestamp.strftime('%Y-%m-%d_%H-%M-%S')
        file_name = f"FD_{timestamp_str}.csv"

        # Full path to the file
        full_path = os.path.join(folder_location, file_name)
        
        column_headers = ['I1 [V]', 'Q1 [V]', 'I2 [V]', 'Q2 [V]']
        
        # Convert the numpy array to a DataFrame for easy CSV writing
        df = pd.DataFrame(self.fd_data.reshape(-1, 4), columns=column_headers)  # Reshape to a 2D array if necessary
        df.to_csv(full_path, index=False)
        
        print(f"Data written to {full_path}")
        
class TDSignalType(Enum):
    I1=0
    Q1=1
    I2=2
    Q2=3