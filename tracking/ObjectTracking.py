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
from stonesoup.tracker.simple import MultiTargetTracker
# Initiator and deleter
from stonesoup.deleter.time import UpdateTimeStepsDeleter
from stonesoup.initiator.simple import MultiMeasurementInitiator

# data associator
from stonesoup.dataassociator.neighbour import GlobalNearestNeighbour
from stonesoup.hypothesiser.distance import DistanceHypothesiser
from stonesoup.measures import Mahalanobis

# Used for clustering
from sklearn.cluster import DBSCAN

# plotting
from stonesoup.plotter import AnimatedPlotterly
from datetime import datetime, timedelta

class ObjectTrackingExtendedObjectGNN():
    """
    capacity: maximum number of track iterations to store 
    """
    def __init__(self, start_time, capacity: int=1000, expected_velocity: float=1, path_min_points: int=5, path_points_to_deletion: int=5):
    
        self.default_cov = [5, 0.5, 5, 0.5]
        self.path_min_points = path_min_points
        self.transition_model = CombinedLinearGaussianTransitionModel([ConstantVelocity(expected_velocity),
                                                                       ConstantVelocity(expected_velocity)])
        
        # Predictor and Updater
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
        # self.detection_set = set()
        
        self.centroid_detections = []
        
    def update_tracks(self, detections: np.ndarray, timestamp: datetime):
        """
        detections: Nx4 array of detections, where N is the number of detections
        the 4 columns are [x, x_vel, y, y_vel]
        timestamp: timestamp of the detections
        """
        # Add "state" for the detections, give them a valid timestamp
        measurements = []
        measurement_set = set()
        detection_set = set()
        
        for detection in detections: # detctions==scans in stone soup
            detection_x_y = np.array([detection[0], detection[2]])
            measurements.append(detection_x_y)
            measurement_set.add(Detection(detection_x_y, timestamp, self.measurement_model))
        
        measurements = np.array(measurements)
        
        # Find clusters in the data using DBSCAN
        # eps and min_samples need to be chosen based on your specific data distribution
        clustering = DBSCAN(eps=100, min_samples=2).fit(measurements)
        labels = clustering.labels_
        
        # Analyze cluster results
        unique_labels = set(labels)
        n_clusters = len(unique_labels) - (1 if -1 in labels else 0)
        
        # Gather centroids of clusters (average of points in each cluster)
        unique_labels = set(labels)
        centroids = np.array([measurements[labels == label].mean(axis=0) for label in unique_labels if label != -1])
        # print(centroids)
        
        # iterate over the centroids to create a new set of detections
        for idet in range(len(centroids)):
            detection_set.add(Detection(state_vector=[[centroids[idet][0]], [centroids[idet][1]]],
                                        timestamp=timestamp,
                                        measurement_model=self.measurement_model))
        
        # Store the detections and the timestamp for plotting
        self.centroid_detections.append(detection_set)
        self.timesteps.append(timestamp.replace(microsecond=0))
        
        # self.timesteps.append(timestamp.replace(microsecond=0))
        # self.all_measurements.append(measurement_set)
    
    def show_tracks_plot(self):
        # Need at least 2 time steps to plot
        if (len(self.timesteps) < self.path_min_points):
            return None
        
        # TODO - we need to make this live somehow..... 
        tracker = MultiTargetTracker(
            initiator=self.initiator,
            deleter=self.deleter,
            data_associator=self.data_associator,
            updater=self.updater,
            detector=zip(self.timesteps, self.centroid_detections))
        
        tracks = set()
        for time, current_tracks in tracker:
            tracks.update(current_tracks)
        
        track_plot = AnimatedPlotterly(self.timesteps, tail_length=0.2)
        # track_plot.plot_measurements(self.all_measurements, [0, 2])
        
        track_plot.plot_measurements(self.centroid_detections, [0, 2], marker=dict(color='red'),
                                measurements_label='Cluster centroids')
        track_plot.plot_tracks(tracks, [0, 2])
        track_plot.fig.show("browser")
        print("Done plotting.")
        
if __name__ == '__main__':
    tracking = ObjectTrackingExtendedObjectGNN(datetime.now())
    
    test1 = np.array([[1, 1, 1, 1], 
                      [2, 1, 2, 1], 
                      [3, 1, 3, 1], 
                      [3, 1, 3, 1], 
                      [4, 1, 4, 1], 
                      [4, 1, 4.1, 1],
                      [4, 1, 4.1, 1], 
                      [4.2, 1, 4.1, 1], 
                      [4.5, 1, 4.1, 1], 
                      [4.4, 1, 4.1, 1], 
                      [5, 1, 4.7, 1]])
    
    # Create some detections

        