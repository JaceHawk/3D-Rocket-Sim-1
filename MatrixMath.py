import math


class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = 1.0  # For matrix operations

    # --- ARITHMETIC OPERATIONS ---

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __truediv__(self, scalar):
        if scalar == 0:
            return Vector3()
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

    def __repr__(self):
        return f"Vec3({self.x}, {self.y}, {self.z})"

    # --- VECTOR OPERATIONS ---

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        m = self.magnitude()
        if m == 0:
            return Vector3()
        return self / m

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        x = self.y * other.z - self.z * other.y
        y = self.z * other.x - self.x * other.z
        z = self.x * other.y - self.y * other.x
        return Vector3(x, y, z)

    def distance_to(self, other):
        return (self - other).magnitude()


class Matrix4:
    def __init__(self):
        # Initialize as identity matrix:
        # [ 1 0 0 0 ]
        # [ 0 1 0 0 ]
        # [ 0 0 1 0 ]
        # [ 0 0 0 1 ]
        self.m = [[0.0]*4 for _ in range(4)]
        self.m[0][0] = 1.0
        self.m[1][1] = 1.0
        self.m[2][2] = 1.0
        self.m[3][3] = 1.0

    def __matmul__(self, other):
        # Uses the @ operator for matrix multiplication
        result = Matrix4()
        for i in range(4):
            for j in range(4):
                result.m[i][j] = sum(self.m[i][k] * other.m[k][j]
                                     for k in range(4))
        return result

    def multiply_vector(self, vec):
        x = vec.x * self.m[0][0] + vec.y * self.m[0][1] + \
            vec.z * self.m[0][2] + vec.w * self.m[0][3]
        y = vec.x * self.m[1][0] + vec.y * self.m[1][1] + \
            vec.z * self.m[1][2] + vec.w * self.m[1][3]
        z = vec.x * self.m[2][0] + vec.y * self.m[2][1] + \
            vec.z * self.m[2][2] + vec.w * self.m[2][3]
        w = vec.x * self.m[3][0] + vec.y * self.m[3][1] + \
            vec.z * self.m[3][2] + vec.w * self.m[3][3]

        result = Vector3(x, y, z)
        result.w = w  # Store w manually
        return result

    # --- STATIC GENERATORS ---

    @staticmethod
    def make_translation(x, y, z):
        mat = Matrix4()
        mat.m[0][3] = x
        mat.m[1][3] = y
        mat.m[2][3] = z
        return mat

    @staticmethod
    def make_rotation_z(angle_deg):
        mat = Matrix4()
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        mat.m[0][0] = cos_a
        mat.m[0][1] = -sin_a
        mat.m[1][0] = sin_a
        mat.m[1][1] = cos_a
        return mat

    @staticmethod
    def make_rotation_x(angle_deg):
        mat = Matrix4()
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        mat.m[1][1] = cos_a
        mat.m[1][2] = -sin_a
        mat.m[2][1] = sin_a
        mat.m[2][2] = cos_a
        return mat

    @staticmethod
    def make_rotation_y(angle_deg):
        mat = Matrix4()
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        mat.m[0][0] = cos_a
        mat.m[0][2] = sin_a
        mat.m[2][0] = -sin_a
        mat.m[2][2] = cos_a
        return mat

    @staticmethod
    def make_projection(fov, aspect_ratio, near, far):
        # This convertes a 3D point to 2D using perspective projection
        mat = Matrix4()
        fov_rad = 1.0 / math.tan(math.radians(fov) / 2.0)

        mat.m[0][0] = aspect_ratio * fov_rad
        mat.m[1][1] = fov_rad
        mat.m[2][2] = far / (far - near)
        mat.m[2][3] = (-far * near) / (far - near)
        mat.m[3][2] = 1.0
        mat.m[3][3] = 0.0
        return mat

    @staticmethod
    def make_scaling(x, y, z):
        matrix = Matrix4()
        matrix.m = [
            [x, 0.0, 0.0, 0.0],
            [0.0, y, 0.0, 0.0],
            [0.0, 0.0, z, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ]
        return matrix

    @staticmethod
    def make_alignment(direction, up_ref=None):
        # Creates a rotation matrix that aligns the Y-axis (Up)
        # to the given 'direction' vector.

        # The Target Y-Axis
        new_y = direction.normalize()

        # Compute X-Axis
        if up_ref is None:
            up_ref = Vector3(0, 1, 0)

        # Handle the edge case where looking straight up/down
        if abs(new_y.dot(up_ref)) > 0.99:
            up_ref = Vector3(0, 0, 1)  # Switch reference

        new_x = new_y.cross(up_ref).normalize()

        # Compute Z-Axis
        # Z is perpendicular to both X and Y
        new_z = new_x.cross(new_y).normalize()

        # 4. Build Matrix
        # [ Xx Yx Zx 0 ]
        # [ Xy Yy Zy 0 ]
        # [ Xz Yz Zz 0 ]
        # [ 0  0  0  1 ]
        mat = Matrix4()
        mat.m = [
            [new_x.x, new_y.x, new_z.x, 0],
            [new_x.y, new_y.y, new_z.y, 0],
            [new_x.z, new_y.z, new_z.z, 0],
            [0,       0,       0,       1]
        ]
        return mat
