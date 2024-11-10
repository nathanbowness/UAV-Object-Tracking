from concurrent.futures import thread
import os
from typing import List
import numpy as np

import plotly.io as pio

from tracking.DetectionsAtTime import DetectionDetails
pio.renderers.default = 'browser'

from stonesoup.models.transition.linear import CombinedLinearGaussianTransitionModel, \
    ConstantVelocity
from stonesoup.models.measurement.linear import LinearGaussian
from stonesoup.types.detection import Detection

# data associator
from stonesoup.hypothesiser.distance import DistanceHypothesiser
from stonesoup.measures import Mahalanobis

from stonesoup.predictor.kalman import KalmanPredictor
from stonesoup.updater.pointprocess import PHDUpdater

# Used for clustering
from sklearn.cluster import DBSCAN

# plotting
from stonesoup.plotter import AnimatedPlotterly
from datetime import datetime, timedelta

from stonesoup.mixturereducer.gaussianmixture import GaussianMixtureReducer

from stonesoup.measures import Mahalanobis
from stonesoup.hypothesiser.gaussianmixture import GaussianMixtureHypothesiser
from stonesoup.updater.kalman import KalmanUpdater

from stonesoup.types.state import TaggedWeightedGaussianState
from stonesoup.types.track import Track
from stonesoup.types.array import CovarianceMatrix

from collections import deque 

from tracking.TrackingConfiguration import TrackingConfiguration

import pandas as pd

def get_object_tracking_gm_phd(start_time, tracking_config: TrackingConfiguration):
    """
    Get the object tracking GM PHD filter based on the tracking configuration.
    
    Args:
        start_time (datetime): The start time of the tracking.
        tracking_config (TrackingConfiguration): The tracking configuration.
        
    Returns:
        ObjectTrackingGmPhd: The object tracking GM PHD filter.
    """
    return ObjectTrackingGmPhd(
        start_time,
        min_detections_to_cluster=tracking_config.minDetectionsToCluster,
        cluster_distance=tracking_config.maxDistanceBetweenClusteredObjectsM,
        track_tail_length=tracking_config.trackTailLength,
        tracking_meas_area=tracking_config.max_track_distance,
        max_deque_size=tracking_config.maxTrackQueueSize,
        # Filter parameters
        birth_covar=tracking_config.birthCovariance,
        expected_velocity=tracking_config.expectedVelocity,
        noise_covar=[tracking_config.noiseCovarianceDistance, tracking_config.noiseCovarianceDistance],
        default_cov=[tracking_config.defaultCovarianceDistance, tracking_config.defaultConvarianceVelocity, 
                     tracking_config.defaultCovarianceDistance, tracking_config.defaultConvarianceVelocity],
        probability_detection=tracking_config.probabilityOfDetection,
        death_probability=tracking_config.probabilityOfDeath,
        clutter_rate=tracking_config.clusterRate,
        merge_threshold=tracking_config.mergeThreshold,
        prune_threshold=tracking_config.pruneThreshold,
        state_threshold=tracking_config.stateThreshold,
        show_plot=tracking_config.showTrackingPlot,
        # Saving tracking results
        saveTrackingResults=tracking_config.saveTrackingResults,
        outputDirectory=tracking_config.outputDirectory
    )


