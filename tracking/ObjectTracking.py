from concurrent.futures import thread
import numpy as np

import plotly.io as pio
pio.renderers.default = 'browser'

from stonesoup.models.transition.linear import CombinedLinearGaussianTransitionModel, \
    ConstantVelocity
from stonesoup.models.measurement.linear import LinearGaussian
from stonesoup.types.state import GaussianState, State
from stonesoup.types.detection import Detection, Clutter
from stonesoup.predictor.kalman import ExtendedKalmanPredictor
from stonesoup.updater.kalman import ExtendedKalmanUpdater

# Initiator and deleter
from stonesoup.deleter.time import UpdateTimeStepsDeleter
from stonesoup.initiator.simple import MultiMeasurementInitiator

# data associator
from stonesoup.dataassociator.neighbour import GlobalNearestNeighbour
from stonesoup.hypothesiser.distance import DistanceHypothesiser
from stonesoup.measures import Mahalanobis

# plotting
from stonesoup.plotter import AnimatedPlotterly
from datetime import datetime, timedelta

class ObjectTrackingExtendedObjectGNN():
    """
    capacity: maximum number of track iterations to store 
    """
    def __init__(self, start_time, capacity: int=1000, expected_velocity: float=1, path_min_points: int=7, path_points_to_deletion: int=5):
    
        self.default_cov = [5, 0.5, 5, 0.5]
        self.transition_model = CombinedLinearGaussianTransitionModel([ConstantVelocity(expected_velocity),
                                                          ConstantVelocity(expected_velocity)])
        
        self.predictor = ExtendedKalmanPredictor(self.transition_model)
        self.measurement_model = LinearGaussian(ndim_state=4,
                                   mapping=(0, 2),
                                   noise_covar=np.diag([25, 25]))
        self.updater = ExtendedKalmanUpdater(self.measurement_model)
        
        # Deleter
        self.deleter = UpdateTimeStepsDeleter(path_points_to_deletion)
        
        # Hypothesiser
        self.hypothesiser = DistanceHypothesiser(
            predictor=self.predictor,
            updater=self.updater,
            measure=Mahalanobis(),
            missed_distance=10)

        # Data associator
        self.data_associator = GlobalNearestNeighbour(self.hypothesiser)

        # Initiator
        self.initiator = MultiMeasurementInitiator(
            prior_state=GaussianState(np.array([0, 0, 0, 0]),
                                    np.diag([10, 0.5, 10, 0.5]) ** 2,
                                    timestamp=start_time),
            measurement_model=None,
            deleter=self.deleter,
            data_associator=self.data_associator,
            updater=self.updater,
            min_points=path_min_points)
        
        # Measurements stored over time
        # TODO - switch this to a deque eventually, with a set size!
        self.timesteps = []
        self.all_measurements = []
        
    def update_tracks(self, detections: np.ndarray, timestamp: datetime):
        """
        detections: Nx4 array of detections, where N is the number of detections
        the 4 columns are [x, x_vel, y, y_vel]
        timestamp: timestamp of the detections
        """
        # Add "state" for the detections, give them a valid timestamp
        measurement_set = set()
        for detection in detections:
            detection_x_y = np.array([detection[0], detection[2]])
            measurement_set.add(Detection(detection_x_y, timestamp, self.measurement_model))
        
        self.timesteps.append(timestamp.replace(microsecond=0))
        self.all_measurements.append(measurement_set)
    
    def show_tracks_plot(self):
        # Need at least 2 time steps to plot
        if (len(self.timesteps) < 2):
            return None
        
        # TODO - remove this, just done for now so we don't show a plot constantly
        if (len(self.timesteps) < 60):
            return None
        
        track_plot = AnimatedPlotterly(self.timesteps, tail_length=0.2)
        track_plot.plot_measurements(self.all_measurements, [0, 2])
        track_plot.fig.show("browser")
        print("Done plotting.")
        