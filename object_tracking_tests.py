import numpy as np
from object_tracking.detection_patterns import object_tracking_straight, object_tracking_across
from plots.PlotDetectionsDynamic import PlotDetectionsDynamic
import matplotlib.pyplot as plt
import time


width_samples = 8
detections = object_tracking_across[::-1, :]
# detections = object_tracking_straight[::-1, :]

# plotter = PlotDetectionsDynamic(num_plots=1,max_steps=10, plot_titles=["Detections"], x_axis_values=width_samples)

# for i in range(13):
#     under_test = detections[i]
#     plotter.update_data([under_test])
#     plt.pause(0.01)
#     print(f"Iteration: {i}")
    
# # Define movement probabilities
# p_jump = {
#     1: 0.75,  # High probability to move one square
#     2: 0.15, # Less likely to jump two squares
#     3: 0.075,  # Least likely to jump three squares
#     4: 0.025  # Least likely to jump three squares
# }

# # Initialize the tracking matrix
# track_matrix = np.zeros_like(detections, dtype=float)
# track_matrix[0] = detections[0]

# for t in range(1, detections.shape[0]):
#     for i in range(detections.shape[1]):
#         prob_sum = 0
#         # Check all possible movements within the jump range
#         for jump, p in p_jump.items():
#             # Check leftward jumps if within bounds
#             if i >= jump:
#                 prob_sum += track_matrix[t-1, i-jump] * p
#             # Check rightward jumps if within bounds
#             if i + jump < detections.shape[1]:
#                 prob_sum += track_matrix[t-1, i+jump] * p
#             # Check straight downward movement
#             prob_sum += track_matrix[t-1, i] * p

#         # Normalize the probability sum based on the number of considered movements
#         prob_sum /= (2 * sum(p_jump.values()))  # Adjust normalization factor based on your model specifics

#         # Update based on detection
#         if detections[t, i] == 1:
#             # Object detected, update probability considering detection
#             track_matrix[t, i] = prob_sum + (1 - prob_sum) * p_jump.get(1, 0.7)
#         else:
#             # Object not detected, consider it a miss
#             track_matrix[t, i] = prob_sum * (1 - p_jump.get(1, 0.7))

# # Plotting the tracking probability matrix as a heatmap
# plt.figure(figsize=(10, 8))
# plt.imshow(track_matrix, cmap='hot', interpolation='nearest')
# plt.title('Tracking Probability Heatmap')
# plt.xlabel('Position')
# plt.ylabel('Time Step')
# plt.colorbar()
# plt.show()

# # Movement probabilities for left, right, and straight
# p_move = {
#     'left': 0.3,
#     'right': 0.3,
#     'down': 0.4
# }

# # Initialize the tracking matrix
# n_rows, n_cols = detections.shape
# track_matrix = np.zeros_like(detections, dtype=float)
# track_matrix[0] = detections[0]  # Initial confidence is just the detection itself

# for t in range(1, n_rows):
#     for i in range(n_cols):
#         # Calculate probabilities from three possible previous states
#         left_prob = track_matrix[t-1, i-1] * p_move['left'] if i > 0 else 0
#         right_prob = track_matrix[t-1, i+1] * p_move['right'] if i < n_cols - 1 else 0
#         down_prob = track_matrix[t-1, i] * p_move['down']

#         # Total probability of being the same object
#         track_matrix[t, i] = (left_prob + right_prob + down_prob) * detections[t, i]

# # Plotting the tracking probability matrix as a heatmap
# plt.figure(figsize=(10, 8))
# plt.imshow(track_matrix, cmap='hot', interpolation='nearest')
# plt.title('Object Tracking Probability Heatmap')
# plt.xlabel('Position')
# plt.ylabel('Time Step')
# plt.colorbar()
# plt.show()

# -----------------------------------------------
# import numpy as np

# # Example detection data provided earlier:
# detections = np.array([
#     [0, 0], [1, 1], [2, 2], [3, 3], [4, 4], 
#     [5, 5], [6, 6], [5, 5], [4, 4], [3, 3], 
#     [2, 2], [1, 1], [0, 0]
# ])

# def estimate_initial_velocity(detections):
#     # Estimate initial velocity based on the first two positions
#     if len(detections) > 1:
#         return detections[1] - detections[0]
#     else:
#         return np.zeros(2)

# # Initial state (position and velocity)
# initial_velocity = estimate_initial_velocity(detections)
# x = np.array([detections[0][0], detections[0][1], initial_velocity[0], initial_velocity[1]])

# # Initial uncertainty: large uncertainty in velocity
# P = np.diag([1, 1, 100, 100])

