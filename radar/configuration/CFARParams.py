from radar.configuration.CFARType import CfarType

class CFARParams():
    """
    A class to define parameters for Constant False Alarm Rate (CFAR) detection.

    Parameters
    ----------
    num_guard : int, optional
        The number of guard cells around the target cell, which are not used in the noise estimate. Default is 2.
    num_train : int, optional
        The number of training cells used to estimate the noise level in the surrounding environment. Default is 5.
    threshold : float, optional
        The threshold value used to decide if a cell is a target or not. Default is 10.0.
    threshold_is_percentage : bool, optional
        Indicates if the threshold value is in percentage (True) or linear scale (False). Default is False.

    Attributes
    ----------
    cfar_type : CfarType
        The type of CFAR algorithm used (e.g., CASO, CA-CFAR). Default is set to CfarType.CASO.
    num_guard : int
        The number of guard cells around the target cell.
    num_train : int
        The number of training cells used for noise estimation.
    threshold : float
        The threshold value for detection.
    threshold_is_percentage : bool
        Indicates if the threshold value is in percentage or linear scale.
    """
    def __init__(self, num_guard: int = 2, num_train: int = 5, threshold: float = 10.0, threshold_is_percentage: bool = False):
        # CasoCFAR Params
        self.cfar_type = CfarType.CASO
        self.num_guard = num_guard
        self.num_train = num_train
        self.threshold = threshold
        self.threshold_is_percentage = threshold_is_percentage
        
    def __str__(self):
        """
        Returns a formatted string representation of the CFAR parameters.
        
        Returns
        -------
        str : A nicely formatted string listing all attributes and values.
        """
        percentage_str = "Percentage" if self.threshold_is_percentage else "Linear"
        return (f"CFAR Parameters:\n"
                f"  CFAR Type          : {self.cfar_type.name}\n"
                f"  Number of Guard Cells : {self.num_guard}\n"
                f"  Number of Training Cells : {self.num_train}\n"
                f"  Detection Threshold    : {self.threshold} ({percentage_str})")
