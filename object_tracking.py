import argparse
import multiprocessing as mp
import time
import threading

from radar_object_tracking.radar_tracking import radar_object_tracking


def cpu_bound_task():
    count = 0
    for i in range(10 ** 7):
        count += 1
    return count

def radar_tracking_task(stop_event, radar_data_queue):
    while not stop_event.is_set():
        result = radar_object_tracking()
        radar_data_queue.put(result)  # Put the result into the queue
        print(f"Radar tracking result: {result}")
        time.sleep(1)  # Add a delay to avoid busy-waiting
        

def thread_task():
    result = cpu_bound_task()
    print(f"Task completed with count = {result}")
    
if __name__ == '__main__':
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description='Object Tracking using Radar and Video')
    parser.add_argument('--video', type=str, default='data/vid.mp4', help='Path to video file')
    parser.add_argument('--radar', type=str, default='data/radar.csv', help='Path to radar data file')
    args = parser.parse_args()
    
    # Create a stop event and a queue for radar_data
    stop_event = mp.Event()
    radar_data_queue = mp.Queue()
    
    # Create the radar tracking process
    process1 = mp.Process(target=radar_tracking_task, args=(stop_event, radar_data_queue))
    process1.start()
    
    
    
    try:
        while True:
            user_input = input("Type 'q' to quit: ")
            if user_input.lower() == 'q':
                stop_event.set()
                break
            # Check if there is data in the queue
            while not radar_data_queue.empty():
                data = radar_data_queue.get()
                print(f"Received data: {data}")
                # Process the data as needed
    except KeyboardInterrupt:
        stop_event.set()

    # Wait for the radar tracking process to complete
    process1.join()

    print(f"Tracking duration: {time.time() - start_time:.2f} seconds")
