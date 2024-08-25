import argparse
import numpy as np
import multiprocessing as mp
import time
import torch
import matplotlib.pyplot as plt

# Different tracking programs
from radar_object_tracking.radar_tracking import radar_object_tracking
from yolo_video_object_tracking.detect import detect

from plots.PlotPolarDynamic import PlotPolarDynamic

def radar_tracking_task(stop_event, radar_data_queue : mp.Queue):
    while not stop_event.is_set():
        result = radar_object_tracking()
        radar_data_queue.put(result)  # Put the result into the queue
        time.sleep(0.1)  # Add a delay to avoid busy-waiting
        
def process_queues(image_data_queue, radar_data_queue, plot_data_queue, stop_event):  
    while not stop_event.is_set():
        # Handle image data queue
        while not image_data_queue.empty():
            try:
                data = image_data_queue.get(timeout=1)  # Add timeout to avoid blocking
                
                distances, angles = zip(*[(item['distance'], item['angle']) for item in data])
                distances, angles = np.array(distances), np.array(angles)  # Convert from tuples to lists
                plot_data_queue.put({"dist": distances, "angles": angles})
                
                # print(f"Received image data: {data}")
                # Process the data as needed
            except mp.queues.Empty:
                pass

        # Handle radar data queue
        while not radar_data_queue.empty():
            try:
                data = radar_data_queue.get(timeout=1)  # Add timeout to avoid blocking
                print(f"Received radar data: {data}")
                # Process the data as needed
            except mp.queues.Empty:
                pass
            
def plot_data(plot_queue: mp.Queue, stop_event):
    polarPlot = PlotPolarDynamic(min_angle=-90, max_angle=90, max_distance=40, interval=50)

    while not stop_event.is_set():
        while not plot_queue.empty():
            try:
                plot_data = plot_queue.get(timeout=1)
                distances, angles = plot_data["dist"], plot_data["angles"]
                polarPlot.update_data(distances, angles, clear=True)
                plt.pause(0.1)
            except mp.queues.Empty:
                pass
    
if __name__ == '__main__':
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description='Object Tracking using Radar and Video')
    parser.add_argument('--weights', nargs='+', type=str, default='yolov7.pt', help='model.pt path(s)')
    parser.add_argument('--download', action='store_true', help='download model weights automatically')
    parser.add_argument('--no-download', dest='download', action='store_false')
    parser.add_argument('--source', type=str, default='inference/images', help='source')  # file/folder, 0 for webcam
    parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=0.25, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='IOU threshold for NMS')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='display results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--update', action='store_true', help='update all models')
    parser.add_argument('--project', default='runs/detect', help='save results to project/name')
    parser.add_argument('--name', default='object_tracking', help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    parser.add_argument('--no-trace', action='store_true', help='don`t trace model')
    parser.add_argument('--blur', action='store_true', help='blur detections')
    parser.set_defaults(download=True)
    args = parser.parse_args()
    opt = parser.parse_args()
    
    # Create a stop event and a queue for radar_data
    stop_event = mp.Event()
    radar_data_queue = mp.Queue()
    image_data_queue = mp.Queue()
    plot_data_queue = mp.Queue()
    
    # Create the radar tracking process
    process1 = mp.Process(target=radar_tracking_task, args=(stop_event, radar_data_queue))
    process1.start()
    
    # Create the video tracking process
    with torch.no_grad():
        video_proc = mp.Process(target=detect, args=(opt, False, image_data_queue))
        video_proc.start()
    
    # Queue process to handle incoming data
    queue_proc = mp.Process(target=process_queues, args=(image_data_queue, radar_data_queue, plot_data_queue, stop_event))
    queue_proc.start()
    
    # plotting process
    plot_process = mp.Process(target=plot_data, args=(plot_data_queue, stop_event))
    plot_process.start()
    
    try:
        while True:
            user_input = input("Type 'q' and hit ENTER to quit: ")
            if user_input.lower() == 'q':
                stop_event.set()
                break
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        process1.join()
        video_proc.join()
        queue_proc.join()
        plot_process.join()

    print(f"Tracking duration: {time.time() - start_time:.2f} seconds")
