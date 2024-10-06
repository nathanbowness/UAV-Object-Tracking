
There are various options that can be passed to the `tracking.py` program when running from the cli. They are described below.

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
--radar-ip              # ip address of the radar
--disable-record        #disable recording the radar data
--radar-record-path     #path to folder to record radar data to
--radar-from-file       #use previously recorded radar data
--radar-source          #path to folder to read prerecorded radar data from. Only used if "--radar-rerun" is set
--radar-disable-print   #disable printing of radar params

# Options for the video configuration
--video-config          # video configuration file path
--model-weights         #model weights path. yolo wil attempt to download the weight if the arg is not a path
--video-source          #source of the video data, supports all yolo default options
--disable-save-video    #disable saving the video data

# Options for the tracking configuration
parser.add_argument('--tracking-config', type=str, default='/configuration/TrackingConfig.yaml', help='tracking configuration file path')
parser.add_argument('--show-tracking-plot', action='store_true', help='show the tracking plot on completion')
parser.add_argument('--tracking-disable-save', action='store_true', help='disable saving the tracking data')

```