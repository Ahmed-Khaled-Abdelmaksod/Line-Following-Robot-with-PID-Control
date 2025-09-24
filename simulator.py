import numpy as np

class Simulator:
    def __init__(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta
        self.true_pose = (x, y, theta)
    
    def update(self, v, omega, dt):
        """
        Update the robot's state using differential drive kinematics.
        """
        self.x += v * dt * np.cos(self.theta)
        self.y += v * dt * np.sin(self.theta)
        self.theta += omega * dt
        self.true_pose = (self.x, self.y, self.theta)
    
    def get_pose(self, with_noise=True, noise_std_dev=0.01):
        """
        Returns the robot's pose, optionally with added sensor noise.
        """
        if not with_noise:
            return self.true_pose
        
        noisy_x = self.x + np.random.normal(0, noise_std_dev)
        noisy_y = self.y + np.random.normal(0, noise_std_dev)
        noisy_theta = self.theta + np.random.normal(0, noise_std_dev / 10)

        return (noisy_x, noisy_y, noisy_theta)

    def get_errors(self, path):
        """
        Calculate lateral and heading errors relative to the path.
        """
        noisy_x, noisy_y, noisy_theta = self.get_pose(with_noise=True,noise_std_dev=0.2)

        ref_y = path.get_reference_y(noisy_x)
        lateral_error = noisy_y - ref_y

        ref_theta = path.get_reference_heading(noisy_x)
        heading_error = noisy_theta - ref_theta

        heading_error = np.arctan2(np.sin(heading_error), np.cos(heading_error))

        return lateral_error, heading_error