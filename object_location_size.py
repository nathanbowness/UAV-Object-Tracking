import math

class CameraDetails():
    def __init__(self,
                 horz_fov : float = 62.7,
                 covert_bb : float = 1.813851,
                 zoom_factor : int = 1):
        """
        Details of the camera used for object detection.
        
        :param horiz_fov_deg (float): horizontal field of view in degrees
        :param covert_bb (float): coefficient to convert BB width to distance
        :param zoom_factor (int): zoom factor of the camera
        """
        self.horz_fov = horz_fov
        self.covert_bb = covert_bb
        self.zoom_factor = zoom_factor
    

class ImageCharacteristics():
    def __init__(self, 
                 image_width : int = 1920,
                 image_height: int = 1080):
        self.image_width = image_width
        self.image_height = image_height
        self.aspect_ratio = image_width / image_height
    """
    Details of the image characteristics.
    
    :param image_width (int): width of the image in pixels
    :param image_height (int): height of the image in pixels
    """
    

def object_location(top_left_x, top_left_y,bottom_right_x,bottom_right_y, image_char : ImageCharacteristics, camera_details : CameraDetails):
    # Image, Camera details
    ImageWidth = image_char.image_width  # Width of the image in pixels
    ImageHeight = image_char.image_height   # Height of the image in pixels
    Aspect_ratio = image_char.aspect_ratio  # Aspect ratio of the image
    ConvertBBToDistanceCoefficent = camera_details.covert_bb  # Anker camera
    # ConvertBBToDistanceCoefficent = 1.813851  # Coefficient to convert BB width to distance

    BBWidth=(bottom_right_x-top_left_x + 1)/ImageWidth
    BBHorizontalCenter = (top_left_x + bottom_right_x )/2/ImageWidth
    BBVerticalCenter= (top_left_y + bottom_right_y)/2/ImageHeight

    # Calculated variables
    FOV_horizontal = camera_details.horz_fov  # Horizontal field of view of the camera in degrees
    FOV_vertical = 2 * math.degrees(math.atan(math.tan(math.radians(camera_details.horz_fov / 2)) * ImageHeight / ImageWidth))/Aspect_ratio # Vertical field of view of the camera in degrees
    BBWidthPixels = BBWidth * ImageWidth  # Width of the bounding box in pixels
    BBHorizontalCenterPixels = BBHorizontalCenter * ImageWidth  # BB horizontal center position in pixels
    BBVerticalCenterPixels = BBVerticalCenter * ImageHeight  # BB vertical center position in pixels

    # Calculated output variables
    # Estimated azimuth and elevation angles of the object in degrees
    if (BBHorizontalCenterPixels - ImageWidth / 2) >= 0:
        OutputEstimatedAzAngle = 90 - (BBHorizontalCenterPixels - ImageWidth / 2) / ImageWidth * (FOV_horizontal / camera_details.zoom_factor)
    else:
        OutputEstimatedAzAngle = 90 + abs((BBHorizontalCenterPixels - ImageWidth / 2) / ImageWidth * (FOV_horizontal / camera_details.zoom_factor))

    if (BBVerticalCenterPixels - ImageHeight / 2) < 0:
        OutputEstimatedElAngle = abs((BBVerticalCenterPixels - ImageHeight / 2) / ImageHeight * (FOV_vertical / camera_details.zoom_factor))
    else:
        OutputEstimatedElAngle = -((BBVerticalCenterPixels - ImageHeight / 2) / ImageHeight * (FOV_vertical / camera_details.zoom_factor))

    # Estimated distance to the object in meters
    OutputEstimatedDistance = ConvertBBToDistanceCoefficent * 1 / (BBWidth / camera_details.zoom_factor)

    # Final output
    OutputVec = [OutputEstimatedAzAngle, OutputEstimatedElAngle, OutputEstimatedDistance]
    return OutputVec