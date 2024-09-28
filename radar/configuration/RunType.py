from enum import Enum

class RunType(Enum):
    """
    ENUM of the type of run the program should perform
    LIVE - means the data will be run on a window of data, and not recorded
    LIVE_RECORD - means the data will be run on a window of data, and the results will be saved to the configured location
    RERUN - means the data will be read from an existing sample file, so the results will be read 1 by 1 from that pre-recorded data. A existing DataFormat is needed for that.
    """
    LIVE = 1,
    LIVE_RECORD = 2,
    RERUN = 3
    
class RunDataFormat(Enum):
    """
    ENUM of data format's that this Python code can read to perform object tracking tests from pre-recorded data
    """
    FD_CUSTOM = 1, # My own FD data that was recorded from this code
    SENTOOL_FD = 2, # Sentool's FD data and formats