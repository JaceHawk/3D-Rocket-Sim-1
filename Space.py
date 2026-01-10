import random
import math
from MatrixMath import Vector3


class Starfield:
    def __init__(self, num_stars=1000):
        self.stars = []

        for _ in range(num_stars):
            # Generate random spherical coordinates
            # Yaw: 0 to 360
            yaw = random.uniform(0, 360)
            # Pitch: -90 to 90
            pitch = random.uniform(-90, 90)

            # Convert to Cartesian (x, y, z) direction vector
            rad_yaw = math.radians(yaw)
            rad_pitch = math.radians(pitch)

            x = math.sin(rad_yaw) * math.cos(rad_pitch)
            y = -math.sin(rad_pitch)
            z = math.cos(rad_yaw) * math.cos(rad_pitch)

            # Store this normalized vector
            self.stars.append(Vector3(x, y, z))


class Planet:
    def __init__(self, x, y, z, radius, mass):
        self.pos = Vector3(x, y, z)
        self.radius = radius
        self.mass = mass  # For Gravitational calculations
