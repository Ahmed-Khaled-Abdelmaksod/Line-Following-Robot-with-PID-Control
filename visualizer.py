import matplotlib.pyplot as plt
import matplotlib.animation as FuncAnimation

import numpy as np

class Visualizer:
    def __init__(self,path):
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.ax.set_xlim(-1, 10)
        self.ax.set_ylim(-3, 3)
        self.ax.set_title('Line Following Robot Simulation')
        self.ax.set_xlabel('X position (m)')
        self.ax.set_ylabel('Y position (m)')
        self.ax.grid(True)

                
        self.ax.axhline(y=path, color='r', linestyle='--', label='Reference Path')

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
    def show(self):
        """Show the plot (for static plots)."""
        plt.show()