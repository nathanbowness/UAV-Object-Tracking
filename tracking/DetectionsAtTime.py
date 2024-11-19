from typing import List, Literal
from datetime import datetime

class DetectionDetails:
    def __init__(self, obj_type: str, detection_data: List[float]):
        """
        Initialize a single detection.

        :param obj_type: The type of the detected object (e.g., 'vehicle', 'bird').
        :param detection: A list containing [x, x_v, y, y_v] values as floats.
        """
        self.object = obj_type  # Store the type of the object
        self.data = detection_data  # Store the detection data [x, x_v, y, y_v]

    def __repr__(self):
        """
        Provide a string representation of the Detection object for easy debugging and printing.

        :return: A string describing the Detection object.
        """
        return f"Detection(object={self.object}, detection={self.data})"


class DetectionsAtTime:
    def __init__(self, timestamp: datetime, data_type: Literal['radar', 'video'], detections: List[DetectionDetails]):
        """
        Initialize the DetectionsAtTime object.

        :param timestamp: The time when the data was captured, as a datetime object.
        :param data_type: A string indicating the type of data, either 'radar' or 'video'.
        :param detections: A list of Detection objects representing individual detections.
        """
        self.timestamp = timestamp  # Store the timestamp of the data
        self.type = data_type  # Store the type of data ('radar' or 'video')
        self.detections = detections  # Store the list of Detection objects

    def __repr__(self):
        """
        Provide a string representation of the DetectionsAtTime object for easy debugging and printing.

        :return: A string describing the DetectionsAtTime object.
        """
        return f"DetectionsAtTime(timestamp={self.timestamp}, type={self.type}, detections={self.detections})"


# Example usage:
# detections_list = [
#     Detection(obj_type="vehicle", detection=[1.0, 1.1, 2.0, 2.1]),
#     Detection(obj_type="bird", detection=[3.0, 3.1, 4.0, 4.1])
# ]
# detections_at_time = DetectionsAtTime(
#     timestamp=datetime.now(),
#     data_type='radar',
#     detections=detections_list
# )
# print(detections_at_time)
