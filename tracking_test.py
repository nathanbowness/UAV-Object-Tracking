import numpy as np
from scipy.stats import multivariate_normal
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def predict_state(x, dt, A, Q):
    """ Predict the next state with the constant velocity model """
    return np.dot(A, x), Q

def create_cv_model(dt):
    """ Create the matrices for the constant velocity model """
    A = np.array([[1, 0, dt, 0],
                  [0, 1, 0, dt],
                  [0, 0, 1, 0],
                  [0, 0, 0, 1]])  # State transition model
    Q = np.eye(4) * 0.1  # Process noise covariance
    return A, Q

def measurement_model(x):
    """ Measurement model that maps the state to the measurement space """
    H = np.array([[1, 0, 0, 0],
                  [0, 1, 0, 0]])  # Measurement matrix
    return np.dot(H, x)

def measurement_noise(R_scale=1.0):
    """ Measurement noise covariance """
    R = np.eye(2) * R_scale
    return R

def jpda_probabilities(tracks, measurements, H, R):
    """ Calculate association probabilities for each track to each measurement """
    num_tracks = len(tracks)
    num_meas = len(measurements)
    prob_matrix = np.zeros((num_tracks, num_meas))

    for i, track in enumerate(tracks):
        for j, meas in enumerate(measurements):
            pred_meas = measurement_model(track['state'])
            S = np.dot(H, np.dot(track['covariance'], H.T)) + R
            mvn = multivariate_normal(mean=pred_meas, cov=S)
            prob_matrix[i, j] = mvn.pdf(meas)
        
        prob_matrix[i, :] /= np.sum(prob_matrix[i, :])  # Normalize probabilities

    return prob_matrix

def update_tracks(tracks, measurements, prob_matrix, H, R):
    """ Update each track with the associated measurements """
    for i, track in enumerate(tracks):
        total_prob = np.sum(prob_matrix[i, :])
        if total_prob > 0:  # Avoid division by zero
            for j, meas in enumerate(measurements):
                weight = prob_matrix[i, j] / total_prob
                y = meas - measurement_model(track['state'])  # Measurement residual
                K = np.dot(track['covariance'], np.dot(H.T, np.linalg.inv(np.dot(H, np.dot(track['covariance'], H.T)) + R)))  # Kalman gain
                track['state'] += np.dot(K, y) * weight
                track['covariance'] = np.dot(np.eye(len(K)) - np.dot(K, H), track['covariance'])
                
def main_loop():
    while True:  # Replace this with a condition to stop processing, e.g., end of data
        # Simulate receiving a new radar measurement
        # In practice, replace this with actual data retrieval logic
        measurements = simulate_radar_measurements()

        # Predict the state of each track
        for track in tracks:
            predicted_state, _ = predict_state(track['state'], dt, A, Q)
            track['state'] = predicted_state
            track['covariance'] = np.dot(A, np.dot(track['covariance'], A.T)) + Q

        # Compute JPDA probabilities
        prob_matrix = jpda_probabilities(tracks, measurements, H, R)

        # Update tracks with JPDA
        update_tracks(tracks, measurements, prob_matrix, H, R)

        # Here, you could also handle track management (creating new tracks, deleting lost ones)

        # Visualization or logging here (optional)
        print_tracks(tracks)

def simulate_radar_measurements():
    """ Function to simulate radar measurements for testing """
    # Simulate some random measurements around actual track positions
    # This is just a placeholder. Replace it with actual data retrieval or more sophisticated simulation
    return np.random.randn(len(tracks), 2) + [track['state'][0:2] for track in tracks]

def print_tracks(tracks):
    """ Utility function to print track states """
    for i, track in enumerate(tracks):
        print(f"Track {i}: Position = ({track['state'][0]}, {track['state'][1]})")
                
# Constants
dt = 0.115  # time step in seconds
A, Q = create_cv_model(dt)  # state transition and noise matrices
H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]])  # Measurement matrix
R = measurement_noise(0.1)  # Measurement noise covariance

# Initialize Tracks
tracks = []
initial_state = np.array([0, 0, 0, 0])  # Initial state (x, y, vx, vy)
initial_covariance = np.eye(4) * 10  # Initial uncertainty

# Example of initializing a track
tracks.append({'state': initial_state, 'covariance': initial_covariance})

# Initialize figure for plotting
fig, ax = plt.subplots()
line_est, = ax.plot([], [], 'ro-', label="Estimated Track")
line_real, = ax.plot([], [], 'bo-', label="Real Track")
ax.set_xlim(-100, 100)
ax.set_ylim(-100, 100)
ax.legend()

def init():
    """ Initialize background of the plot """
    line_est.set_data([], [])
    line_real.set_data([], [])
    return line_est, line_real

def update(frame):
    """ Update the plot for each frame """
    # Here we simulate both the measurement and the real position
    real_positions, measurements = simulate_radar_measurements()

    # Predict and update each track
    for track in tracks:
        track['predicted_state'], _ = predict_state(track['state'], dt, A, Q)
        track['state'] = track['predicted_state']
        track['covariance'] = np.dot(A, np.dot(track['covariance'], A.T)) + Q

    # Compute JPDA probabilities
    prob_matrix = jpda_probabilities(tracks, measurements, H, R)

    # Update tracks with JPDA
    update_tracks(tracks, measurements, prob_matrix, H, R)

    # Extract positions for plotting
    est_positions = [track['state'][:2] for track in tracks]
    line_est.set_data(*zip(*est_positions))
    line_real.set_data(*zip(*real_positions))
    return line_est, line_real

def simulate_radar_measurements():
    """ Simulate real and measurement positions for the tracks """
    real_positions = [track['state'][0:2] + np.random.randn(2) * 10 for track in tracks]  # Real positions with some noise
    measurements = [pos + np.random.randn(2) * 5 for pos in real_positions]  # Measurements with more noise
    return real_positions, measurements

# Create animation
ani = FuncAnimation(fig, update, frames=np.arange(100), init_func=init, blit=True, interval=100)

# To show plot
plt.show()

if __name__ == "__main__":
    main_loop()