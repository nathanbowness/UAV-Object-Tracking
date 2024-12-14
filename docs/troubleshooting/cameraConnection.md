# Investigating Camera Connectivity
Some instructions to investigate the connectivity issues with an attached camera in the docker container.

## Startup Container With Following Commands:
Startup the container, with the device mounted and the output folder mounted to look at output data. This assumes the image is called `tracking-image`, and the camera is attached to `/dev/video0`:
=== "Linux"

    ``` bash
    docker run -it -v "$(pwd)/output:/output" --device=/dev/video0:/dev/video0 tracking-image 
    ```

=== "Jetson5"

    ``` bash
    docker run --ipc=host --runtime=nvidia -it -v "$(pwd)/output:/output" --device=/dev/video0:/dev/video0 tracking-image
    ```

### Making Changes Then Rebuilding
You can rebuild the container in between with these commands:
=== "Linux"

    ``` bash
    docker build . -t tracking-image:latest
    ```

=== "Jetson5"

    ``` bash
    docker build . -f Dockerfile-jetson-jetpack5 tracking-image:latest
    ```

## 1 - Check If Container Works with Youtube Stream
First let's check the video processing works with a youtube stream. This will ensure that python code is working, and that the issue is with the local camera connection.
The following command will skip radar processing as well, just to eliminate that factor as well.
```
python3 tracking.py --skip-radar --skip-tracking --video-source "https://youtu.be/LNwODJXcvt4"
```

You should see processing output like this:
```
1/1: https://youtu.be/LNwODJXcvt4... Success ✅ (10842 frames of shape 1920x1080 at 30.00 FPS)

0: 384x640 1 person, 1 potted plant, 53.0ms
0: 384x640 1 person, 1 potted plant, 16.8ms
0: 384x640 1 person, 1 potted plant, 26.1ms
0: 384x640 1 person, 1 potted plant, 25.0ms
0: 384x640 1 person, 1 potted plant, 16.1ms
0: 384x640 1 person, 1 potted plant, 18.6ms
0: 384x640 1 person, 1 potted plant, 20.2ms
0: 384x640 1 person, 1 chair, 1 potted plant, 22.2ms
0: 384x640 1 person, 1 chair, 1 potted plant, 17.4ms
0: 384x640 1 person, 1 chair, 1 potted plant, 18.0ms
0: 384x640 1 person, 1 chair, 1 potted plant, 20.8ms
```

## 2 - Verify Device Access With FFMPEG
Install and use FFMPEG inside the container as an initial check to ensure the camera is mounted properly. This output will be saved in the output folder assuming it's mounted to the container.
```
# Commands for running ffmpeg, install then capture frames
apt-get install ffmpeg

ffmpeg -f v4l2 -framerate 1 -video_size 640x480 -i /dev/video0 -vframes 1 /output/output_image.jpg
```

If that works, you should be able to see an image in the output folder.

## 3 - Check If Yolo Works With the Device Through CLI
Try to run the following command:
```
yolo detect predict model=yolov8n.pt source=0
```

This will use the yolo cli to do a simple prediction.
NOTE: Latest version of yolo only need the integer of the video source, not the entire video.

## 4 - Try Removing Stream For Local Cameras
In the VideoConfiguration, change the videoStream to off and try again. This is unlikely to fix the issue, but worth trying.

* Edit the config file in the pod, you can also mount a configuration directory to make this quicker.
```
# Install some text editor (nano, vi, etc)
agt-get install nano
nano /configuration/VideoConfiguration.yaml
```

* Change the "videoStream" to False, the following setting:
```
# Configuration for the Yolo Processing
...
iouThreshold: 0.5
videoStream: False # CHANGE THIS TO FALSE
...
```

Run the tracking program:
```
python3 tracking.py --skip-radar --skip-tracking --video-source "0"
```

## Other Alternatives
There is a reported issue with using arducam's with the Orin Nano boards:

- [Ultralytics Github Issue - Using Arducam (with gstreamer) and YoloV8](https://github.com/ultralytics/ultralytics/issues/14848)

There are some discussions there about using Nvidia-OpenCV rather than OpenCV that Ultralytics Yolo uses by default.
If there are issues with using yolo with the Arducam, but it can be used with ffmpeg that switch may be needed.