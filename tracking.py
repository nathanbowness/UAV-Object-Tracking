import multiprocessing as mp
import time
import torch
import pandas as pd

from datetime import datetime, timedelta

from video.VideoConfiguration import VideoConfiguration
from tracking.TrackingConfiguration import TrackingConfiguration

from cli_arguments import define_argument_parser, update_radar_config, update_video_config, update_tracking_config

# Different tracking programs
from tracking.ObjectTrackingGmPhd import get_object_tracking_gm_phd
from radar.configuration.RadarConfiguration import RadarConfiguration
from radar.radar_tracking import RadarTracking
from video.object_tracking_yolo_v8 import track_objects

from datetime import datetime, timedelta
import time

import multiprocessing as mp
import queue
from datetime import datetime, timedelta

def radar_tracking_task(stop_event, config: RadarConfiguration, start_time: pd.Timestamp, radar_data_queue: mp.Queue):
    radar_tracking = RadarTracking(config, start_time, radar_data_queue)
    radar_tracking.object_tracking(stop_event)


def process_queues(stop_event, tracker, image_data_queue, radar_data_queue, batching_time=0.2):
    
    count = 1
    last_print_time = datetime.now()
    last_remove_tracks_time = datetime.now()
    time_window = timedelta(seconds=batching_time)  # Define the window
    max_wait_time = 0.14  # Wax wait time to check data in the queue (just less than half the batching time)

    last_batch_time = None

    # Buffers to store data for the next processing loop
    image_buffer = []
    radar_buffer = []

    while not stop_event.is_set():
        processed_anything = False
        image_detections_in_window = []
        radar_detections_in_window = []

        # Define a batch time window for collecting data
        if last_batch_time is None:
            last_batch_time = datetime.now()

        batch_window_end = last_batch_time + time_window  # Set the upper limit for the current batch window

        # Fetch all image data within the batch window
        try:
            # Process buffered image data from the previous loop
            for detectionsAtTime in image_buffer:
                image_timestamp = detectionsAtTime.timestamp
                if image_timestamp <= batch_window_end:
                    image_detections_in_window.append(detectionsAtTime)
                else:
                    # Keep the data for the next loop
                    break

            image_buffer = [d for d in image_buffer if d.timestamp > batch_window_end]

            # Process new data from the queue
            while image_data_queue is not None and not image_data_queue.empty():
                detectionsAtTime = image_data_queue.get(timeout=max_wait_time)
                image_timestamp = detectionsAtTime.timestamp
                
                if image_timestamp <= batch_window_end:
                    image_detections_in_window.append(detectionsAtTime)
                else:
                    # Buffer data for the next loop
                    image_buffer.append(detectionsAtTime)
                    break

        except queue.Empty:
            pass

        # Fetch all radar data within the batch window
        try:
            # Process buffered radar data from the previous loop
            for detectionsAtTime in radar_buffer:
                radar_timestamp = detectionsAtTime.timestamp
                if radar_timestamp <= batch_window_end:
                    radar_detections_in_window.append(detectionsAtTime)
                else:
                    # Keep the data for the next loop
                    break

            radar_buffer = [d for d in radar_buffer if d.timestamp > batch_window_end]

            # Process new data from the queue
            while radar_data_queue is not None and not radar_data_queue.empty():
                detectionsAtTime = radar_data_queue.get(timeout=max_wait_time)
                radar_timestamp = detectionsAtTime.timestamp
                
                if radar_timestamp <= batch_window_end:
                    radar_detections_in_window.append(detectionsAtTime)
                else:
                    # Buffer data for the next loop
                    radar_buffer.append(detectionsAtTime)
                    break

        except queue.Empty:
            pass

        # Process both image and radar data if available within the time window
        if image_detections_in_window and radar_detections_in_window:
            combined_timestamp = max(
                image_detections_in_window[-1].timestamp, radar_detections_in_window[-1].timestamp
            )
            combined_detections = (
                image_detections_in_window[-1].detections + radar_detections_in_window[-1].detections
            )
            tracker.update_tracks(combined_detections, combined_timestamp, type="combined")
            
        elif image_detections_in_window:
            image_timestamp = image_detections_in_window[-1].timestamp
            image_detections = image_detections_in_window[-1].detections
            tracker.update_tracks(image_detections, image_timestamp, type="image_only")

        elif radar_detections_in_window:
            radar_timestamp = radar_detections_in_window[-1].timestamp
            radar_detections = radar_detections_in_window[-1].detections
            tracker.update_tracks(radar_detections, radar_timestamp, type="radar_only")
        else:
            last_batch_time = datetime.now()  # Set the start of the next batch window
            
            time.sleep(0.01) # Small sleep to avoid busy waiting
            continue
        
        count += 1
        current_time = datetime.now()
        last_batch_time = current_time  # Set the start of the next batch window
        # Print current tracks approx every 5 seconds
        if (current_time - last_print_time).total_seconds() >= 5:
            
            remove = False
            interval = batching_time*2
            # Print current tracks with remove_tracks=True every 30 seconds, this will remove tracks that are not being updated
            if (current_time - last_remove_tracks_time).total_seconds() >= 30:
                remove = True
                interval = batching_time*10
                last_remove_tracks_time = current_time

            tracker.print_current_tracks(remove_tracks=remove, interval=interval)
            last_print_time = current_time

    tracker.show_tracks_plot()
    tracker.print_current_tracks(remove_tracks=True, interval=batching_time*2)
            
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
        radar_proc = mp.Process(name="Radar Data Coll.", target=radar_tracking_task, args=(stop_event, radar_config, start_time, radar_data_queue))
        radar_proc.start()
      
    # Create the object tracking configuration, process, queue to move data
    if not args.skip_tracking:
        tracking_config = TrackingConfiguration()
        tracking_config = update_tracking_config(tracking_config, args) # Update the video configuration with the command line arguments
        tracking_config.max_track_distance = radar_config.bin_size_meters * 512 # Override the max distance based on radar range
        tracker = get_object_tracking_gm_phd(start_time, tracking_config)
        
        # Queue process to handle incoming data
        tracking_proc = mp.Process(name="Tracking", target=process_queues, args=(stop_event, tracker, image_data_queue, radar_data_queue, args.batching_time))
        tracking_proc.start()
        
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
