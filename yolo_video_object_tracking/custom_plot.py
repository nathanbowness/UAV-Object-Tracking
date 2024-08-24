import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import defaultdict

class LivePlot:
    def __init__(self, xlim=(0, 10), ylim=(0, 10), interval=100):
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.objects_data = defaultdict(list)
        self.lines = {}
        self.ani = animation.FuncAnimation(self.fig, self.animate, interval=interval, repeat=False)
        
    def update(self, frame, objects_map):
        # Clear the plot
        self.ax.clear()
        self.ax.set_xlim(self.ax.get_xlim())
        self.ax.set_ylim(self.ax.get_ylim())
        
        # Update the lines
        for object_id, (distance, angle) in objects_map.items():
            if object_id in self.objects_data:
                self.objects_data[object_id].append((distance, angle))
            else:
                self.objects_data[object_id] = [(distance, angle)]
            
            if object_id not in self.lines:
                self.lines[object_id], = self.ax.plot([], [], label=f'Object {object_id}')

            line = self.lines[object_id]
            distances, angles = zip(*self.objects_data[object_id])
            line.set_data(distances, angles)

        # Remove lines for objects that no longer exist
        existing_ids = set(objects_map.keys())
        for object_id in list(self.objects_data.keys()):
            if object_id not in existing_ids:
                del self.objects_data[object_id]
                del self.lines[object_id]

        # Update legend
        self.ax.legend()

    # Sample objects map to simulate the update
    # Replace this with your actual data fetching mechanism
    def get_objects_map(self):
        import random
        objects_map = {}
        for i in range(random.randint(1, 5)):
            object_id = random.randint(1, 10)
            distance = random.uniform(0, 10)
            angle = random.uniform(0, 10)
            objects_map[object_id] = (distance, angle)
        return objects_map

    # Update function for the animation
    def animate(self, frame):
        objects_map = self.get_objects_map()
        self.update(frame, objects_map)
        
    def show(self):
        plt.show(block=False)