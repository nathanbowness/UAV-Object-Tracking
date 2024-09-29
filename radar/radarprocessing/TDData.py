from enum import Enum
import pandas as pd
import os

class TDData():
    def __init__(self, td_data, timestamp = None):
        """
        Initialize the TDDataMatrix with data and an optional timestamp of when it was recorded.
        If no timestamp is provided, the current time is used.
        
        Parameters:
            td_data (np.ndarray): The numerical data for the matrix. [1024x4] Matrix Containing --> 
            I1 [V], Q1 [V], I2[V], Q2 [V]
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
        # Format the timestamp to a safe and standard file name format
        timestamp_str = self.timestamp.strftime('%Y-%m-%d_%H-%M-%S.%f')[:-3]
        file_name = f"TD_{timestamp_str}.txt"
        file_path = os.path.join(folder_location, file_name)
        
        # Create a pandas DataFrame
        df = pd.DataFrame(self.td_data, columns=["I1", "Q1", "I2", "Q2"])

        # Create a header for the file
        header = (
            "Unit of the Time Domain Samples:\t[V]\n"
            "=======================================================\n"
            "<I1>\t<Q1>\t<I2>\t<Q2>\n\n"
        )

        # Write header and DataFrame to a .txt file
        with open(file_path, "w") as file:
            file.write(header)  # Write the header to the file
            # Use to_csv with tab separator and no index or header, float formatted to four decimals
            df.to_csv(file, sep='\t', index=False, header=False, float_format="%.4f")
        
class TDSignalType(Enum):
    I1=0
    Q1=1
    I2=2
    Q2=3