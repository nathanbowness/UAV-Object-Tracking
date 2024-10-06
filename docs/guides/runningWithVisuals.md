# Running the Container with Visuals

These options should let you run the container with visuals enabled, meaning you can see the Yolo results live. As well on completion, the stone-soup graph can be shown to the user. Assuming they have a browser enabled.

1.  Run the Container Interactively

    To run the container interactively with visuals, you will need these additional options added to the normal run command.
    
    **Note:** This has only be tested on linux, there may be different arguments needed for Jetson.
    ``` bash
    xhost +local:docker && docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -it tracking-image
    ```

2. Run the tracking program, with video processing and radar tracking disabled.
```bash
python3 tracking.py --show-tracking-plot -show-video-live
```