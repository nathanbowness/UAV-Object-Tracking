import yaml
import os
from radar.configuration.CFARType import CfarType
from radar.configuration.RunType import RunType
from radar.configuration.CFARParams import CFARParams

# Radar dev kit imports
from radar.RadarDevKit.ConfigClasses import SysParams
from radar.RadarDevKit.Interfaces.Ethernet.EthernetConfig import EthernetParams
from radar.RadarDevKit.RadarModule import GetRadarModule, RadarModule

class RadarConfiguration:
    """
    A class to handle loading and accessing radar configuration settings.
    The class checks for the existence of a YAML configuration file and
    loads the settings. If the file is missing, default settings are applied.

    Attributes:
        config_path (str): The file path to the radar YAML configuration file.
        minimum_frequency_mhz (int): Minimum frequency in MHz for the radar.
        maximum_frequency_mhz (int): Maximum frequency in MHz for the radar.
        ramp_time_fmcw_chirp (int): Ramp time for FMCW chirp in ms.
        attenuation (int): Attenuation level for the radar.
        ethernet_params (EthernetParams): An instance of the EthernetParams class for radar connection parameters.
        cfar_params (CFARParams): An instance of the CFARParams class containing CFAR parameters.
        run_type (RunType): Enum value representing the type of run.
        source_path (str): The path to the folder where the data is read from.
        record_data (bool): Whether to record the data.
        output_path (str): The path to the folder where the data is recorded.
        processing_window (int): The number of results to keep in the processing window.
        print_settings (bool): Whether to print the radar settings on startup.
    """

    def __init__(self, config_path="/configuration/RadarConfig.yaml"):
        """
        Initializes the RadarConfiguration instance by checking if the configuration file exists.
        If the file exists, it loads the configuration settings from it.
        Otherwise, it assigns default values.

        Args:
            config_path (str): The path to the radar YAML configuration file.
        """
        self.config_path = config_path  # Path to the radar configuration file

        # Default values if the YAML file is not found
        self.defaults = {
            'minimumFrequencyMhz': 24000,
            'maximumFrequencyMhz': 25000,
            'rampTimeFmcwChirp': 1,
            'attenuation': 0,
            'ethernetParams': {
                'ip': "10.0.0.59",
                'port': 1024,
                'timeout': 1.0
            },
            'cfarParams': {
                'numGuard': 2,
                'numTrain': 5,
                'threshold': 10.0,
                'cfarType': 'CASO'
            },
            'run': 'LIVE',
            'sourcePath': '/data/radar/',
            'recordData': True,
            'recordDataPath': '/output',
            'processingWindow': 200,
            'printSettings': True
        }

        # Ethernet connection parameters
        self.ethernet_params = EthernetParams()

        # Load the configuration
        self.load_config()

    def load_config(self):
        """
        Loads the radar configuration from the YAML file if it exists. If the file doesn't exist,
        it applies the default settings. The configuration values are set as attributes
        of the class instance.
        """
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as file:
                try:
                    config = yaml.safe_load(file)

                    # Load signal and connection configuration
                    self.minimum_frequency_mhz = config.get('minimumFrequencyMhz', self.defaults['minimumFrequencyMhz'])
                    self.maximum_frequency_mhz = config.get('maximumFrequencyMhz', self.defaults['maximumFrequencyMhz'])
                    self.ramp_time_fmcw_chirp = config.get('rampTimeFmcwChirp', self.defaults['rampTimeFmcwChirp'])
                    self.attenuation = config.get('attenuation', self.defaults['attenuation'])

                    # Load Ethernet parameters
                    ethernet_params = config.get('ethernetParams', self.defaults['ethernetParams'])
                    self.ethernet_params.ip = ethernet_params.get('ip', self.defaults['ethernetParams']['ip'])
                    self.ethernet_params.port = ethernet_params.get('port', self.defaults['ethernetParams']['port'])
                    self.ethernet_params.timeout = ethernet_params.get('timeout', self.defaults['ethernetParams']['timeout'])

                    # CFAR parameters
                    cfar_params = config.get('cfarParams', self.defaults['cfarParams'])
                    self.cfar_params = CFARParams(
                        num_guard=cfar_params.get('numGuard', self.defaults['cfarParams']['numGuard']),
                        num_train=cfar_params.get('numTrain', self.defaults['cfarParams']['numTrain']),
                        threshold=cfar_params.get('threshold', self.defaults['cfarParams']['threshold']),
                    )
                    cfar_type_str = cfar_params.get('cfarType', self.defaults['cfarParams']['cfarType'])
                    self.cfar_params.cfar_type = CfarType[cfar_type_str] if cfar_type_str in CfarType.__members__ else CfarType.CASO
                    
                    # Run configuration
                    run_type_str = config.get('run', self.defaults['run'])
                    self.source_path = config.get('sourcePath', self.defaults['sourcePath'])
                    self.run_type = RunType[run_type_str] if run_type_str in RunType.__members__ else RunType.LIVE
                    self.record_data = config.get('recordData', self.defaults['recordData'])
                    self.output_path = config.get('recordDataPath', self.defaults['recordDataPath'])
                    self.processing_window = config.get('processingWindow', self.defaults['processingWindow'])

                    # Print settings
                    self.print_settings = config.get('printSettings', self.defaults['printSettings'])

                except yaml.YAMLError as exc:
                    print(f"Error reading YAML file: {exc}.")
                    print('Will use default values.')
                    self.apply_defaults()
        else:
            print(f"Radar configuration file '{self.config_path}' not found. Using default settings.")
            self.apply_defaults()

        # Print settings if enabled
        if self.print_settings:
            print(self)

    def apply_defaults(self):
        """
        Apply the default settings if the configuration file is not found or cannot be read.
        """
        self.minimum_frequency_mhz = self.defaults['minimumFrequencyMhz']
        self.maximum_frequency_mhz = self.defaults['maximumFrequencyMhz']
        self.ramp_time_fmcw_chirp = self.defaults['rampTimeFmcwChirp']
        self.attenuation = self.defaults['attenuation']

        # Apply Ethernet parameters from defaults
        self.ethernet_params.ip = self.defaults['ethernetParams']['ip']
        self.ethernet_params.port = self.defaults['ethernetParams']['port']
        self.ethernet_params.timeout = self.defaults['ethernetParams']['timeout']

        # Apply CFAR parameters from defaults
        self.cfar_params = CFARParams(
            num_guard=self.defaults['cfarParams']['numGuard'],
            num_train=self.defaults['cfarParams']['numTrain'],
            threshold=self.defaults['cfarParams']['threshold'],
        )
        self.cfar_params.cfar_type = CfarType[self.defaults['cfarParams']['cfarType']]

        # Run configuration
        self.run_type = RunType[self.defaults['run']]
        self.source_path = self.defaults['sourcePath']
        self.record_data = self.defaults['recordData']
        self.output_path = self.defaults['recordDataPath']
        self.processing_window = self.defaults['processingWindow']

        # Print settings flag
        self.print_settings = self.defaults['printSettings']
        
    def connect_get_radar_module(self) -> RadarModule:
        """
        Connect and get to the radar module instance with the current configuration settings.
        """
        updatedSysParmas = SysParams()
        updatedSysParmas.minFreq = self.minimum_frequency_mhz
        updatedSysParmas.manualBW = self.maximum_frequency_mhz - self.minimum_frequency_mhz
        updatedSysParmas.t_ramp = self.ramp_time_fmcw_chirp
        updatedSysParmas.atten = self.attenuation
        updatedSysParmas.active_RX_ch = 15
        updatedSysParmas.freq_points = 512
        # Not using FFT_data, but configure it incase it's used in the future
        updatedSysParmas.FFT_data_type = 1
        
        return GetRadarModule(updatedRadarParams=updatedSysParmas,
                              updatedEthernetConfig=self.ethernet_params, 
                              printSettings=self.print_settings)

    def __str__(self):
        """
        Returns a string representation of the radar configuration.
        """
        return (f"RadarConfiguration:\n"
                f"minimumFrequencyMhz: {self.minimum_frequency_mhz}\n"
                f"maximumFrequencyMhz: {self.maximum_frequency_mhz}\n"
                f"rampTimeFmcwChirp: {self.ramp_time_fmcw_chirp}\n"
                f"attenuation: {self.attenuation}\n"
                f"Ethernet Params:\n"
                f"  {self.ethernet_params}\n"
                f"CFAR Params:\n"
                f"  {self.cfar_params}\n"
                f"Run Type: {self.run_type}\n"
                f"Source Data Path: {self.source_path}\n"
                f"Record Data: {self.record_data}\n"
                f"Record Data Path: {self.output_path}\n"
                f"Processing Window: {self.processing_window}\n"
                f"Print Settings: {self.print_settings}")

# Example usage:
if __name__ == "__main__":
    radar_config = RadarConfiguration("RadarConfiguration.yaml")
