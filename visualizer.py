import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class Visualizer:
    def __init__(self, path):
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.ax.set_xlim(-1, 55)
        self.ax.set_ylim(-3, 3)
        self.ax.set_title('Line Following Robot Simulation')
        self.ax.set_xlabel('X position (m)')
        self.ax.set_ylabel('Y position (m)')
        self.ax.grid(True)

        # Plot the reference path based on its type
        path_x = np.linspace(0, 50, 500)
        path_y = [path.get_reference_y(x) for x in path_x]
        self.ax.plot(path_x, path_y, 'r--', label='Reference Path')
        
        self.trajectory_line, = self.ax.plot([], [], 'b-', label='Robot Path')
        self.current_pos, = self.ax.plot([], [], 'go', markersize=8, label='Current Position')
        self.ax.legend()

        self.x_data = []
        self.y_data = []
    
    def update_plot(self, x, y):
        """Update the plot with new robot position."""
        self.x_data.append(x)
        self.y_data.append(y)
        self.trajectory_line.set_data(self.x_data, self.y_data)
        self.current_pos.set_data([x], [y])
        return self.trajectory_line, self.current_pos