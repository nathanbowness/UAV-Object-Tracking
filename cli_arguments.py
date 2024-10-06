import argparse

from radar.configuration.RadarConfiguration import RadarConfiguration
from radar.configuration.RunType import RunType
from video.VideoConfiguration import VideoConfiguration
from tracking.TrackingConfiguration import TrackingConfiguration

def define_argument_parser() -> argparse.ArgumentParser:
    """
    Define the argument parser for the main function. This will include all configurable options for the program.
    """
    parser = argparse.ArgumentParser(description='Object Tracking using Radar and Video')
    
    # Output folder for all the results
    parser.add_argument('--output-folder', type=str, default=None, help='output folder for all results to be saved to')
    parser.add_argument('--radar-start-delay', type=int, default=5, help='delay in seconds before starting the radar after the video processing starts')
    
    # Options for disabling parts of the program, but default video and radar tracking are enabled. Plots are not.
    parser.add_argument('--skip-video', action='store_true', help='skip video based tracking')
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
    parser.add_argument('--show-video-live ', action='store_true', help='if the live video feed should be shown, this requires a display')
    
    # Options for the tracking configuration
    parser.add_argument('--tracking-config', type=str, default='/configuration/TrackingConfig.yaml', help='tracking configuration file path')
    parser.add_argument('--show-tracking-plot', action='store_true', help='show the tracking plot on completion')
    parser.add_argument('--tracking-disable-save', action='store_true', help='disable saving the tracking data')
    
    return parser
    
def update_radar_config(config:RadarConfiguration, args:argparse.Namespace) -> RadarConfiguration:
    
    if args.output_folder is not None:
        config.output_folder = args.output_folder
    
    if args.radar_ip is not None:
        config.radar_ip = args.radar_ip
    if args.disable_record:
        config.record_data = False
    if args.radar_record_path is not None:
        config.output_path = args.radar_record_path
    if args.radar_from_file:
        config.run_type = RunType.RERUN
    if args.radar_source is not None:
        config.source_path = args.radar_source
    if args.radar_disable_print:
        config.print_settings = False
    
    return config

def update_video_config(config:VideoConfiguration, args:argparse.Namespace) -> VideoConfiguration:
    """
    Update the video configuration object with the arguments from the command line.
    """
    if args.output_folder is not None:
        config.outputDirectory = args.output_folder
    
    if args.model_weights is not None:
        config.modelWeights = args.model_weights
    if args.video_source is not None:
        config.videoSource = args.video_source
    if args.disable_save_video:
        config.saveProcessedVideo = False
    if args.show_video_live:
        config.showVideo = True
    
    return config

def update_tracking_config(config:TrackingConfiguration, args:argparse.Namespace) -> TrackingConfiguration:
    
    if args.output_folder is not None:
        config.outputDirectory = args.output_folder
    
    if args.show_tracking_plot:
        config.showTrackingPlot = True
    if args.tracking_disable_save:
        config.saveTrackingResults = False
        
    return config
