import yaml
import os

from video.CameraDetails import CameraDetails

class VideoConfiguration:
    """
    A class to handle loading and accessing video configuration settings.
    The class checks for the existence of YAML configuration files and
    loads the settings. If the files are missing, default settings are applied.

    Attributes:
        config_path (str): The file path to the main YAML configuration file.
        bb_coefficients_path (str): The file path to the BB Coefficients YAML file.
        defaults (dict): The default video configuration values.
        bb_defaults (dict): The default BB Coefficients.
    """

    def __init__(self, config_path="/configuration/VideoConfig.yaml", bb_coefficients_path="/configuration/BBCoefficients.yaml"):
        """
        Initializes the VideoConfiguration instance by checking if the configuration files exist.
        If the files exist, it loads the configuration settings from them.
        Otherwise, it assigns default values.

        Args:
            config_path (str): The path to the main YAML configuration file.
            bb_coefficients_path (str): The path to the BB Coefficients YAML file.
        """
        self.config_path = config_path  # Path to the video configuration file
        self.bb_coefficients_path = bb_coefficients_path  # Path to the BB Coefficients file
        
        # Default configuration values if the YAML file is not found
        self.defaults = {
            'modelWeights': "yolov8n.pt",
            'saveRawImages': False,
            'saveProcessedVideo': True,
            'outputDirectory': "/output",
            'videoSource': "",
            'confidenceThreshold': 0.3,
            'iouThreshold': 0.5,
            'videoStream': True,
            'showBoxesInVideo': True,
            'showVideo': False,
            'cameraHorizontalFOV': 90,
            'cameraZoomFactor': 1.0,
            'imageWidth': 1920,
            'imageHeight': 1080
        }

        # Default BB Coefficients if the YAML file is not found
        self.bb_defaults = {
            'dog': 0.5,
            'person': 0.5,
            'car': 0.5,
            'truck': 0.5
        }

        # Load the configuration and bb coefficients
        self.load_config()
        self.load_bb_coefficients()
        
        # Camera and Image characteristics
        self.camera_details = CameraDetails(self.bbCoefficients, self.cameraHorizontalFOV, self.cameraZoomFactor, self.imageWidth, self.imageHeight)

    def load_config(self):
        """
        Loads the configuration from the YAML file if it exists. If the file doesn't exist,
        it applies the default settings. The configuration values are set as attributes
        of the class instance to allow easy access using dot notation.

        This method reads the main video configuration YAML file and assigns values
        to the corresponding attributes. If a value is missing in the file, it will be
        replaced by a default value.
        """
        # Check if the YAML file exists
        if os.path.exists(self.config_path):
            # If file exists, attempt to open and read it
            with open(self.config_path, 'r') as file:
                try:
                    # Load the YAML content
                    config = yaml.safe_load(file)
                    # Ensure any missing values in the config are replaced by defaults
                    config = {key: config.get(key, default_value) for key, default_value in self.defaults.items()}
                except yaml.YAMLError as exc:
                    print(f"Error reading YAML file: {exc}")
                    config = self.defaults
        else:
            print(f"Video Config file not found. Using default configuration.")
            config = self.defaults

        # Set each configuration key-value pair as an instance attribute
        for key, value in config.items():
            setattr(self, key, value)

    def load_bb_coefficients(self):
        """
        Loads the bounding box (BB) coefficients from a YAML file if it exists.
        If the file doesn't exist, it applies default BB coefficients. The BB coefficients
        are used to determine the distance of an object based on the pixel width of the
        bounding box.

        This method reads the BB Coefficients YAML file and assigns values
        to the corresponding attributes. If a value is missing in the file, it will be
        replaced by a default value.
        """
        # Check if the BB Coefficients YAML file exists
        if os.path.exists(self.bb_coefficients_path):
            # If file exists, attempt to open and read it
            with open(self.bb_coefficients_path, 'r') as file:
                try:
                    # Load the YAML content for BB Coefficients
                    bb_config = yaml.safe_load(file)
                    self.bbCoefficients = bb_config.get('bbCoefficients', self.bb_defaults)
                except yaml.YAMLError as exc:
                    print(f"Error reading BB Coefficients YAML file: {exc}")
                    self.bbCoefficients = self.bb_defaults
        else:
            print(f"BB Coefficients Configuration file not found. Using default coefficients.")
            self.bbCoefficients = self.bb_defaults

    def __str__(self):
        """
        Returns a string representation of the video configuration and BB coefficients.
        This is useful for debugging or inspecting the configuration.

        Returns:
            str: A formatted string displaying all configuration settings and BB coefficients.
        """
        # Generate a string with each configuration attribute and its value
        config_str = '\n'.join(f'{key}: {getattr(self, key)}' for key in self.defaults)
        # Add BB Coefficients to the string
        bb_str = '\n'.join(f'{key}: {value}' for key, value in self.bbCoefficients.items())
        return f"VideoConfiguration:\n{config_str}\n\nBBCoefficients:\n{bb_str}"

if __name__ == "__main__":
    # Usage example
    video_config = VideoConfiguration()
    print(video_config)

    # Access individual settings
    print(video_config.modelWeights)
    print(video_config.bbCoefficients)  # Access the BB Coefficients map
