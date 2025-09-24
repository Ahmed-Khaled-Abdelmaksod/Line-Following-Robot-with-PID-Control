from simulator import Simulator
from controller import PIDController
from visualizer import Visualizer
from path import CurvedPath, StraightLinePath 

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

# --- Choose Path Type and Simulation Mode ---
path_type = "curved"    # Options: "curved" or "straight"
run_animation = True   # Set to False to run KPI calculation instead

# Simulation parameters
dt = 0.1
sim_time = 90.0
n_steps = int(sim_time / dt)
# kp = -1.0 , ki = 0.0 , kd = 0.5
kp = -2.5
ki = 0.1
kd = 0.6
controller = PIDController(kp=kp, ki=ki, kd=kd)

# --- Path Initialization ---
if path_type == "curved":
    path_instance = CurvedPath(amplitude=1.5, frequency=0.2)
    sim = Simulator(x=0.0, y=0.0, theta=np.pi/4)
elif path_type == "straight":
    path_instance = StraightLinePath(y_ref=1.0)
    sim = Simulator(x=0.0, y=0.0, theta=0)

# --- Simulation Execution ---
if run_animation:
    viz = Visualizer(path=path_instance)

    # This function will be called by FuncAnimation at each frame
    def update_frame(i):
        lateral_error, heading_error = sim.get_errors(path_instance)
        combined_error = lateral_error + 1.0 * heading_error
        omega_cmd = controller.update(error=combined_error, dt=dt)
        v_cmd = 0.5
        sim.update(v_cmd, omega_cmd, dt)
        x, y, _ = sim.get_pose(with_noise=True, noise_std_dev=0.01)
        return viz.update_plot(x, y)

    ani = FuncAnimation(viz.fig, update_frame, frames=n_steps, blit=True, interval=int(dt * 1000))
    plt.show()

else: # Run for KPI calculation
    viz = Visualizer(path=path_instance)
    history = {'x':[], 'y':[], 'lateral_error':[], 'heading_error':[]}

    for i in range(n_steps):
        x, y, theta = sim.get_pose(with_noise=True, noise_std_dev=0.01)
        lateral_error, heading_error = sim.get_errors(path_instance)
        combined_error = lateral_error + 1.0 * heading_error
        omega_cmd = controller.update(error=combined_error, dt=dt)
        v_cmd = 0.5
        sim.update(v_cmd, omega_cmd, dt)
        viz.update_plot(x, y)
        history['x'].append(x)
        history['y'].append(y)
        history['lateral_error'].append(lateral_error)
        history['heading_error'].append(heading_error)

    # --- KPI CALCULATION AND REPORTING ---
    print("\n--- KPI Results ---")
    print(f"Controller: Kp={kp}, Ki={ki}, Kd={kd}")
    print(f"Path Type: {path_type.capitalize()}")

    max_deviation = max(np.abs(history['lateral_error']))
    print(f"Overshoot/Max Deviation: {max_deviation:.4f} m")

    steady_state_error = np.mean(history['lateral_error'][int(n_steps * 0.9):])
    print(f"Steady-State Error: {steady_state_error:.4f} m")

    tolerance = 0.05
    settling_time_steps = next((i for i, error in enumerate(history['lateral_error']) if all(abs(e) <= tolerance for e in history['lateral_error'][i:])), None)
    
    if settling_time_steps is not None:
        settling_time = settling_time_steps * dt
        print(f"Settling Time: {settling_time:.2f} s")
    else:
        print("System did not settle within the tolerance.")

    # Plot the errors over time
    plt.figure()
    plt.plot(history['lateral_error'], label='Lateral Error')
    plt.plot(history['heading_error'], label='Heading Error')
    plt.title('Errors Over Time')
    plt.xlabel('Time step')
    plt.ylabel('Error')
    plt.grid(True)
    plt.legend()
    plt.show()

    