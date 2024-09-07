from radar_object_tracking.configuration.CFARType import CfarType

class CFARParams():    
    def __init__(self, num_guard: int = 2, num_train: int = 5, threshold: float = 10.0, threshold_is_percentage: bool = False):
        # CasoCFAR Params
        self.cfar_type = CfarType.CASO
        self.num_guard = num_guard
        self.num_train = num_train
        self.threshold = threshold
        self.threshold_is_percentage = threshold_is_percentage