class ObjectTrackingGmPhd():
    """
    capacity: maximum number of track iterations to store 
    """
    def __init__(self, 
                 start_time, 
                 min_detections_to_cluster: int = 1, 
                 cluster_distance: int = 2, 
                 track_tail_length : float = 0.001,
                 tracking_meas_area : int =  150,
                 max_deque_size: int = 200,
                 birth_covar: int = 150,
                 expected_velocity: float=1,
                 noise_covar: list = [1, 1],
                 default_cov: list = [1, 0.3, 1, 0.3],
                 probability_detection: float = 0.8,
                 death_probability: float = 0.01,
                 clutter_rate: float = 7.0,
                 merge_threshold: float = 5, # Threshold Squared Mahalanobis distance
                 prune_threshold: float = 1E-8, # Threshold component weight
                 state_threshold: float = 0.25,
                 show_plot: bool = False,
                 saveTrackingResults: bool = False,
                 outputDirectory: str = "/output"
                 ):
    
        self.start_time = start_time
        self.min_detections_to_cluster = min_detections_to_cluster
        self.track_tail_length = track_tail_length
        self.cluster_distance = cluster_distance
        self.default_cov = default_cov
        self.tracking_meas_area = tracking_meas_area
        self.show_plot = show_plot
        
        self.transition_model = CombinedLinearGaussianTransitionModel([ConstantVelocity(expected_velocity),
                                                                       ConstantVelocity(expected_velocity)])
        
        self.measurement_model = LinearGaussian(ndim_state=4,
                                   mapping=(0, 2),
                                   noise_covar=np.diag(noise_covar))      
        
        # Area in which we look for target. Note that if a target appears outside of this area the
        # filter will not pick up on it.
        meas_range = np.array([[-1, 1], [-1, 1]])*tracking_meas_area
        clutter_spatial_density = clutter_rate/np.prod(np.diff(meas_range))
        
        # Predictor and Updater
        self.kalman_predictor = KalmanPredictor(self.transition_model)
        self.kalman_updater = KalmanUpdater(self.measurement_model)
        self.updater = PHDUpdater(
                    self.kalman_updater,
                    clutter_spatial_density=clutter_spatial_density,
                    prob_detection=probability_detection,
                    prob_survival=1-death_probability)
        
        # Initialise a Gaussian Mixture reducer
        self.state_threshold = state_threshold
        self.reducer = GaussianMixtureReducer(
            prune_threshold=prune_threshold,
            pruning=True,
            merge_threshold=merge_threshold,
            merging=True)
        
        # Hypothetiser
        self.base_hypothesiser = DistanceHypothesiser(self.kalman_predictor, self.kalman_updater, Mahalanobis(), missed_distance=3)
        self.hypothesiser = GaussianMixtureHypothesiser(self.base_hypothesiser, order_by_detection=True)
        
        birth_covar = CovarianceMatrix(np.diag([birth_covar, 2, birth_covar, 2]))
        self.birth_component = TaggedWeightedGaussianState(
            state_vector=[0, 0, 0, 0],
            covar=birth_covar**2,
            weight=0.25,
            tag='birth',
            timestamp=start_time
        )
        
        # GM PHD Tracker variables
        self.timesteps = deque(maxlen=max_deque_size)
        self.all_measurements = deque(maxlen=max_deque_size)
        self.tracks = set()
        self.reduced_states = set([track[-1] for track in self.tracks])
        self.all_gaussians = deque(maxlen=max_deque_size)
        self.tracks_by_time = deque(maxlen=max_deque_size)
        self.tracker_count = 0
        
        self.saveTrackingResults = saveTrackingResults
        self.save_dir = None
        
        # Create folder to save data if "saveTrackingResults" is set to True
        if self.saveTrackingResults:
            self.save_dir = os.path.join(outputDirectory, start_time.strftime('%Y-%m-%d_%H-%M-%S'), 'tracking')
            os.makedirs(self.save_dir, exist_ok=True)
        
        
    def cluster_measurements(self, detections, eps, min_samples):
        # Extract measurements (x, y) from detections
        measurements = np.array([[detection.data[0], detection.data[2]] for detection in detections])

        # Cluster the measurements using DBSCAN
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(measurements)
        labels = clustering.labels_

        # Filter out noise points and calculate centroids for each cluster
        centroids = np.array([measurements[labels == label].mean(axis=0) 
                            for label in set(labels) if label != -1])

        return centroids
        
    def update_tracks(self, detections: List[DetectionDetails], timestamp: datetime, type: str = None, print_coord: bool = False):
        """
        detections: Nx4 array of detections, where N is the number of detections
        the 4 columns are [x, x_vel, y, y_vel]
        timestamp: timestamp of the detections
        print_coord: if True, print the coordinates of the detections added to tracks
        """
        if (detections is None) or (len(detections) == 0):
            return
        
        timestamp = timestamp.replace(microsecond=0)
        
        # Get the measurements after they've been clustered
        measurements = self.cluster_measurements(detections, self.cluster_distance, self.min_detections_to_cluster)        
        detection_set = set()
        # iterate over the centroids to create a new set of detection for this time instance.
        for idet in range(len(measurements)):
            detection_set.add(Detection(state_vector=[[measurements[idet][0]], [measurements[idet][1]]],
                                        timestamp=timestamp,
                                        measurement_model=self.measurement_model))
        
        # Add the measurements and timestamps to the list
        self.timesteps.append(timestamp)
        self.all_measurements.append(detection_set)
        
        # Append empty lists to deques
        self.all_gaussians.append([])  
        self.tracks_by_time.append([])

        current_state = self.reduced_states

        if detection_set:  # TODO remove this
            time = timestamp
        else:
            time = self.start_time + timedelta(seconds=self.tracker_count)
        
        self.birth_component.timestamp = time
        current_state.add(self.birth_component)

        hypotheses = self.hypothesiser.hypothesise(current_state, detection_set, timestamp=time, order_by_detection=True)

        updated_states = self.updater.update(hypotheses)
        self.reduced_states = set(self.reducer.reduce(updated_states))

        added_detect_to_print = []

        for reduced_state in self.reduced_states:
            if reduced_state.weight > 0.05:
                self.all_gaussians[-1].append(reduced_state)  # Append to the current deque index

            tag = reduced_state.tag

            if reduced_state.weight > self.state_threshold:
                for track in self.tracks:
                    track_tags = [state.tag for state in track.states]

                    if tag in track_tags:
                        track.append(reduced_state)
                        self.tracks_by_time[-1].append(reduced_state)  # Append to the current deque index
                        x_y = self.get_tracks_x_y(reduced_state)
                        if x_y is not None:
                            added_detect_to_print.append(x_y)
                        break
                else:
                    new_track = Track(reduced_state)
                    self.tracks.add(new_track)
                    self.tracks_by_time[-1].append(reduced_state)
                    x_y = self.get_tracks_x_y(reduced_state)
                    if x_y is not None:
                        added_detect_to_print.append(x_y)
        
        self.tracker_count += 1
        
        # Print all coordinate that were added to active tracks. Points not shown here, were not associated with a track!
        if print_coord and len(added_detect_to_print) > 0:
            # Create a formatted string with all coordinates on a single line
            formatted_coords = ", ".join([f"({coord[0]:.1f}, {coord[1]:.1f})" for coord in added_detect_to_print])
            # formatted_coords = ", ".join([f"(x: {coord[0]:.1f}, y: {coord[1]:.1f})" for coord in coordinates]) # Alternative formatting with x, y labels
            print(f"Detections associated to tracks: {formatted_coords}")
    
    def get_tracks_x_y(self, state):
        """
        Get the x, y coordinates of the track to print
        """
        # Get the first and third elements of the state_vector (assuming it has at least 4 elements)
        x = state.state_vector[0, 0]
        y = state.state_vector[2, 0]
        # Append the (x, y) pair to the print_list
        if abs(x) != 0 and abs(y) != 0:
            return (x,y)
        else:
            return None
    
    def show_tracks_plot(self):
        # If the plot is not configured, return
        if not self.show_plot:
            return
        
        if (len(self.timesteps) < 5):
            return None
        
        x_min, x_max, y_min, y_max = 0, self.tracking_meas_area, -self.tracking_meas_area, self.tracking_meas_area
        
        # Plot the tracks
        plotter = AnimatedPlotterly(list(self.timesteps), tail_length=self.track_tail_length)
        plotter.plot_measurements(list(self.all_measurements), [0, 2], marker=dict(color='red'), measurements_label='Detections After Clustering')
        plotter.plot_tracks(list(self.tracks), [0, 2], uncertainty=True)
        plotter.fig.update_xaxes(range=[x_min, x_max])
        plotter.fig.update_yaxes(range=[y_min, y_max])
        
        # Save the plot to an HTML file if a save is desired
        if self.saveTrackingResults:
            fileName = "tracking_plot.html"
            plotter.fig.write_html(os.path.join(self.save_dir, fileName))
            print("Stone soup plot saved to file.")
        
        if self.show_plot:
            plotter.fig.show("browser")
            print("Done loading plot into the browser.")
    
    def find_tracks_remove_older_tracks(self, 
                                        current_time: datetime = datetime.now(),
                                        remove_tracks = False, 
                                        interval = 5):
        """
        Find current tracks within an interval, return them. 
        If remove_tracks is passed, remove older states
        :param current_time: The current time to compare states against.
        :param remove_tracks: If True, remove states from older tracks that are older than the last 'interval' seconds.
        :param interval: The time interval in seconds for filtering states.
        """
        # Define the time threshold for filtering states
        time_threshold = current_time - timedelta(seconds=interval)
        
        # Iterate through each track in the set and collect tracks to remove
        tracks_to_remove = {track for track in self.tracks if track.state.timestamp < time_threshold.replace(microsecond=0)}
        
        # Remove the entire track if all states are too old
        current_tracks = self.tracks - tracks_to_remove
        
        # Remove the states from the tracks if the flag is set
        if remove_tracks:
            self.tracks = current_tracks
        
        return current_tracks
    
    def print_current_tracks(self, 
                             current_time: datetime = None, 
                             remove_tracks = False,
                             interval : int = 5):
        """
        Print the current tracks with their coordinates.
        :param current_time: The current time to compare states against.
        :param remove_tracks: If True, remove states from older tracks that are older than the last 'interval' seconds.
        :param interval: The time interval in seconds for filtering states.
        """
        if current_time is None:
            current_time = datetime.now()
        
        current_tracks = self.find_tracks_remove_older_tracks(current_time, remove_tracks=remove_tracks, interval=interval)
        print(f"There are currently {len(current_tracks)} tracks identified in the last {interval} seconds.")
        
        coordinates = []
        # Iterate through each tracks, find the x, y coordinates to print the current tracks
        for track in current_tracks:
            # Get the first and third elements of the state_vector (assuming it has at least 4 elements)
            x_y = self.get_tracks_x_y(track.state)
            if x_y is None:
                continue
            # Append the (x, y) pair to the coordinates list
            coordinates.append(x_y)
                
       # Create a formatted string with all coordinates on a single line
        formatted_coords = []
        for coord in coordinates:
            x, y = coord
            R = np.sqrt(x**2 + y**2)
            Theta = np.degrees(np.arctan2(y, x))
            formatted_coords.append(f"(R: {R:.1f}, θ: {Theta:.1f}, X: {x:.1f}, Y: {y:.1f})")
        
        # Join the formatted coordinates into a single string
        formatted_coords_str = ", ".join(formatted_coords)
        
        # Print them to a file if the option is configured
        if self.saveTrackingResults:
            fileName = f"tracks-{current_time.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
            # Save the coordinates to a file
            with open(os.path.join(self.save_dir, fileName), "a") as f:
                f.write(f"{formatted_coords_str}\n")
        
        # Print the coordinates to the console for sure
        print(f"Coordinates of current tracks at {current_time.strftime('%Y-%m-%d_%H-%M-%S')}: {formatted_coords_str}")
        
    
