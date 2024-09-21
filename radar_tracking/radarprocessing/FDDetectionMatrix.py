class FDDetectionMatrix():
    """
    Matrix to track the detections of an object after running a CFAR algorithm
    detection_matrix: Matrix of 1's and 0. 1 is a detected object, 0 is not. The format is of [I1, I1_Thresh, Q1, Q1_Thresh, I2, I2_Thresh, Q2_Thresh] (512x8)
    timestamp: time when the original sample was collected
    """
    def __init__(self, detection_matrix, timestamp):
        self.dectections = detection_matrix
        self.timestamp = timestamp
        print("")