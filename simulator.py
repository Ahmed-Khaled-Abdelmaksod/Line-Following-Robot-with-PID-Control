
import numpy as np
def update_pose(v,omega):
    pass

def add_noise(pose):
    pass
class Simulator:
    def __init__(self,x,y,theta):
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.true_pose = (x,y,theta)
    
    def update(self,v,omega,dt):
        """
        Update the robot's state using differential drive kinematics.
        v: linear velocity command (m/s)
        omega: angular velocity command (rad/s)
        dt: time step (s)
        """
        self.x += v * dt * np.cos(self.theta)
        self.y += v * dt * np.sin(self.theta)
        self.theta += omega * dt
        self.true_pose = (self.x,self.y,self.theta) 
    
    def get_pose(self,with_noise=True,noise_std_dev=0.01):
        if not with_noise:
            return self.true_pose
        
        noisy_x = self.x + np.random.normal(0,noise_std_dev)
        noisy_y = self.y + np.random.normal(0,noise_std_dev)
        noisy_theta = self.theta + np.random.normal(0,noise_std_dev/10)

        return (noisy_x,noisy_y,noisy_theta)
    def get_lateral_error(self,path):
        
        _,y_measured,_ = self.get_pose(with_noise=True)
        lateral_error = y_measured - path
        return lateral_error
