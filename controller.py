class PIDController:
    def __init__(self,kp,ki,kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.prev_error = 0.0
    
    def update(self,error,dt):
        """
        Calculate control output based on error and time step.
        error: the current error signal
        dt: time step (s)
        Returns: control output (u)
        """

        P = self.kp * error

        self.integral +=  error * dt
        I = self.integral * self.ki

        derivative = (error - self.prev_error ) / dt
        D = derivative * self.kd

        self.prev_error = error

        out = P + I + D
        return out