import argparse
import numpy as np
import multiprocessing as mp
import time
import torch

# from plots.PlotRadarFrequencyHeatMapDynamic import PlotRadarFrequencyHeatMapDynamic
# from plots.PlotDetectionsDynamic import PlotDetectionsDynamic
# from plots.PlotPolarDynamic import PlotPolarDynamic
# import matplotlib
# matplotlib.use('Qt5Agg') # Required for GUI support on linux
# import matplotlib.pyplot as plt
# plt.ion()  # Enable interactive mode

from datetime import datetime

# Different tracking programs
from tracking.ObjectTracking import ObjectTrackingExtendedObjectGNN
from radar_object_tracking.configuration.CFARParams import CFARParams
from radar_object_tracking.configuration.RadarRunParams import RadarRunParams
from radar_object_tracking.radar_tracking import RadarTracking
from object_tracking_yolo_v8 import track_objects


def radar_tracking_task(stop_event, args, radar_data_queue: mp.Queue, plot_data_queue: mp.Queue):
   
    cfar_params = CFARParams(num_guard=10, num_train=15, threshold=12, threshold_is_percentage=False)
    radar_params = RadarRunParams(args, cfar_params)
    radar_tracking = RadarTracking(radar_params, radar_data_queue, plot_data_queue)

    radar_tracking.object_tracking(stop_event)
    time.sleep(0.1)  # Add a delay to avoid busy-waiting
        
def process_queues(stop_event, image_data_queue, radar_data_queue, plot_data_queue = None):
    
    tracking = ObjectTrackingExtendedObjectGNN(time.time())
    count = 1
    
    while not stop_event.is_set():
        # Handle image data queue
        while image_data_queue is not None and not image_data_queue.empty():
            try:
                detectionsAtTime = image_data_queue.get(timeout=1)  # Add timeout to avoid blocking
                timestamp = detectionsAtTime.timestamp
                detections = detectionsAtTime.detections
                dataType = detectionsAtTime.type
                
                tracking.update_tracks(detections, timestamp, type=dataType)
                count += 1
                if (count % 10 == 0):
                    tracking.show_tracks_plot()
            except mp.queues.Empty:
                pass

        # Handle radar data queue
        while radar_data_queue is not None and not radar_data_queue.empty():
            try:
                detections_raw = radar_data_queue.get(timeout=1)  # Add timeout to avoid blocking
                # print(f"Received radar data: {detections_raw}")
                
                if (detections_raw == "DONE"):
                    print("Radar data processing is done.")
                    tracking.show_tracks_plot()
                    break
                
                # Extract the array data and time from the detections dictionary
                array_data = detections_raw['data']
                timestamp = detections_raw['time']
                
                # Convert array_data to a numpy array
                detection_array = np.array([[float(d['x']), float(d['x_v']), float(d['y']), float(d['y_v'])] for d in array_data])
                
                # Convert time_str to datetime object using the provided format                  
                # timestamp = datetime.strptime(time_str, '%Y-%m-%d %H-%M-%S')
                
                tracking.update_tracks(detection_array, timestamp)
                
                # if (len(tracking.timesteps) % 50 == 0):
                #     tracking.show_tracks_plot()
                count += 1
                
            except mp.queues.Empty:
                pass
            except Exception as e:
                print(f"Error processing radar data: {e}")
                pass
            
