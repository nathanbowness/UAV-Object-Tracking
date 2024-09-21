import math

from video.CameraDetails import CameraDetails

def object_location(top_left_x, top_left_y,bottom_right_x,bottom_right_y, camera_details : CameraDetails, detected_object = "person"):
    """
    Given the bounding box coordinates, calculate the object location and size.
    
    :param top_left_x: x-coordinate of the top-left corner of the bounding box
    :param top_left_y: y-coordinate of the top-left corner of the bounding box
    :param bottom_right_x: x-coordinate of the bottom-right corner of the bounding box
    :param bottom_right_y: y-coordinate of the bottom-right corner of the bounding box
    :param camera_details: A CameraDetails object containing details of the camera.
    :param detected_object: The type of object detected
    """
    
    # Image, Camera details
    ImageWidth = camera_details.image_width  # Width of the image in pixels
    ImageHeight = camera_details.image_height   # Height of the image in pixels
    Aspect_ratio = camera_details.aspect_ratio  # Aspect ratio of the image
    
    if detected_object in camera_details.bbCoefficientsMap:
        ConvertBBToDistanceCoefficent = camera_details.bbCoefficientsMap[detected_object]
    else: 
        # Set to default value if the object is not in the map
        ConvertBBToDistanceCoefficent = 1.813851  # Coefficient to convert BB width to distance

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