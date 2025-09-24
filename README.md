# Line-Following Robot with PID Control

A Siemens collaborative project implementing a digital twin of a differential-drive robot that follows predefined paths using PID control. Developed as part of the Siemens Digital Twin & Its Applications framework, this project demonstrates industrial automation principles with both standalone and Siemens VSI-integrated architectures.

## 📁 Project Structure


The repository contains two main implementations:

### 📂 `with-vsi-integration/`
- **Architecture**: Distributed system using Innexis Virtual System Interconnect (IVSI)
- **Components**: 
  - **PID Controller** – Computes control commands to minimize path-tracking error
  - **Simulator** – Models robot kinematics and updates position over time
  - **Visualizer** – Displays real-time robot trajectory and performance
- **Communication**: Components communicate via IVSI using socket-based messaging
- **Features**: Decoupled, modular design suitable for distributed systems

### 📂 `without-vsi/`
- **Architecture**: Standalone integrated system
- **Components**: All functionality (controller, simulator, visualizer) in a single application
- **Communication**: Direct function calls within the same process
- **Features**: Simpler setup, easier to understand for learning purposes


## 🧠 Model Description

### Robot Kinematics (Differential Drive)
\[
x_{k+1} = x_k + v_k \cdot \cos(\theta_k) \cdot \Delta t
\]
\[
y_{k+1} = y_k + v_k \cdot \sin(\theta_k) \cdot \Delta t
\]
\[
\theta_{k+1} = \theta_k + \omega_k \cdot \Delta t
\]

### PID Control Law
\[
u_k = K_p \cdot e_k + K_i \cdot \sum_{j=0}^{k} e_j \cdot \Delta t + K_d \cdot \frac{e_k - e_{k-1}}{\Delta t}
\]

### Sensor Noise Model
Gaussian noise is added to simulate real-world sensor inaccuracies.

## 🧪 Experiments Conducted

### Experiment 1: Straight Line Path (No Noise)
- **Reference Path**: \( y = 2 \)
- Tested multiple PID gains to analyze overshoot, settling time, and steady-state error.

### Experiment 2: Curved Path (With Noise)
- **Reference Path**: \( y = A \sin(\omega x) \)
- Tested under low and high noise conditions.

### Experiment 3: Straight Line Path (With Noise)
- Evaluated robustness of PID control under sensor noise.

### Experiment 4: Curved Path (PD vs PID)
- Compared PD and PID performance on sinusoidal paths.

## 📊 Performance Metrics

- **Maximum Overshoot**: Peak deviation from the reference path
- **Settling Time**: Time to reach and stay within 5% of steady-state error
- **Steady-State Error**: Long-term average tracking error

## 🛠️ Technologies Used

- Python
- IVSI (Innexis Virtual System Interconnect)
- Socket-based communication
- Matplotlib for visualization
## 📈 Results

Results from various trials are included in the report. Key findings:

- PID control effectively minimizes tracking error on straight paths.
- Curved paths and high noise levels challenge controller performance.
- Proper tuning of \( K_p, K_i, K_d \) is critical for stability.

## 👨‍💻 Author

**Ahmed Khaled Abdelmaksod Ebrahim**  
Course: Digital Twin & Its Applications  
Supervisors: Dr. Mohamed Abdelsalam & Eng. Mohamed El-Leithy

## 📄 License

This project is for academic and educational purposes.