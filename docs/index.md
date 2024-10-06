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
        subgraph radarProc["**Radar_process.py**"]
            style desc1 text-align:left
            desc1["`1 Collect Data
            2 Data Processing
            3 Put detection into Queue`"]
        end

        %%  Image Processing SubGraph
        subgraph imageProc["`**Image_process.py**`"]
            style desc2 text-align:left
            desc2["`1 Collect Image
            2 Data Processing
            3 Put detection into Queue`"]
        end
        Queue[["MP Queue"]]
        subgraph trackProc["`**Object_tracking.py**`"]
            style desc3 text-align:left
            desc3["`1 Collect Image
            2 Data Processing
            3 Put detection into Queue`"]
        end
    end
    Radar["fa:fa-satellite-dish"]:::bigNode
    Video["fa:fa-camera"]:::bigNode

    Radar <--> radarProc
    Video <--> imageProc
    radarProc --> Queue
    imageProc --> Queue
    Queue -- Data read from Queue --> trackProc
```

