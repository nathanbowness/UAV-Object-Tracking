import yaml
from ultralytics import YOLO
import cv2
import math

# Known values of object width in meters
relative_sizes = {
    'airplane': 60.0,
    'apple': 0.1,
    'backpack': 0.4,
    'banana': 0.15,
    'baseball bat': 0.1,
    'baseball glove': 0.3,
    'bench': 1.5,
    'bicycle': 1.8,
    'bird': 0.3,
    'boat': 4.0,
    'bottle': 0.1,
    'bowl': 0.2,
    'broccoli': 0.2,
    'bus': 2.5,
    'cake': 0.3,
    'car': 2.0,
    'carrot': 0.05,
    'cat': 0.3,
    'chair': 0.5,
    'couch': 2.0,
    'cow': 1.5,
    'dog': 0.5,
    'donut': 0.1,
    'elephant': 3.0,
    'fire hydrant': 0.4,
    'fork': 0.03,
    'frisbee': 0.25,
    'giraffe': 1.0,
    'handbag': 0.4,
    'horse': 0.8,
    'hot dog': 0.2,
    'kite': 1.0,
    'knife': 0.03,
    'motorcycle': 0.9,
    'orange': 0.1,
    'parking meter': 0.2,
    'person': 0.6,
    'pizza': 0.4,
    'potted plant': 0.3,
    'sheep': 0.8,
    'skateboard': 0.3,
    'skis': 0.15,
    'snowboard': 0.3,
    'spoon': 0.03,
    'sports ball': 0.25,
    'stop sign': 0.6,
    'suitcase': 0.5,
    'surfboard': 0.5,
    'tennis racket': 0.3,
    'tie': 0.1,
    'traffic light': 0.4,
    'train': 4.0,
    'truck': 2.5,
    'umbrella': 0.8,
    'wine glass': 0.1,
    'zebra': 1.5
}

def get_object_width_from_camera(object_name, image_width=None, image_height=None, save_image_path = None):
    # Load the YOLOv8 model (you can specify a pre-trained model like 'yolov8n', 'yolov8s', etc.)
    model = YOLO('yolov8n.pt')

    # Capture video from the first camera (0)
    cap = cv2.VideoCapture(0)
    
    # Set the image width and height if specified
    if image_width is not None:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, image_width)
    if image_height is not None:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, image_height)
        
    # Verify if the resolution was set correctly
    actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"Resolution set to: {actual_width}x{actual_height}")

    # Read a single frame from the video source (camera 0)
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame from camera.")
        return None

    # Run YOLOv8 inference on the frame to detect objects
    results = model(frame)

    # Parse the results to find the object of interest by name and draw bounding boxes on the frame
    detected_object_width = None
    for result in results:
        for obj in result.boxes:
            class_name = model.names[int(obj.cls)]  # Get the name of the detected object
            x1, y1, x2, y2 = map(int, obj.xyxy[0].tolist())  # Get bounding box coordinates as integers

            # Draw the bounding box rectangle
            color = (0, 255, 0)  # Green bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Put the class label text
            label = f"{class_name}: {obj.conf[0]:.2f}"  # Include confidence score
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            # If the detected object matches the desired one, calculate its width
            if class_name == object_name:
                detected_object_width = x2 - x1  # Calculate width in pixels
            
    # Save the image with the bounding boxes drawn
    if save_image_path is not None:
        cv2.imwrite(save_image_path, frame)
        print(f"Image with bounding boxes saved to {save_image_path}")

    # Close the camera stream
    cap.release()

    return detected_object_width

def determine_bb_coeff_for_object(distance_from_camera, object_name, object_width_meters, camera_horizontal_fov, image_width, image_height, save_image_path = None):
    """
    Determine the bounding box coefficient for a given object.
    
    :param distance_from_camera (float): distance from the camera to the object in meters
    :param object_name (str): name of the object
    :param object_width_meters (float): width of the object in meters
    :param camera_horizontal_fov (float): horizontal field of view in degrees
    :param image_width (int): width of the image in pixels
    :param image_height (int): height of the image in pixels
    :param save_image_path (str): path to save the image with bounding boxes (optional)
    :return: the bounding box coefficient
    """
    # Get the pixel width of the object from the camera image
    object_pixel_width  = get_object_width_from_camera(object_name, image_width, image_height, save_image_path=save_image_path)
    if object_pixel_width is None:
        print(f"Could not detect object: {object_name}")
        return None
    print(f"Object '{object_name}' detected with width: {object_pixel_width} pixels, at {distance_from_camera}m")
    
    # Calculate focal length based on the camera's horizontal field of view (FOV)
    horizon_fov_rad = math.radians(camera_horizontal_fov)  # Convert FOV to radians
    focal_length_pixels = image_width / (2 * math.tan(horizon_fov_rad / 2))  # Focal length in pixels

    # Calculate the bounding box coefficient (BB coefficient)
    bb_coefficient = (distance_from_camera * object_pixel_width) / (focal_length_pixels * object_width_meters)

    print(f"Bounding Box Coefficient for '{object_name}': {bb_coefficient}")

    return bb_coefficient

def write_bb_coefficients_to_file(bb_coefficients, file_name):
    with open(file_name, 'w') as file:
        yaml.dump({"bbCoefficients": bb_coefficients}, file, default_flow_style=False)

def determine_all_bb_coefficients(object_name, known_object_size_meters, known_bb_coefficient, file_name = "BBCoefficients.yaml"):
    
    if object_name is None or known_bb_coefficient is None:
        print("Please provide the object name and known BB coefficient.")
        return None
    
    if known_object_size_meters is None:
        if object_name not in relative_sizes:
            print(f"Please provide the known object size for '{object_name}'")
        else :
            known_object_size_meters = relative_sizes[object_name]
    
     # Initialize the BB coefficient map
    bb_coefficients = {}

    # Populate the BB coefficient for all objects based on the known object's coefficient
    for obj_name, obj_size in relative_sizes.items():
        bb_coefficients[obj_name] = known_bb_coefficient * (known_object_size_meters / obj_size)

    write_bb_coefficients_to_file(bb_coefficients, file_name)
    return bb_coefficients

if __name__ == "__main__":
    distance = 1.8
    object_name = "suitcase"
    camera_horizontal_fov = 65
    known_object_size = 0.35
    bb_coefficient = determine_bb_coeff_for_object(distance, object_name, known_object_size, camera_horizontal_fov, 1920, 1080, "test.jpg")
    determine_all_bb_coefficients(object_name, known_object_size, bb_coefficient, "BBCoefficients.yaml")
