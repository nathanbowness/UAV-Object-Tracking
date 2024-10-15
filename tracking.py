import multiprocessing as mp
import time
import torch

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
                
                if count % 25 == 0:
                    tracker.print_current_tracks(remove_tracks=False, interval=2)
            except mp.queues.Empty:
                pass
            except Exception as e:
                print(f"Error processing image data: {e}")
                pass

        # Handle radar data queue
        while radar_data_queue is not None and not radar_data_queue.empty():
            try:
                detectionsAtTime = radar_data_queue.get(timeout=1)  # Add timeout to avoid blocking
                timestamp = detectionsAtTime.timestamp
                detections = detectionsAtTime.detections
                dataType = detectionsAtTime.type
                
                tracker.update_tracks(detections, timestamp, type=dataType)
                count += 1
                
                if count % 25 == 0:
                    tracker.print_current_tracks(remove_tracks=False, interval=2)
            except mp.queues.Empty:
                pass
            except Exception as e:
                print(f"Error processing radar data: {e}")
                pass
    
    tracker.show_tracks_plot()
    tracker.print_current_tracks(remove_tracks=True, interval=1)
            
def plot_data(plot_queue: mp.Queue, stop_event):
    while not stop_event.is_set():
        while plot_queue is not None and not plot_queue.empty():
            try:                
                plot_data = plot_queue.get(timeout=1)
                # For now, do nothing. 
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
      
    # Create the video tracking configuration, process, queue to move data
    if not args.skip_video:
        video_config = VideoConfiguration(config_path=args.video_config)
        video_config = update_video_config(video_config, args) # Update the video configuration with the command line arguments
        
        image_data_queue = mp.Queue()
        with torch.no_grad():
            video_proc = mp.Process(name="Video Data Coll.", target=track_objects, args=(stop_event, video_config, start_time, image_data_queue))
            video_proc.start()  
    
    # Create the radar tracking configuration, process, queue to move data if not disabled
    if not args.skip_radar:
        if not args.skip_video: # Add a delay to allow the video process to start before the radar process
            time.sleep(args.radar_start_delay)
        radar_config = RadarConfiguration(config_path=args.radar_config)
        radar_config = update_radar_config(radar_config, args) # Update the radar configuration with the command line arguments
        
        radar_data_queue = mp.Queue()
        radar_proc = mp.Process(name="Radar Data Coll.", target=radar_tracking_task, args=(stop_event, radar_config, start_time, radar_data_queue, plot_data_queue))
        radar_proc.start()
      
    # Create the object tracking configuration, process, queue to move data      
    if not args.skip_tracking:
        tracking_config = TrackingConfiguration()
        tracking_config = update_tracking_config(tracking_config, args) # Update the video configuration with the command line arguments
        tracker = get_object_tracking_gm_phd(start_time, tracking_config)
        
        # Queue process to handle incoming data
        tracking_proc = mp.Process(name="Tracking", target=process_queues, args=(stop_event, tracker, image_data_queue, radar_data_queue, plot_data_queue))
        tracking_proc.start()
        
    # plotting process - remove for now, provided little value
    # if args.enable_plot:
        
    #     plot_data_queue = mp.Queue()
    #     plot_data(plot_data_queue, stop_event) # Start the plot data process
    
    try:
        while True:
            user_input = input("Type 'q' and hit ENTER to quit:\n")
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

    duration = time.time() - start_time.timestamp()
    print(f"Tracking duration: {duration:.2f} seconds")
