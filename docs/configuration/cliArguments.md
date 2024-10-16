## CLI Arguments for Tracking.py

By default, the Tracking.py program will use the options that are passed through the configuration files. See [Configuration](./configuration.md) for more details.

However, for further customizations the there are various options that can be passed to the `tracking.py` program when running from the cli.
The arguments passed through the CLI will take priority over the configuration files. 

A full list can be seen by running `python3 tracking.py --help` from an environment with python and this project cloned. All options are also described below.

``` bash
--output-folder,        # Output folder for all results to be saved to 
--radar-start-delay     # Delay in seconds before starting the radar after the video processing starts

# Options for disabling parts of the program, but default video and radar tracking are enabled. Plots are not.
--skip-video           # skip video based tracking
--skip-radar           # skip radar based tracking
--skip-tracking        # skip tracking algorithm and path determination
--enable-plot          # enable plotting

# Options for the radar configuration
--radar-config          #radar configuration file path
--radar-ip              # ip address of the radar, DEFAULT - 192.168.0.2
--disable-record        # option to disable recording the radar data
--radar-record-path     # path to folder to record radar data to, DEFAULT - /output
--radar-from-file       # use previously recorded radar data
--radar-source          # path to folder to read prerecorded radar data from. Only used if "--radar-rerun" is set
--radar-disable-print   # disable printing of radar params

# Options for the video configuration
--video-config          # video configuration file path
--model-weights         #model weights path. yolo wil attempt to download the weight if the arg is not a path
--video-source          #source of the video data, supports all yolo default options
--disable-save-video    #disable saving the video data
--show-live-video       # if a live-feed of the video should be shown while running 

# Options for the tracking configuration
--tracking-config       # tracking configuration file path, DEFAULT - /configuration/TrackingConfig.yaml
--show-tracking-plot    # show the tracking plot on completion
--tracking-disable-save # disable saving the tracking data
--batching-time         # time to accumulate detections before sending to tracking algorithm - default 0.3 seconds
```