from enum import Enum

class CfarType(Enum):
    """
    Enumeration for different types of Constant False Alarm Rate (CFAR) detection algorithms.

    Attributes
    ----------
    CASO : int
        Represents the Cell Averaging Smallest Of (CASO) CFAR algorithm. Value is 0.
    LEADING_EDGE : int
        Represents the Leading Edge CFAR algorithm. Value is 1.
    """
    
    CASO = 0
    LEADING_EDGE = 1