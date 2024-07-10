import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random

class PolarPlotDynamic:
    def __init__(self, max_points=500, interval=1000, min_angle=-70, max_angle=70, max_distance=100, angle_unit='degrees'):
        self.max_points = max_points
        self.interval = interval
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.max_distance = max_distance
        self.angle_unit = angle_unit  # 'degrees' or 'radians'
        
        # Initialize data arrays
        self.distances = np.zeros(max_points)
        self.angles = np.zeros(max_points)
        self.colors = np.array([self.generate_random_color() for _ in range(max_points)])
        
        # Set up the plotting environment
        self.fig, self.ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(10, 10))
        self.scatter = self.ax.scatter([], [], c=[])
        
        # Customize the plot to display data from min_angle to - max_angle degrees pointed upward
        self.ax.set_theta_zero_location('N')  # Zero degrees is at the top
        self.ax.set_theta_direction(-1)  # Clockwise direction
        self.ax.set_thetamin(min_angle)
        self.ax.set_thetamax(max_angle)
        self.ax.set_ylim(0, max_distance)  # Set the maximum distance
        self.ax.set_ylabel('Range (m)', fontsize=12)
        self.ax.set_title(f'Radar Detections', fontsize=18)
        
        # Initialize the animation
        self.anim = FuncAnimation(self.fig, self.update_plot, init_func=self.init_plot, interval=interval, blit=True, cache_frame_data=False)
        
        # Show the plot
        plt.show(block=False)

    def generate_random_color(self):
        return (random.random(), random.random(), random.random())

    def init_plot(self):
        self.scatter.set_offsets(np.empty((0, 2)))
        self.scatter.set_color(np.empty((0, 3)))
        return self.scatter,

    def update_data(self, new_distances, new_angles, clear=False):
        # Clear the data arrays if the clear parameter is True
        if clear:
            self.distances.fill(0)
            self.angles.fill(0)
            self.colors = np.array([self.generate_random_color() for _ in range(self.max_points)])
        
        # Check if the input arrays are None or have less than 1 element
        if new_distances is None or new_angles is None or len(new_distances) < 1 or len(new_angles) < 1:
            return

        num_new_points = len(new_distances)
        if num_new_points > self.max_points:
            num_new_points = self.max_points

        # Roll the arrays to make space for new data
        self.distances = np.roll(self.distances, -num_new_points)
        self.angles = np.roll(self.angles, -num_new_points)
        self.colors = np.roll(self.colors, -num_new_points, axis=0)

        # Insert new data at the end
        self.distances[-num_new_points:] = new_distances
        self.angles[-num_new_points:] = new_angles
        self.colors[-num_new_points:] = np.array([self.generate_random_color() for _ in range(num_new_points)])

    def update_plot(self, frame):
        if self.angle_unit == 'degrees':
            angles_radians = np.radians(self.angles)
        else:
            angles_radians = self.angles

        self.scatter.set_offsets(np.c_[angles_radians, self.distances])
        self.scatter.set_color(self.colors)
        return self.scatter,

# Example usage
if __name__ == "__main__":
    plot = PolarPlotDynamic(max_points=500, interval=1000, min_angle=-90, max_angle=90, max_distance=15, angle_unit='degrees')
    
    # Example to update data dynamically with clearing the graph
    new_batches = [
        ([1, 2, 3], [30, 60, 90], True),  # First batch
        ([4, 5, 6], [120, 150, 180], True),  # Second batch
        ([7, 8, 9], [210, 240, 270], True),  # Third batch
        # Add more batches as needed
    ]
    
    for batch in new_batches:
        plot.update_data(*batch, clear=True)
        plt.pause(1)  # Pause to allow the plot to update

    plt.show()  # Show the plot at the end
