import yaml
import os

class TrackingConfiguration:
    """
    A class to handle loading and accessing tracking configuration settings.
    The class checks for the existence of a YAML configuration file and
    loads the settings. If the file is missing, default settings are applied.

    Attributes:
        config_path (str): The file path to the tracking YAML configuration file.
        activeFilter (str): The currently active filter.
        filters (dict): The filter configuration for various tracking algorithms.
    """

    def __init__(self, config_path="/configuration/TrackingConfig.yaml"):
        """
        Initializes the TrackingConfiguration instance by checking if the configuration file exists.
        If the file exists, it loads the configuration settings from it.
        Otherwise, it assigns default values.

        Args:
            config_path (str): The path to the tracking YAML configuration file.
        """
        self.config_path = config_path  # Path to the tracking configuration file
        self.max_track_distance = 200 # Maximum distance in meters to track an object
        
        # Default values if the YAML file is not found
        self.defaults = {
            'activeFilter': 'gmPHD',
            'filters': {
                'gmPHD': {
                    'birthCovariance': 5,
                    'expectedVelocity': 1,
                    'noiseCovarianceDistance': 1,
                    'defaultCovarianceDistance': 1,
                    'defaultConvarianceVelocity': 0.3,
                    'probabilityOfDetection': 0.8,
                    'probabilityOfDeath': 0.01,
                    'clusterRate': 7.0,
                    'mergeThreshold': 5,
                    'pruneThreshold': 1E-8,
                    'stateThreshold': 0.25
                }
            },
            'minDetectionsToCluster': 1,
            'maxDistanceBetweenClusteredObjectsM': 2,
            'trackTailLength': 0.1,
            'maxTrackQueueSize': 200,
            'showTrackingPlot': False,
            'saveTrackingResults': False,
            'outputDirectory': '/output'
        }

        # Load the configuration
        self.load_config()

    def load_config(self):
        """
        Loads the tracking configuration from the YAML file if it exists. If the file doesn't exist,
        it applies the default settings. The configuration values are set as attributes
        of the class instance to allow easy access using the active filter.
        """
        # Check if the YAML file exists
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as file:
                try:
                    # Load the YAML content
                    config = yaml.safe_load(file)
                    
                    # Load active filter and filters
                    self.activeFilter = config.get('activeFilter', self.defaults['activeFilter'])
                    self.filters = config.get('filters', self.defaults['filters'])
                    
                    # Load additional settings
                    self.minDetectionsToCluster = config.get('minDetectionsToCluster', self.defaults['minDetectionsToCluster'])
                    self.maxDistanceBetweenClusteredObjectsM = config.get('maxDistanceBetweenClusteredObjectsM', self.defaults['maxDistanceBetweenClusteredObjectsM'])
                    self.trackTailLength = config.get('trackTailLength', self.defaults['trackTailLength'])
                    self.maxTrackQueueSize = config.get('maxTrackQueueSize', self.defaults['maxTrackQueueSize'])
                    self.showTrackingPlot = config.get('showTrackingPlot', self.defaults['showTrackingPlot'])
                    self.saveTrackingResults = config.get('saveTrackingResults', self.defaults['saveTrackingResults'])
                    self.trackingOutputPath = config.get('outputDirectory', self.defaults['outputDirectory'])
                    
                    # Set the active filter's settings as attributes of this instance
                    self.set_active_filter_attributes()
                    
                except yaml.YAMLError as exc:
                    print(f"Error reading YAML file: {exc}")
                    self.apply_defaults()
        else:
            print(f"Tracking configuration file not found. Using default settings.")
            self.apply_defaults()

    def apply_defaults(self):
        """
        Apply the default settings if the configuration file is not found or cannot be read.
        """
        self.activeFilter = self.defaults['activeFilter']
        self.filters = self.defaults['filters']
        self.minDetectionsToCluster = self.defaults['minDetectionsToCluster']
        self.maxDistanceBetweenClusteredObjectsM = self.defaults['maxDistanceBetweenClusteredObjectsM']
        self.trackTailLength = self.defaults['trackTailLength']
        self.maxTrackQueueSize = self.defaults['maxTrackQueueSize']
        self.showTrackingPlot = self.defaults['showTrackingPlot']
        self.saveTrackingResults = self.defaults['saveTrackingResults']
        self.trackingOutputPath = self.defaults['outputDirectory']
        
        # Set the active filter's settings as attributes of this instance
        self.set_active_filter_attributes()

    def set_active_filter_attributes(self):
        """
        Dynamically set the attributes of the active filter onto the instance.
        This allows accessing the active filter's settings via dot notation.
        """
        active_filter_settings = self.filters.get(self.activeFilter, {})
        for key, value in active_filter_settings.items():
            setattr(self, key, value)

    def __str__(self):
        """
        Returns a string representation of the tracking configuration.
        This is useful for debugging or inspecting the configuration.

        Returns:
            str: A formatted string displaying all configuration settings.
        """
        active_filter_settings = self.filters.get(self.activeFilter, {})
        filter_str = '\n'.join(f'{key}: {value}' for key, value in active_filter_settings.items())
        
        return f"TrackingConfiguration (Active Filter: {self.activeFilter}):\n" \
               f"{filter_str}\n" \
               f"minDetectionsToCluster: {self.minDetectionsToCluster}\n" \
               f"maxDistanceBetweenClusteredObjectsM: {self.maxDistanceBetweenClusteredObjectsM}\n" \
               f"trackTailLength: {self.trackTailLength}\n" \
               f"maxTrackQueueSize: {self.maxTrackQueueSize}\n" \
                f"showTrackingPlot: {self.showTrackingPlot}\n" \
                f"outputDirectory: {self.trackingOutputPath}"

if __name__ == "__main__":
    tracking_config = TrackingConfiguration()
    print(tracking_config)

    # Access individual settings using dot notation
    print(tracking_config.birthCovariance)  # Outputs: 5
    print(tracking_config.expectedVelocity)  # Outputs: 1
