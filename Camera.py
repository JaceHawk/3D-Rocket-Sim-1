from MatrixMath import Vector3, Matrix4
import math
import pygame


class Camera:
    def __init__(self):
        self.mode = 'chase'  # Begin camera in chase
        self.pos = Vector3(0, 0, -10)
        self.yaw = 0.0
        self.pitch = 0.0

        self.follow_distance = 15.0  # Current default
        self.min_distance = 5.0      # Minimum zoom
        self.max_distance = 1000.0    # Maximum zoom

    def get_view_matrix(self):
        mat_trans = Matrix4.make_translation(
            -self.pos.x, -self.pos.y, -self.pos.z)
        mat_rot_y = Matrix4.make_rotation_y(-self.yaw)
        mat_rot_x = Matrix4.make_rotation_x(-self.pitch)
        return mat_rot_x @ mat_rot_y @ mat_trans

    def chase(self, target):
        # 1. COPY ROTATION
        self.yaw = target.yaw
        self.pitch = target.pitch

        dist = self.follow_distance

        # 2. CALCULATE 3D FORWARD VECTOR
        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)

        # Rotate a forward vector (0,0,1) by Pitch(X) then Yaw(Y)
        # x = sin(yaw) * cos(pitch)
        # y = -sin(pitch)
        # z = cos(yaw) * cos(pitch)
        fx = math.sin(rad_yaw) * math.cos(rad_pitch)
        fy = -math.sin(rad_pitch)
        fz = math.cos(rad_yaw) * math.cos(rad_pitch)

        # 3. SET POSITION
        self.pos.x = target.pos.x - (fx * dist)
        self.pos.y = target.pos.y - (fy * dist)
        self.pos.z = target.pos.z - (fz * dist)

    def update(self, keys, mouse_delta):
        # 1. ROTATION
        dx, dy = mouse_delta
        sensitivity = 0.2
        self.yaw += dx * sensitivity
        self.pitch -= dy * sensitivity
        # Clamp Pitch
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        # 2. MOVEMENT SPEED
        base_speed = 60
        # TURBO MODE: Hold L-SHIFT to go 10x faster
        if keys[pygame.K_LSHIFT]:
            speed = base_speed * 10.0
        # PRECISION MODE: Hold L-CTRL to go 3x slower
        elif keys[pygame.K_LCTRL]:
            speed = base_speed * 1/3
        else:
            speed = base_speed
        # Update position based on WASD
        if keys[pygame.K_w]:
            self.pos.x += math.sin(math.radians(self.yaw)) * speed
            self.pos.z += math.cos(math.radians(self.yaw)) * speed
        if keys[pygame.K_s]:
            self.pos.x -= math.sin(math.radians(self.yaw)) * speed
            self.pos.z -= math.cos(math.radians(self.yaw)) * speed
        if keys[pygame.K_a]:
            self.pos.x -= math.cos(math.radians(self.yaw)) * speed
            self.pos.z += math.sin(math.radians(self.yaw)) * speed
        if keys[pygame.K_d]:
            self.pos.x += math.cos(math.radians(self.yaw)) * speed
            self.pos.z -= math.sin(math.radians(self.yaw)) * speed
        # E and Q for vertical movement
        if keys[pygame.K_e]:
            self.pos.y -= speed
        if keys[pygame.K_q]:
            self.pos.y += speed

    def follow(self, target, mouse_delta):
        # Update rotation from mouse (same as free camera)
        dx, dy = mouse_delta
        sensitivity = 0.2
        self.yaw += dx * sensitivity
        self.pitch -= dy * sensitivity

        # Clamp pitch
        self.pitch = max(-89.0, min(89.0, self.pitch))

        # Position stays with ship (with offset behind)
        dist = self.follow_distance

        # Calculate backward vector from camera's OWN rotation
        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)

        fx = math.sin(rad_yaw) * math.cos(rad_pitch)
        fy = -math.sin(rad_pitch)
        fz = math.cos(rad_yaw) * math.cos(rad_pitch)

        # Position camera behind where it's looking, centered on ship
        self.pos.x = target.pos.x - (fx * dist)
        self.pos.y = target.pos.y - (fy * dist)
        self.pos.z = target.pos.z - (fz * dist)

    def adjust_distance(self, delta):
        # delta positive for scroll up, negative for scroll down
        self.follow_distance += delta

        # Clamp to min/max
        if self.follow_distance < self.min_distance:
            self.follow_distance = self.min_distance
        if self.follow_distance > self.max_distance:
            self.follow_distance = self.max_distance

    def switch_mode(self):
        if self.mode == 'chase':
            self.mode = 'follow'
        elif self.mode == 'follow':
            self.mode = 'free'
        elif self.mode == 'free':
            self.mode = 'chase'
