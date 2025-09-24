import numpy as np

class CurvedPath:
    def __init__(self, amplitude=2.0, frequency=0.05):
        self.amplitude = amplitude
        self.frequency = frequency

    def get_reference_y(self, x):
        """
        Calculates the reference y-coordinate for a given x along the path.
        """
        return self.amplitude * np.sin(self.frequency * x)

    def get_reference_heading(self, x):
        """
        Calculates the tangent heading (angle) at a given x along the path.
        """
        return np.arctan(self.amplitude * self.frequency * np.cos(self.frequency * x))

class StraightLinePath:
    def __init__(self, y_ref=0.0):
        self.y_ref = y_ref

    def get_reference_y(self, x):
        """
        Returns a constant y-coordinate for the straight line.
        """
        return self.y_ref

    def get_reference_heading(self, x):
        """
        The heading for a straight horizontal line is always 0 radians.
        """
        return 0.0