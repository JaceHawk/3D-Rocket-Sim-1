import math
import pygame
from MatrixMath import Vector3, Matrix4


class Spacecraft:
    def __init__(self, x=0, y=0, z=0):
        # State Vectors
        self.pos = Vector3(x, y, z)
        self.vel = Vector3(0, 0, 0)

        # Orientation
        self.yaw = 0.0   # Left/Right
        self.pitch = 0.0  # Up/Down

        # Physics Constants
        self.acceleration = 0.05

    # --- GRAVITY APPLICATION ---

    def apply_gravity(self, planet, dt=1/60):
        dx = planet.pos.x - self.pos.x
        dy = planet.pos.y - self.pos.y
        dz = planet.pos.z - self.pos.z

        dist_sq = dx*dx + dy*dy + dz*dz
        dist = math.sqrt(dist_sq)

        if dist < planet.radius:
            return

        # F = G * M / r^2
        accel_mag = planet.mass / dist_sq

        # Apply Acceleration * Time (dt)
        step_accel = accel_mag * dt

        self.vel.x += (dx / dist) * step_accel
        self.vel.y += (dy / dist) * step_accel
        self.vel.z += (dz / dist) * step_accel

    # --- COLLISION CHECKING ---
    def check_collision(self, planet):
        # 1. Vector from Planet to Ship
        dx = self.pos.x - planet.pos.x
        dy = self.pos.y - planet.pos.y
        dz = self.pos.z - planet.pos.z

        dist_sq = dx*dx + dy*dy + dz*dz
        dist = math.sqrt(dist_sq)

        # 2. Define the "Surface"
        COLLISION_BUFFER = 1.0
        surface_level = planet.radius + COLLISION_BUFFER

        # 3. Check for Impact
        if dist < surface_level:
            # --- CRASH LOGIC ---

            # A. Kill Velocity
            self.vel = Vector3(0, 0, 0)

            # B. Push Out (The "Floor")
            if dist > 0:  # Prevent divide by zero
                nx = dx / dist
                ny = dy / dist
                nz = dz / dist

                self.pos.x = planet.pos.x + (nx * surface_level)
                self.pos.y = planet.pos.y + (ny * surface_level)
                self.pos.z = planet.pos.z + (nz * surface_level)

    # --- UPDATE FUNCTION ---
    def update(self, keys, mouse_delta, dt=1.0, controls_enabled=True):
        # 1. ROTATION (Independent of Time Warp)
        if controls_enabled:
            dx, dy = mouse_delta
            sensitivity = 0.2
            self.yaw += dx * sensitivity
            self.pitch -= dy * sensitivity

        # Clamp Pitch
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        # 2. CALCULATE FORWARD (Using Trig)
        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)

        fx = math.sin(rad_yaw) * math.cos(rad_pitch)
        fy = -math.sin(rad_pitch)
        fz = math.cos(rad_yaw) * math.cos(rad_pitch)
        forward = Vector3(fx, fy, fz)

        # 3. THRUST (Scaled by dt)
        # Engine gets stronger with time warp to keep up
        thrust_amt = self.acceleration * dt

        if controls_enabled:
            if keys[pygame.K_w]:
                self.vel = self.vel + (forward * thrust_amt)
            if keys[pygame.K_s]:
                self.vel = self.vel - (forward * thrust_amt)

        # 4. PHYSICS (Position = Velocity * Time)
        self.pos = self.pos + (self.vel * dt)
