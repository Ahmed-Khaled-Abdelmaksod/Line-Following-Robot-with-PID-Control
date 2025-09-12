from simulator import Simulator
from controller import PIDController
from visualizer import Visualizer

import matplotlib.pyplot as plt
import numpy as np

# Simulation parameters
dt = 0.1  # time step [s]
sim_time = 40.0  # total simulation time [s]
n_steps = int(sim_time / dt)

sim = Simulator(x=0.0,y=2.0,theta=0)
controller = PIDController(kp=0.1, ki=0.01, kd=0.1)
viz = Visualizer(path=0)
history = {'x':[],'y':[],'error':[]}
for i in range(n_steps):
    x,y,theta = sim.get_pose(with_noise=True,noise_std_dev=0.05)
    error = sim.get_lateral_error(path=0)
    omega_cmd = controller.update(error=error,dt=dt)
    v_cmd = 0.5
    sim.update(v_cmd,omega_cmd,dt)
    viz.update_plot(x,y)
    history['x'].append(x)
    history['y'].append(y)
    history['error'].append(error)

# After simulation, plot the error over time
plt.figure()
plt.plot(history['error'])
plt.title('Lateral Error Over Time')
plt.xlabel('Time step')
plt.ylabel('Error (m)')
plt.grid(True)
plt.show()

# Keep the trajectory plot open
viz.show()