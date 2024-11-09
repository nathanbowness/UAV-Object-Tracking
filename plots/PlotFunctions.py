import numpy as np
from matplotlib import pyplot as plt
from tracking.DetectionsAtTime import DetectionsAtTime

def plot_polar_detections(ax_polar, detected_distances_Rx1, detected_angles_Rx1, detected_distances_Rx2, detected_angles_Rx2, MAX_DIST):
    # Ensure detected_distances and detection_angles have the same length
    if len(detected_distances_Rx1) != len(detected_angles_Rx1):
        raise ValueError(f"Length mismatch: detected_distances_Rx1 has length {len(detected_distances_Rx1)}, but detected_angles_Rx1 has length {len(detected_angles_Rx1)}")
    if len(detected_distances_Rx2) != len(detected_angles_Rx2):
        raise ValueError(f"Length mismatch: detected_distances_Rx2 has length {len(detected_distances_Rx2)}, but detected_angles_Rx2 has length {len(detected_angles_Rx2)}")
    
    # Update Polar Plot
    ax_polar.plot(np.radians(detected_angles_Rx1), detected_distances_Rx1, 'k*', markersize=8, label="Detections Rx1")
    ax_polar.plot(np.radians(detected_angles_Rx2), detected_distances_Rx2, 'b*', markersize=8, label="Detections Rx2")
    ax_polar.set_ylim([0, MAX_DIST])
    ax_polar.set_theta_zero_location('N')  # Set 0 degrees to face north
    ax_polar.set_thetalim(np.deg2rad([-90, 90]))  # Only show grid labels from -90 to 90 degrees
    ax_polar.legend(loc="upper right")
    
def db_conv(arr):
    arr = np.where(arr > 0, arr, np.nan)  # Replace non-positive values with NaN
    return 20 * np.log10(arr)

def plot_cartesian_detections(ax_cartesian, Rx1_amp, Rx2_amp, cfar_detection_Rx1, cfar_detection_Rx2, cfar_threshold_Rx1, cfar_threshold_Rx2, detected_distances_Rx1, detected_distances_Rx2, range_vector):
    # Update Cartesian Plot
    ax_cartesian.plot(range_vector, db_conv(Rx1_amp), label="Signal Rx1")  # Added small constant for log stability
    ax_cartesian.plot(range_vector, db_conv(cfar_threshold_Rx1), 'r', label="CFAR Threshold Rx1")
    ax_cartesian.plot(range_vector, db_conv(Rx2_amp), label="Signal Rx2")  # Added small constant for log stability
    ax_cartesian.plot(range_vector, db_conv(cfar_threshold_Rx2), 'g', label="CFAR Threshold Rx2")
    cfar_detection_Rx1_bool = np.where(cfar_detection_Rx1)[0]
    cfar_detection_Rx2_bool = np.where(cfar_detection_Rx2)[0]
    ax_cartesian.plot(detected_distances_Rx1, db_conv(Rx1_amp[cfar_detection_Rx1_bool]), 'k*', label="Detections Rx1")
    ax_cartesian.plot(detected_distances_Rx2, db_conv(Rx2_amp[cfar_detection_Rx2_bool]), 'b*', label="Detections Rx2")
    ax_cartesian.set_xlabel("Distance (m)")
    ax_cartesian.set_ylabel("Level (dB)")
    ax_cartesian.legend(loc="lower right")
    ax_cartesian.grid()
    
def plot_xy_detections(ax_xy, detections_at_time: DetectionsAtTime, max_dist: float = 110.0):
    # Extract detection details
    detections = detections_at_time.detections
    
    # Initialize lists for Rx1 and Rx2 coordinates
    x_Rx1, y_Rx1 = [], []
    x_Rx2, y_Rx2 = [], []

    # Iterate over detections and separate Rx1 and Rx2 coordinates
    for detection in detections:
        x, _, y, _ = detection.data
        if detection.object == "Rx1":
            x_Rx1.append(x)
            y_Rx1.append(y)
        elif detection.object == "Rx2":
            x_Rx2.append(x)
            y_Rx2.append(y)
    
    # Plot the detections
    ax_xy.plot(x_Rx1, y_Rx1, 'k*', label="Detections Rx1")
    ax_xy.plot(x_Rx2, y_Rx2, 'b*', label="Detections Rx2")
    ax_xy.set_xlabel("X (m)")
    ax_xy.set_ylabel("Y (m)")
    ax_xy.set_xlim([0, max_dist])
    ax_xy.set_ylim([-max_dist, max_dist])
    ax_xy.legend(loc="upper right")
    ax_xy.grid()