def plot_data(plot_queue: mp.Queue, stop_event):
    # import matplotlib
    # matplotlib.use('Qt5Agg')  # Use TkAgg backend for GUI support
    # import matplotlib.pyplot as plt
    # plt.ion()  # Enable interactive mode
    # max_distance_plotted = 60
    
    # polarPlot = PlotPolarDynamic(min_angle=-90, max_angle=90, max_distance=40, interval=50)
    # detectionsPlot = PlotDetectionsDynamic(num_plots=2, plot_titles=["Rx1 Detections", "Rx2 Detections"], interval=50, max_bins=512)
    # heatMapPlot = PlotRadarFrequencyHeatMapDynamic(title="Raw FD Data Heatmap", range_bin_size=0.199861, min_distance=5, max_distance=max_distance_plotted)
    
    # heatMapPlotFreq = PlotRadarFrequencyHeatMapDynamic(title="MicroDop Freq", range_bin_size=0.199861, min_limit=0, max_limit=0.5, min_distance=5, max_distance=max_distance_plotted)
    # heatMapPlotVelocity = PlotRadarFrequencyHeatMapDynamic(title="Velocity", range_bin_size=0.199861, min_limit=-2, max_limit=1, min_distance=5, max_distance=max_distance_plotted)
    
    # plt.show(block=False)  # Show the plot window without blocking
    # plt.pause(0.1)
    # count = 0

    while not stop_event.is_set():
        while plot_queue is not None and not plot_queue.empty():
            try:                
                plot_data = plot_queue.get(timeout=1)
                # if (plot_data["type"] == "detections"):
                #     detections_data = plot_data["data"]
                #     detectionsPlot.update_data([detections_data["Rx1"], detections_data["Rx2"]])
                    
                # elif (plot_data["type"] == "polar"):
                #     distances, angles = plot_data["dist"], plot_data["angles"]
                #     # polarPlot.update_data(distances, angles, clear=True)
                    
                # elif (plot_data["type"] == "magnitude"):
                #     magnitude_data = plot_data["data"]
                #     time = plot_data["relativeTimeSec"]
                #     heatMapPlot.update_data(time, magnitude_data)
                    
                # elif (plot_data["type"] == "microFreq"):
                #     magnitude_data = plot_data["data"]
                #     time = plot_data["relativeTimeSec"]
                #     heatMapPlotFreq.update_data(time, magnitude_data)
                    
                # elif (plot_data["type"] == "velocity"):
                #     magnitude_data = plot_data["data"]
                #     time = plot_data["relativeTimeSec"]
                #     heatMapPlotVelocity.update_data(time, magnitude_data)
                    
                plt.pause(0.1)
                
                if count % 20 == 0:
                    print(f"Plotting data")
                
                count += 1
                    
                # distances, angles = plot_data["dist"], plot_data["angles"]
                # polarPlot.update_data(distances, angles, clear=True)
                # plt.pause(0.1)
                
                # Convert the angles to radians, so we can then get the x, y coordinates
                # angles_in_radians = np.radians(angles)
                # x_coord_detections = distances * np.cos(angles_in_radians)
                # y_coord_detections = distances * np.sin(angles_in_radians)
                # x_vel = np.full(x_coord_detections.shape, 1)
                # y_vel = np.full(y_coord_detections.shape, 1)
                
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
    
    # Options added by me
    parser.add_argument('--skip-video', action='store_true', help='skip video tracking')
    parser.add_argument('--skip-radar', action='store_true', help='skip radar tracking')
    parser.add_argument('--skip-tracking', action='store_true', help='skip the tracking algorithm and path creation')
    parser.add_argument('--enable-plot', action='store_true', help='enable plotting')
    parser.add_argument('--radar-from-file', action='store_true', help='use radar data from file')
    parser.add_argument('--radar-source', type=str, default='data/radar', help='source folder to pull the radar data from. Only used if "radar-from-file" is set')
    parser.set_defaults(download=True)
    args = parser.parse_args()
    opt = parser.parse_args()
    
    # Create a stop event and a queue for radar_data
    stop_event = mp.Event()
    radar_data_queue = None
    image_data_queue = None
    plot_data_queue = None
    
    # plotting process
    if args.enable_plot:
        plot_data_queue = mp.Queue()
    
    # Create the radar tracking process
    if not args.skip_radar:
        radar_data_queue = mp.Queue()
        radar_proc = mp.Process(target=radar_tracking_task, args=(stop_event, args, radar_data_queue, plot_data_queue))
        radar_proc.start()
        
    if not args.skip_video:
        image_data_queue = mp.Queue()
        # Create the video tracking process if it's not skipped
        with torch.no_grad():
            video_proc = mp.Process(target=track_objects, args=(opt, image_data_queue))
            video_proc.start()
            
    if not args.skip_tracking:
        # Queue process to handle incoming data
        tracking_proc = mp.Process(target=process_queues, args=(stop_event, image_data_queue, radar_data_queue, plot_data_queue))
        tracking_proc.start()
    
    if args.enable_plot:
        plot_data(plot_data_queue, stop_event) # Start the plot data process
    
    try:
        while True:
            user_input = input("Type 'q' and hit ENTER to quit: ")
            if user_input.lower() == 'q':
                stop_event.set()
                break
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        if not args.skip_radar:
            radar_proc.join()
        if not args.skip_video:
            video_proc.join()
            
        tracking_proc.join()

    print(f"Tracking duration: {time.time() - start_time:.2f} seconds")
