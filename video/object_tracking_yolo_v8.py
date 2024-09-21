from tracking.DetectionsAtTime import DetectionDetails, DetectionsAtTime
from ultralytics import YOLO
import time
from datetime import datetime
from PIL import Image
import os
import multiprocessing as mp
import math
from constants import IMAGE_DETECTION_TYPE

from video.object_location_size import CameraDetails, object_location
from video.VideoConfiguration import VideoConfiguration

def setup_output_folders(output_directory : str, save_raw_img : bool = True, start_time = None):
    """
    Create the output folder structure for the run
    Args:
        output_directory (str): the root folder to save the results
        save_raw_img (bool): if True, save the original images to disk
        start_time (datetime): the time the run started, used to create a unique folder name
    Returns:
        output_folder (str): the path to the folder where the run results will be saved
    """
    
    if start_time is None:
        start_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    output_folder = os.path.join(output_directory, start_time)
    os.makedirs(output_folder, exist_ok=True)
    
    if (save_raw_img):
        # Create a folder to save the raw output images if the option is selected
        raw_output_folder = os.path.join(output_folder, "raw")
        os.mkdir(raw_output_folder)
        print("Saving contents of the run to: ", raw_output_folder)
    
    return output_folder    

def on_predict_batch_end(predictor, start_time):
    print("Predictions completed in {:.2f}s".format(time.time() - start_time))
    
    for result in predictor.results:
        for box in result.boxes:
            classificationIndex = box.cls[0].item()
            detected_object = result.names[classificationIndex]
            print(f"Object: {detected_object}, Confidence { box.conf[0].item()}")
            # print(box)
            
def detection_from_bbox(yolo_box, detected_object, camera_details : CameraDetails):
    """
    Calculate the object location and size from the bounding box coordinates.
    
    :param yolo_box: Yolo bounding box definition
    :param detected_object: The object detected
    :param camera_details: A CameraDetails object containing details of the camera.
    :return: Detection object containing the object type and location.
    """
    # print(f"Object: {detected_object}, Confidence { yolo_box.conf[0].item()}")
    
    x1, y1, x2, y2 = yolo_box.xyxy[0].tolist()
    polar_range_data = object_location(x1, y1, x2, y2, camera_details=camera_details, detected_object=detected_object)
    
    # Convert angles from degrees to radians
    az_angle_rad = math.radians(polar_range_data[0])
    el_angle_rad = math.radians(polar_range_data[1])
    distance = polar_range_data[2]
    
    # Calculate the horizontal distance (on the ground)
    distance_horizontal = distance * math.cos(el_angle_rad)
    
    # Calculate x (horizontal) and y (vertical) distances
    x = distance_horizontal * math.sin(az_angle_rad)  # Horizontal distance in the x direction
    y = distance * math.sin(el_angle_rad)  # Vertical distance in the y direction
    
    return DetectionDetails(detected_object, [x, 0, y , 0])
    
def track_objects(stop_event = mp.Event(), video_config = VideoConfiguration, data_queue : mp.Queue = None):
    ### PARAMs to the program
    model_weights = video_config.modelWeights
    save_raw_img = video_config.saveRawImages
    save_detection_video = video_config.saveProcessedVideo
    output_directory = video_config.outputDirectory  
    source = video_config.videoSource
      
    # source = "https://www.youtube.com/watch?v=CN2m0SfLT9Q" # walking through park
    # source = "https://www.youtube.com/watch?v=Guk_ql0-ZyM" # walking back and forth
    # source = "https://www.youtube.com/watch?v=Mol0lrRBy3g"
    source = "/data/video/M0101.mp4"
    confidence_threshold = video_config.confidenceThreshold
    
    iou_threshold = video_config.iouThreshold
    stream = video_config.videoStream
    # Graphical show users
    show_boxes = video_config.showBoxesInVideo
    show = video_config.showVideo
    ### END OF PARAMS
    
    if source == "" or source is None:
        raise Exception("No video source provided. Please provide a source for the video.")
    
    camera = video_config.camera_details
    
    output_folder = setup_output_folders(output_directory, save_raw_img)
    model = YOLO(model_weights)
    # model.add_callback("on_predict_batch_end", on_predict_batch_end)

    # save_crops=True # save detected crops as .jpg files, of the individual objects detected
    results = model.track(source=source, conf=confidence_threshold, iou=iou_threshold, save=save_detection_video, show=show, stream=stream, project=output_folder, show_boxes=show_boxes)

    for i, result in enumerate(results):
        if stop_event.is_set():
            break   
        orig_img_h = result.orig_img.shape[0]
        orig_img_w = result.orig_img.shape[1]
        
        # If configured, saved the original image to disk, in the <output_folder>/raw/*
        if save_raw_img:
            orig_img_rgb = Image.fromarray(result.orig_img[..., ::-1])  # Convert BGR to RGB
            orig_img_rgb.save(os.path.join(output_folder, "raw", f"image_{i}_{orig_img_w}x{orig_img_h}.jpg"))
        
        detectionTimestamp = datetime.now().replace(microsecond=0)
        detections = []
        
        # Iterate over the detected objects, add tracking details into the detections_data list
        for box in result.boxes:
            classificationIndex = box.cls[0].item()
            detected_object = result.names[classificationIndex]
            # print(f"Object: {detected_object}, Confidence { box.conf[0].item()}")
            
            detection = detection_from_bbox(box, detected_object, camera_details=camera)
            detections.append(detection)
        
        # If a data_queue is provided, put the detections into the queue
        if data_queue is not None and len(detections) > 0:
            data_queue.put(DetectionsAtTime(detectionTimestamp, IMAGE_DETECTION_TYPE, detections))
            
        # For debugging purposes, add 1 second delay between frames
        time.sleep(0.1)

if __name__ == "__main__":
    video_config = VideoConfiguration()
    track_objects(video_config, None)