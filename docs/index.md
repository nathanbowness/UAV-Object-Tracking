# Object Tracking using Yolov8 and FMCW Radar

This project is **currently in progress**. 

This project's goal is to create software that can be used to track objects using both live radar sensor data and video using yolo. The latest version of this project is using Yolov8 for object detection through video. The radar processing is done using a IMST custom radar toolkit, with custom implemented signal and CFAR processing. The tracking portion of those individual signal results is done using Stone Soup's library.

## Where to Start

* Get a quickstart by running this software in a docker container - [Running in Docker](./guides/runningInDocker.md)
* Customizing the arguments run in the container - [Configuration](./configuration/configuration.md)

## Development

* Please see the [Developer Environment](./setup/devEnviroment.md) section under setup.

## Architecture
The design of this process uses python multiprocess queues to move data between the radar and video processing to the tracking algorithm. 
The queue allows for better synchronization of the data, and abstraction to swap out various video or tracking algorithms in the future. The queue follow the data shape described in [Detections Spec](./configuration/detections-spec.md)

```mermaid
flowchart LR
    %% Class definition to allow for bigger icon pictures
    classDef bigNode font-size:24px;

    subgraph tracking["Tracking.py"]
        %%  Radar Processing SubGraph
        subgraph radarProc["**RadarProcess.py**"]
            style desc1 text-align:left
            desc1["`1 Collect data
            2 Data drocessing
            3 Put detection into queue`"]
        end

        %%  Image Processing SubGraph
        subgraph imageProc["`**ImageProcess.py**`"]
            style desc2 text-align:left
            desc2["`1 Collect image
            2 Data processing
            3 Put detection into queue`"]
        end
        Queue[["MP Queue"]]
        subgraph trackProc["`**ObjectTracking.py**`"]
            style desc3 text-align:left
            desc3["`1 Read data from queue
            2 Update tracks based of new data
            3 Report current tracks`"]
        end
    end
    Radar[["Radar"]]:::bigNode
    Video[[Video]]:::bigNode

    Radar <--> radarProc
    Video <--> imageProc
    radarProc --> Queue
    imageProc --> Queue
    Queue -- Data read from Queue --> trackProc
```


## Algorithm for Data Processing
The system processes data from both radar and video sensors, each sending data to their respective queues: the radar processing queue and the image processing queue. Data from both sensors can arrive at different rates, so a batching mechanism with a 0.3-second window is used to synchronize them.

Every 0.3 seconds, all available data is retrieved from both queues. This window is chosen because it ensures that both radar and video processing have completed at least once in that period. If both radar and video data are available within the same batch, they are combined and used for tracking. If only one is available, it is used alone.

When multiple detections are present within the 0.3-second window, the latest detection is used for tracking. Future improvements will allow either taking an average of the detections or selecting the detection with the highest confidence score for better tracking accuracy.

As performance improves, the batching window can be adjusted to handle data more frequently while maintaining synchronization between the radar and video data.


```mermaid
graph TD
    subgraph Image Process
        A1(Video Data Capture)
        A1 -->|Sends to| Q1[image_data_queue]
    end

    subgraph Radar Process
        B1(Radar Data Capture)
        B1 -->|Sends to| Q2[radar_data_queue]
    end

    subgraph Main Processing Loop
        Q1 -->|Pulls Data| P1[Check image_data_queue]
        Q2 -->|Pulls Data| P2[Check radar_data_queue]
        
        P1 -->|Check timestamps within 0.3s| D1(Within 0.3s?)
        P2 -->|Check timestamps within 0.3s| D2(Within 0.3s?)
        
        D1 -->|Yes| I1[Process Image Data]
        D2 -->|Yes| R1[Process Radar Data]
        
        D1 -->|No| I2[Buffer Image Data for Next Loop]
        D2 -->|No| R2[Buffer Radar Data for Next Loop]
        
        I1 --> M1[Process Detections, Indivually or Concatenated]
        R1 --> M1

        M1 -->|Pass Detections| T1[Update Current Tracks]
        
        I2 -->|Use buffered data in next loop| P1
        R2 -->|Use buffered data in next loop| P2
    end
```
