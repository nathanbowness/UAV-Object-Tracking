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

from video.VideoConfiguration import VideoConfiguration
from tracking.TrackingConfiguration import TrackingConfiguration

from cli_arguments import define_argument_parser, update_radar_config, update_video_config, update_tracking_config

# Different tracking programs
from tracking.ObjectTrackingGmPhd import get_object_tracking_gm_phd
from radar.configuration.RadarConfiguration import RadarConfiguration
from radar.radar_tracking import RadarTracking
from video.object_tracking_yolo_v8 import track_objects

import pandas as pd

def radar_tracking_task(stop_event, config: RadarConfiguration, start_time: pd.Timestamp, radar_data_queue: mp.Queue, plot_data_queue: mp.Queue):
    radar_tracking = RadarTracking(config, start_time, radar_data_queue, plot_data_queue)
    radar_tracking.object_tracking(stop_event)
    time.sleep(0.1)  # Add a delay to avoid busy-waiting
        
def process_queues(stop_event, tracker, image_data_queue, radar_data_queue, plot_data_queue = None):
    
    count = 1
    while not stop_event.is_set():
        # Handle image data queue
        while image_data_queue is not None and not image_data_queue.empty():
            try:
                detectionsAtTime = image_data_queue.get(timeout=1)  # Add timeout to avoid blocking
                timestamp = detectionsAtTime.timestamp
                detections = detectionsAtTime.detections
                dataType = detectionsAtTime.type
                
                tracker.update_tracks(detections, timestamp, type=dataType)
                count += 1
                if (count % 300 == 0):
                    tracker.show_tracks_plot()
            except mp.queues.Empty:
                pass

        # Handle radar data queue
        while radar_data_queue is not None and not radar_data_queue.empty():
            try:
                detections_raw = radar_data_queue.get(timeout=1)  # Add timeout to avoid blocking
                # print(f"Received radar data: {detections_raw}")
                
                if (detections_raw == "DONE"):
                    print("Radar data processing is done.")
                    tracker.show_tracks_plot()
                    break
                
                # Extract the array data and time from the detections dictionary
                array_data = detections_raw['data']
                timestamp = detections_raw['time']
                
                # Convert array_data to a numpy array
                detection_array = np.array([[float(d['x']), float(d['x_v']), float(d['y']), float(d['y_v'])] for d in array_data])
                
                # Convert time_str to datetime object using the provided format                  
                # timestamp = datetime.strptime(time_str, '%Y-%m-%d %H-%M-%S')
                
                tracker.update_tracks(detection_array, timestamp)
                tracker.print_current_tracks(interval = 1) # remove tracks older than 1 second for now
                
                # if (len(tracking.timesteps) % 50 == 0):
                #     tracking.show_tracks_plot()
                count += 1
                
            except mp.queues.Empty:
                pass
            except Exception as e:
                print(f"Error processing radar data: {e}")
                pass
    
    tracker.print_current_tracks()
    tracker.show_tracks_plot()
            
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
    start_time = pd.Timestamp.now()
    parser = define_argument_parser()
    parser.set_defaults(download=True)
    args = parser.parse_args()
    
    print("Starting the tracking processes.")
    
    # Create a stop event and a queue for data to be passed between processes
    stop_event = mp.Event()
    radar_data_queue = None
    image_data_queue = None
    plot_data_queue = None
    
    # Create the radar tracking configuration, process, queue to move data if not disabled
    if not args.skip_radar:
        radar_config = RadarConfiguration(config_path=args.radar_config)
        radar_config = update_radar_config(radar_config, args) # Update the radar configuration with the command line arguments
        
        radar_data_queue = mp.Queue()
        radar_proc = mp.Process(name="Radar Data Coll.", target=radar_tracking_task, args=(stop_event, radar_config, start_time, radar_data_queue, plot_data_queue))
        radar_proc.start()
      
    # Create the video tracking configuration, process, queue to move data
    if not args.skip_video:
        video_config = VideoConfiguration(config_path=args.video_config)
        video_config = update_video_config(video_config, args) # Update the video configuration with the command line arguments
        
        image_data_queue = mp.Queue()
        with torch.no_grad():
            video_proc = mp.Process(name="Video Data Coll.", target=track_objects, args=(stop_event, video_config, image_data_queue))
            video_proc.start()  
      
    # Create the object tracking configuration, process, queue to move data      
    if not args.skip_tracking:
        tracking_config = TrackingConfiguration()
        tracking_config = update_tracking_config(video_config, args) # Update the video configuration with the command line arguments
        tracker = get_object_tracking_gm_phd(start_time, tracking_config)
        
        # Queue process to handle incoming data
        tracking_proc = mp.Process(name="Tracking", target=process_queues, args=(stop_event, tracker, image_data_queue, radar_data_queue, plot_data_queue))
        tracking_proc.start()
        
    # plotting process
    # if args.enable_plot:
        
    #     plot_data_queue = mp.Queue()
    #     plot_data(plot_data_queue, stop_event) # Start the plot data process
    
    try:
        print("Starting the tracking processes.")
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
        if not args.skip_tracking:
            tracking_proc.join()

    print(f"Tracking duration: {time.time() - start_time:.2f} seconds")