# # Time step
# dt = 1

# # State transition matrix, assumes constant velocity model
# F = np.array([
#     [1, 0, dt, 0],  # Update x position
#     [0, 1, 0, dt],  # Update y position
#     [0, 0, 1, 0],   # Maintain x velocity
#     [0, 0, 0, 1]    # Maintain y velocity
# ])

# # Measurement function: we can only measure positions
# H = np.array([
#     [1, 0, 0, 0],
#     [0, 1, 0, 0]
# ])

# # Measurement uncertainty
# R = np.array([
#     [0.1, 0],  # Variance in x measurement
#     [0, 0.1]   # Variance in y measurement
# ])

# # Process covariance matrix: small uncertainty if we trust our model
# Q = np.diag([0.1, 0.1, 1, 1])

# # Identity matrix for the update step
# I = np.eye(4)

# def kalman_filter(x, P, F, H, Q, R, I, measurements):
#     results = []
#     for Z in measurements:
#         # Measurement update
#         Z = np.array(Z).reshape(2, 1)
#         y = Z - np.dot(H, x.reshape(4, 1))
#         S = np.dot(H, np.dot(P, H.T)) + R
#         K = np.dot(P, np.dot(H.T, np.linalg.inv(S)))
#         x = x + np.dot(K, y).reshape(1, 4)[0]
#         P = np.dot((I - np.dot(K, H)), P)

#         # Prediction
#         x = np.dot(F, x)
#         P = np.dot(F, np.dot(P, F.T)) + Q

#         # Store results
#         results.append(x[:2])

#     return results

# tracked_positions = kalman_filter(x, P, F, H, Q, R, I, detections)

# # Print the estimated positions
# for idx, pos in enumerate(tracked_positions, 1):
#     print(f'Step {idx}: Estimated Position: x={pos[0]}, y={pos[1]}')


import numpy as np
import matplotlib.pyplot as plt

# Provided detection data for plotting
detections = np.array([
    [0, 0], [1, 2], [2, 3], [3, 3], [4, 4],
    [5, 5], [6, 6], [5, 5], [4, 4], [3, 3],
    [2, 2], [1, 1], [0, 0]
])

def estimate_initial_velocity(detections):
    # Estimate initial velocity based on the first two positions
    if len(detections) > 1:
        return detections[1] - detections[0]
    else:
        return np.zeros(2)

# Initial state (position and velocity)
initial_velocity = estimate_initial_velocity(detections)
x = np.array([detections[0][0], detections[0][1], initial_velocity[0], initial_velocity[1]])

# Initial uncertainty: large uncertainty in velocity
P = np.diag([1, 1, 100, 100])

# Time step
dt = 1

# State transition matrix, assumes constant velocity model
F = np.array([
    [1, 0, dt, 0],  # Update x position
    [0, 1, 0, dt],  # Update y position
    [0, 0, 1, 0],   # Maintain x velocity
    [0, 0, 0, 1]    # Maintain y velocity
])

# Measurement function: we can only measure positions
H = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0]
])

# Measurement uncertainty
R = np.array([
    [0.1, 0],  # Variance in x measurement
    [0, 0.1]   # Variance in y measurement
])

# Process covariance matrix: small uncertainty if we trust our model
Q = np.diag([0.1, 0.1, 1, 1])

# Identity matrix for the update step
I = np.eye(4)

def kalman_filter(x, P, F, H, Q, R, I, measurements):
    results = []
    for Z in measurements:
        # Measurement update
        Z = np.array(Z).reshape(2, 1)
        y = Z - np.dot(H, x.reshape(4, 1))
        S = np.dot(H, np.dot(P, H.T)) + R
        K = np.dot(P, np.dot(H.T, np.linalg.inv(S)))
        x = x + np.dot(K, y).reshape(1, 4)[0]
        P = np.dot((I - np.dot(K, H)), P)

        # Prediction
        x = np.dot(F, x)
        P = np.dot(F, np.dot(P, F.T)) + Q

        # Store results
        results.append(x[:2])

    return results

tracked_positions = kalman_filter(x, P, F, H, Q, R, I, detections)

# Plotting the results
plt.figure(figsize=(10, 6))
plt.plot(detections[:, 0], detections[:, 1], 'ro-', label='True Positions')
tracked_positions_array = np.array(tracked_positions)
plt.plot(tracked_positions_array[:, 0], tracked_positions_array[:, 1], 'bx-', label='Estimated Positions')
plt.title('Comparison of True and Estimated Trajectories')
plt.xlabel('Position X')
plt.ylabel('Position Y')
plt.legend()
plt.grid(True)
plt.show()

print("test")
