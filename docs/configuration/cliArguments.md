
There are various options that can be passed to the `tracking.py` program when running from the cli. They are described below.

``` bash
--output-folder,        # Output folder for all results to be saved to 
--radar-start-delay     # Delay in seconds before starting the radar after the video processing starts

# Options for disabling parts of the program, but default video and radar tracking are enabled. Plots are not.
--skip-video           # skip video based tracking
parser.add_argument('--skip-radar', action='store_true', help='skip radar based tracking')
parser.add_argument('--skip-tracking', action='store_true', help='skip tracking algorithm and path determination')
parser.add_argument('--enable-plot', action='store_true', help='enable plotting')

# Options for the radar configuration
parser.add_argument('--radar-config', type=str, default='/configuration/RadarConfig.yaml', help='radar configuration file path')
parser.add_argument('--radar-ip', type=str, default=None, help='ip address of the radar')
parser.add_argument('--disable-record', action='store_true', help='disable recording the radar data')
parser.add_argument('--radar-record-path', type=str, default=None, help='path to folder to record radar data to')
parser.add_argument('--radar-from-file', action='store_true', help='use previously recorded radar data')
parser.add_argument('--radar-source', type=str, default=None, help='path to folder to read prerecorded radar data from. Only used if "--radar-rerun" is set')
parser.add_argument('--radar-disable-print', action='store_true', help='disable printing of radar params')

# Options for the video configuration
parser.add_argument('--video-config', type=str, default='/configuration/VideoConfig.yaml', help='video configuration file path')
parser.add_argument('--model-weights', type=str, default=None, help='model weights path. yolo wil attempt to download the weight if the arg is not a path')
parser.add_argument('--video-source', type=str, default=None, help='source of the video data, supports all yolo default options')
parser.add_argument('--disable-save-video', action='store_true', help='disable saving the video data')

# Options for the tracking configuration
parser.add_argument('--tracking-config', type=str, default='/configuration/TrackingConfig.yaml', help='tracking configuration file path')
parser.add_argument('--show-tracking-plot', action='store_true', help='show the tracking plot on completion')
parser.add_argument('--tracking-disable-save', action='store_true', help='disable saving the tracking data')

```