import time
import pandas as pd
import os

class FDDataMatrix():
    def __init__(self, fd_data, timestamp = None):
        """
        Initialize the FDDataMatrix with data and an optional timestamp of when it was recorded.
        If no timestamp is provided, the current time is used.
        
        Parameters:
            fd_data (np.ndarray): The numerical data for the matrix. [512 x 7] Matrix Containing --> 
            [I1 [dBm], Q1 [dBm], I2 [dBm], Q1 [dBm], Rx1 Phase [Rad], Rx2 Phase [Rad], Estimated View Angle [Deg]]
            timestamp (time.time, optional): The timestamp for the data.
        """
        self.fd_data = fd_data
        self.timestamp = timestamp if timestamp else time.time()
        
    def __str__(self):
        """
        String representation of batch matrices with a single timestamp.
        """
        return f"Batch Timestamp: {self.timestamp}\nMatrices Data: {self.data.shape}"
    
    def print_data_to_file(self, folder_location: str):
        # Create the directory if it doesn't exist
        os.makedirs(folder_location, exist_ok=True)

        # Format the timestamp to a safe and standard file name format
        timestamp_str = self.timestamp.strftime('%Y-%m-%d_%H-%M-%S')
        file_name = f"FD_{timestamp_str}.csv"

        # Full path to the file
        full_path = os.path.join(folder_location, file_name)

        # Convert the numpy array to a DataFrame for easy CSV writing
        df = pd.DataFrame(self.data.reshape(-1, 7))  # Reshape to a 2D array if necessary
        df.to_csv(full_path, index=False)
        
        print(f"Data written to {full_path}")