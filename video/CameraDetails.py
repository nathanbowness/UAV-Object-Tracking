class CameraDetails():
    def __init__(self,
                 bbCoefficientsMap : map,
                 horz_fov : float = 62.7,
                 zoom_factor : int = 1,
                 image_width : int = 1920,
                 image_height: int = 1080):
        """
        Details of the camera used for object detection.
        
        :param bbCoefficientsMap (map): coefficient map to convert BB width to distance for each object
        :param horiz_fov_deg (float): horizontal field of view in degrees
        :param zoom_factor (int): zoom factor of the camera
        :param image_width (int): width of the image in pixels
        :param image_height (int): height of the image in pixels
        """
        self.bbCoefficientsMap = bbCoefficientsMap
        self.horz_fov = horz_fov
        self.zoom_factor = zoom_factor
        
        self.image_width = image_width
        self.image_height = image_height
        self.aspect_ratio = image_width / image_height