from .CFARParams import CFARParams
from .CFARType import CfarType
from .RunType import RunDataFormat, RunType

class RadarRunParams():
    """
    Parameters to run the radar system
    """
    def __init__(self, args, cfar_params: CFARParams):
        # Default run parameters
        self.runType = RunType.LIVE                        
        self.recordedDataFolder= None
        self.recordedProcessingDelaySec = 0
        self.recordedDataFormat = RunDataFormat.FD_CUSTOM
        self.ramp_type = "UP-Ramp"
        self.cfar_params = cfar_params
        self.run_velocity_measurements = False
        
        # Run validation of settings, exit if they are invalid
        self.run_validation(args)
        
        # Modify default setup based on the command line arguments
        self.modify_params_using_cmd_args(args)

        # The minimum amount of data that must be kept in memory to window on
        if(self.cfar_params.cfar_type == CfarType.LEADING_EDGE):
            self.data_window_size = cfar_params.num_guard + cfar_params.num_train + 1 + 1 # 1 more to have 1 extra
        else:
            self.data_window_size = (2*cfar_params.num_guard) + (2*cfar_params.num_train) + 1 + 1 # 1 more to have 1 extra
        
        # Print details for the user
        if (self.runType == RunType.LIVE_RECORD):
          print("Data will be recorded.")


    def modify_params_using_cmd_args(self, args):
        if not args.skip_radar and not args.skip_video:
            exit("Both radar and video tracking cannot be skipped. Please choose one to run.")
        
        if args.radar_from_file:
            self.runType = RunType.RERUN
            self.recordedDataFormat = RunDataFormat.SENTOOL_FD
        
        if args.radar_source:
            self.recordedDataFolder = args.radar_source

  
    def run_validation(self, args):
        if not args.skip_radar and not args.skip_video:
            exit("Both radar and video tracking cannot be skipped. Please choose one to run.")
        
        if(self.recordedDataFormat == RunDataFormat.SENTOOL_FD and not self.runType == RunType.RERUN):
            exit("You cannot use the SENTOOL_FD format for a live data run, since this program cannot record data in that format.")
        