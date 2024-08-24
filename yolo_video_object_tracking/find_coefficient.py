import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Example data: known distances (in meters) and corresponding bounding box widths (in pixels)
distances = np.array([1, 2.86])  # Known distances
bb_widths = np.array([90, 32])  # Corresponding bounding box widths

# Reshape data for sklearn
bb_widths_reshaped = bb_widths.reshape(-1, 1)

# Create and fit the model
model = LinearRegression()
model.fit(bb_widths_reshaped, distances)

# The coefficient is the inverse of the slope of the fitted line
coefficient = 1 / model.coef_[0]
print("Coefficient:", coefficient)

# Plotting the data and the fitted line
plt.scatter(bb_widths, distances, color='blue')
plt.plot(bb_widths, model.predict(bb_widths_reshaped), color='red')
plt.xlabel('Bounding Box Width (pixels)')
plt.ylabel('Distance (meters)')
plt.title('Bounding Box Width vs Distance')
plt.show()