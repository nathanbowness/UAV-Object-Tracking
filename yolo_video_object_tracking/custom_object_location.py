import math

def ImageCharacteristics():
    def __init__(self, 
                 image_width : int = 1920,
                 image_height: int = 1080,
                 fov : int = 62.7,
                 convert_bb_to_distance_coefficent : float = 1.813851):
        self.image_width = image_width
        self.image_height = image_height
        self.fov = fov
        self.convert_bb_to_distance_coefficent = convert_bb_to_distance_coefficent

def object_location(top_left_x, top_left_y,bottom_right_x,bottom_right_y, ZoomFactor=1):
    # Input constants
    ImageWidth = 640  # Width of the image in pixels
    ImageHeight = 480  # Height of the image in pixels
    FOV = 65  # Field of view of the camera in degrees
    ConvertBBToDistanceCoefficent = 0.64  # Anker camera
    # ConvertBBToDistanceCoefficent = 1.813851  # Coefficient to convert BB width to distance
    
    BBWidth=(bottom_right_x-top_left_x + 1)/ImageWidth
    BBHorizontalCenter = (top_left_x + bottom_right_x )/2/ImageWidth
    BBVerticalCenter= (top_left_y + bottom_right_y)/2/ImageHeight

    # Calculated variables
    FOV_horizontal = FOV  # Horizontal field of view of the camera in degrees
    FOV_vertical = 2 * math.degrees(math.atan(math.tan(math.radians(FOV / 2)) * ImageHeight / ImageWidth))/1.5566  # Vertical field of view of the camera in degrees
    BBWidthPixels = BBWidth * ImageWidth  # Width of the bounding box in pixels
    BBHorizontalCenterPixels = BBHorizontalCenter * ImageWidth  # BB horizontal center position in pixels
    BBVerticalCenterPixels = BBVerticalCenter * ImageHeight  # BB vertical center position in pixels

    # Calculated output variables
    # Estimated azimuth and elevation angles of the object in degrees
    if (BBHorizontalCenterPixels - ImageWidth / 2) >= 0:
        OutputEstimatedAzAngle = 90 - (BBHorizontalCenterPixels - ImageWidth / 2) / ImageWidth * (FOV_horizontal / ZoomFactor)
    else:
        OutputEstimatedAzAngle = 90 + abs((BBHorizontalCenterPixels - ImageWidth / 2) / ImageWidth * (FOV_horizontal / ZoomFactor))

    if (BBVerticalCenterPixels - ImageHeight / 2) < 0:
        OutputEstimatedElAngle = abs((BBVerticalCenterPixels - ImageHeight / 2) / ImageHeight * (FOV_vertical / ZoomFactor))
    else:
        OutputEstimatedElAngle = -((BBVerticalCenterPixels - ImageHeight / 2) / ImageHeight * (FOV_vertical / ZoomFactor))

    # Estimated distance to the object in meters
    OutputEstimatedDistance = ConvertBBToDistanceCoefficent * 1 / (BBWidth / ZoomFactor)

    # Final output
    OutputVec = [OutputEstimatedAzAngle, OutputEstimatedElAngle, OutputEstimatedDistance]
    return OutputVec