if __name__ == '__main__':
    
    currentTime = pd.Timestamp.now()
    trackingConfiguration = TrackingConfiguration()
    tracking = get_object_tracking_gm_phd(currentTime, trackingConfiguration)
    
    # General path create with 4 steady objects
    # tracking.update_tracks(np.array(([1, 1, 1, 1], [5, 1, 5, 1], [10, 1, 10, 1], [20, 1, 20, 1])), currentTime + timedelta(seconds=1))
    # tracking.update_tracks(np.array(([1.5, 1, 1.5, 1], [5, 1, 5, 1], [10, 1, 10, 1], [20, 1, 20, 1])), currentTime + timedelta(seconds=2))
    # tracking.update_tracks(np.array(([1.2, 1, 1.2, 1], [5, 1, 5, 1], [10, 1, 10, 1], [20, 1, 20, 1])), currentTime + timedelta(seconds=3))
    # tracking.update_tracks(np.array(([1.4, 1, 1.4, 1], [5, 1, 5, 1], [10, 1, 10, 1], [20, 1, 20, 1])), currentTime + timedelta(seconds=4))
    # tracking.update_tracks(np.array(([1.7, 1, 1.7, 1], [5, 1, 5, 1], [10, 1, 10, 1], [20, 1, 20, 1])), currentTime + timedelta(seconds=5))
    # tracking.update_tracks(np.array(([1.8, 1, 1.8, 1], [5, 1, 5, 1], [10, 1, 10, 1], [20, 1, 20, 1])), currentTime + timedelta(seconds=6))
    # tracking.update_tracks(np.array(([1, 1, 1, 1], [5, 1, 5, 1], [10, 1, 10, 1], [20, 1, 20, 1])), currentTime + timedelta(seconds=7))
    
    # Path tracking with 2 objects, then 1 object, then 2nd object re-appears. Based on path_points_to_deletion it may still be tracked by the same object (5 = same object, 2 = new object)
    # tracking.update_tracks(np.array(([1, 1, 1, 1], [5, 1, 5, 1])), currentTime + timedelta(seconds=1))
    # tracking.update_tracks(np.array(([1.5, 1, 1.5, 1], [5.5, 2, 5.5, 2])), currentTime + timedelta(seconds=2))
    # tracking.update_tracks(np.array(([1.2, 1, 1.2, 1], [6.8, 1, 6.8, 1])), currentTime + timedelta(seconds=3))
    # tracking.update_tracks(np.array(([1.4, 1, 1.4, 1], [7.2, 1, 5.9, 1])), currentTime + timedelta(seconds=4))
    # tracking.update_tracks(np.array(([1.7, 1, 1.7, 1], [6.6, 1, 5.5, 1])), currentTime + timedelta(seconds=5))
    # tracking.update_tracks(np.array(([1.8, 1, 1.8, 1], [6, 1, 5.2, 1])), currentTime + timedelta(seconds=6))
    # tracking.update_tracks(np.array(([1.6, 1, 2.4, 1], [5, 1, 4.5, 1])), currentTime + timedelta(seconds=7))
    # tracking.update_tracks(np.array(([1.5, 1, 2.6, 1],)), currentTime + timedelta(seconds=8))
    # tracking.update_tracks(np.array(([1.3, 1, 2.8, 1],)), currentTime + timedelta(seconds=9))
    # tracking.update_tracks(np.array(([1.0, 1, 2.9, 1],)), currentTime + timedelta(seconds=10))
    # tracking.update_tracks(np.array(([0.8, 1, 3.3, 1],)), currentTime + timedelta(seconds=11))
    # tracking.update_tracks(np.array(([0.7, 1, 3.5, 1],[4.8, 1, 4.2, 1])), currentTime + timedelta(seconds=12))
    # tracking.update_tracks(np.array(([0.6, 1, 3.7, 1],[4.6, 1, 4.6, 1])), currentTime + timedelta(seconds=13))
    # tracking.update_tracks(np.array(([0.5, 1, 3.8, 1],[4.4, 1, 4.8, 1])), currentTime + timedelta(seconds=14))
    # tracking.update_tracks(np.array(([0.3, 1, 4.2, 1],[4.2, 1, 5.2, 1])), currentTime + timedelta(seconds=15))
    
    # 2 objects crossing eachother -- needs some help, has issues with crossovers
    # tracking.update_tracks(np.array(([1, 1, 1, 1], [1, 1, 5, 1])), currentTime + timedelta(seconds=1))
    # tracking.update_tracks(np.array(([2, 1, 2, 1], [2, 2, 4.5, 2])), currentTime + timedelta(seconds=2))
    # tracking.update_tracks(np.array(([3, 1, 3, 1], [3, 1, 4, 1])), currentTime + timedelta(seconds=3))
    # tracking.update_tracks(np.array(([4, 1, 4, 1], [3.5, 1, 3.5, 1])), currentTime + timedelta(seconds=4))
    # tracking.update_tracks(np.array(([5, 1, 5, 1], [4, 1, 3, 1])), currentTime + timedelta(seconds=5))
    # tracking.update_tracks(np.array(([6, 1, 6, 1], [4.2, 1, 2.2, 1])), currentTime + timedelta(seconds=6))
    # tracking.update_tracks(np.array(([7, 1, 7, 1], [5, 1, 2, 1])), currentTime + timedelta(seconds=7))
    
    # Path tracking tests, with objects further apart, at 10m and 60+m. Birth should happen for both. Includes some missed measurements.
    tracking.update_tracks(np.array(([10, 1, 10, 1], [62, 1, 20, 1])), currentTime)
    currentTime = currentTime + timedelta(seconds=1)
    
    tracking.update_tracks(np.array(([13, 1, 6, 1], [63, 1, 21, 1])), currentTime, print_coord=True)
    currentTime = currentTime + timedelta(seconds=1)
    
    tracking.update_tracks(np.array(([18, 1, 4, 1], [64, 1, 23, 1])), currentTime, print_coord=True)
    currentTime = currentTime + timedelta(seconds=1)
    
    tracking.update_tracks(np.array(([22, 1, 20, 1], [65, 1, 25, 1])), currentTime, print_coord=True)
    currentTime = currentTime + timedelta(seconds=1)
    tracking.update_tracks(np.array(([23, 1, 3, 1], [66, 1, 27, 1])), currentTime, print_coord=True)
    currentTime = currentTime + timedelta(seconds=1)
    
    tracking.update_tracks(np.array(([26, 1, 1, 1], [68, 1, 29, 1])), currentTime, print_coord=True)
    currentTime = currentTime + timedelta(seconds=1)
    tracking.update_tracks(np.array(([30, 1, -3, 1], [70, 1, 30, 1])), currentTime, print_coord=True)
    currentTime = currentTime + timedelta(seconds=1)
    
    tracking.update_tracks(np.array(([33, 1, -6, 1], [100, 1, 130, 1])), currentTime, print_coord=True)
    currentTime = currentTime + timedelta(seconds=1)
    tracking.update_tracks(np.array(([-40, 1, -10, 1], [75, 1, 33, 1])), currentTime, print_coord=True)
    currentTime = currentTime + timedelta(seconds=1)
    tracking.update_tracks(np.array(([36, 1, -13, 1], [73, 1, 36, 1])), currentTime, print_coord=True)
    currentTime = currentTime + timedelta(seconds=1)
    tracking.update_tracks(np.array(([34, 1, -16, 1], [72, 1, 125, 1])), currentTime, print_coord=True)
    currentTime = currentTime + timedelta(seconds=1)
    tracking.print_current_tracks(currentTime, remove_tracks=False, interval=5)
    
    tracking.update_tracks(np.array(([37, 1, -20, 1], [71, 1, 37, 1])), currentTime, print_coord=True)
    currentTime = currentTime + timedelta(seconds=1)
    tracking.update_tracks(np.array(([40, 1, -19, 1], [69, 1, 40, 1])), currentTime, print_coord=True)
    currentTime = currentTime + timedelta(seconds=1)
    
    tracking.update_tracks(np.array(([42, 1, -22.2, 1], [130, 1, 20, 1])), currentTime)
    currentTime = currentTime + timedelta(seconds=1)
    tracking.update_tracks(np.array(([44, 1, -24, 1], [66, 1, 43, 1])), currentTime)
    currentTime = currentTime + timedelta(seconds=1)
    
    tracking.print_current_tracks(currentTime, remove_tracks=False, interval=1)
    tracking.show_tracks_plot()
    print("complete")
    
    # Create some detections

        