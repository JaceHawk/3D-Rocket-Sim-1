import math
from MatrixMath import Matrix4, Vector3


class Pipeline:
    def __init__(self, width, height, fov=90.0):
        self.width = width
        self.height = height
        self.aspect_ratio = height / width  # NOTE: Depending on matrix math, might be w/h
        self.fov = fov

        # 1. SETUP PROJECTION MATRIX
        self.mat_proj = Matrix4.make_projection(
            fov, self.aspect_ratio, 0.1, 1000.0)

    def process_mesh(self, mesh, camera, world_matrix, base_color=(255, 255, 255)):
        triangles_to_draw = []

        # --- STEP 1: DEFINE WORLD MATRICES ---
        # Don't calculate rotations here.
        # Main.py did the physics math and sent us the final matrix.
        mat_world = world_matrix

        mat_view = camera.get_view_matrix()

        # LOOP THROUGH ALL TRIANGLES IN THE MESH
        for tri in mesh.triangles:
            tri_projected = [Vector3(), Vector3(), Vector3()]

            p0_trans = mat_world.multiply_vector(tri.p[0])
            p1_trans = mat_world.multiply_vector(tri.p[1])
            p2_trans = mat_world.multiply_vector(tri.p[2])

            p0_view = mat_view.multiply_vector(p0_trans)
            p1_view = mat_view.multiply_vector(p1_trans)
            p2_view = mat_view.multiply_vector(p2_trans)

            line1 = p1_view - p0_view
            line2 = p2_view - p0_view
            normal_view = line1.cross(line2).normalize()
            camera_ray = p0_view.normalize()
            if normal_view.dot(camera_ray) > 0:
                continue
            if p0_view.z < 0.1 or p1_view.z < 0.1 or p2_view.z < 0.1:
                continue

            p0_proj = self.mat_proj.multiply_vector(p0_view)
            p1_proj = self.mat_proj.multiply_vector(p1_view)
            p2_proj = self.mat_proj.multiply_vector(p2_view)

            if p0_proj.w != 0:
                p0_proj = p0_proj / p0_proj.w
            if p1_proj.w != 0:
                p1_proj = p1_proj / p1_proj.w
            if p2_proj.w != 0:
                p2_proj = p2_proj / p2_proj.w

            p0_proj.x = (p0_proj.x + 1.0) * 0.5 * self.width
            p0_proj.y = (p0_proj.y + 1.0) * 0.5 * self.height
            p1_proj.x = (p1_proj.x + 1.0) * 0.5 * self.width
            p1_proj.y = (p1_proj.y + 1.0) * 0.5 * self.height
            p2_proj.x = (p2_proj.x + 1.0) * 0.5 * self.width
            p2_proj.y = (p2_proj.y + 1.0) * 0.5 * self.height

            tri_projected[0] = p0_proj
            tri_projected[1] = p1_proj
            tri_projected[2] = p2_proj

            # Store the result
            tri_projected[0] = p0_proj
            tri_projected[1] = p1_proj
            tri_projected[2] = p2_proj

            # Calculate max depth (z)
            avg_depth = max(p0_view.z, p1_view.z, p2_view.z)

            # CALCULATE LIGHTING
            # 1. Define Light Direction (Forward into the scene)
            light_dir = Vector3(0.0, 0.0, -1.0)
            light_dir = light_dir.normalize()

            line1 = p1_trans - p0_trans
            line2 = p2_trans - p0_trans
            normal = line1.cross(line2).normalize()

            dp = normal.dot(light_dir)
            brightness = max(0.2, dp)

            final_color = (
                int(base_color[0] * brightness),
                int(base_color[1] * brightness),
                int(base_color[2] * brightness)
            )

            # Fetching flags from the original triangle 'tri'
            triangles_to_draw.append(
                (tri_projected, avg_depth, final_color, tri.edge_flags))

        # --- SORTING (Painter's Algorithm) ---
        triangles_to_draw.sort(key=lambda x: x[1], reverse=True)

        return triangles_to_draw

    def project_point(self, point, camera):
        # 1. View Transform
        mat_view = camera.get_view_matrix()
        p_view = mat_view.multiply_vector(point)

        # 2. NEAR PLANE CLIP (Safety)
        # If point is behind the camera, don't draw it.
        if p_view.z < 1.0:
            return None

        # 3. Projection Transform
        p_proj = self.mat_proj.multiply_vector(p_view)

        # 4. Perspective Divide
        if p_proj.w != 0:
            p_proj.x /= p_proj.w
            p_proj.y /= p_proj.w
        else:
            return None

        # 5. Screen Scale
        screen_x = (p_proj.x + 1.0) * 0.5 * self.width
        screen_y = (1.0 + p_proj.y) * 0.5 * self.height

        return (screen_x, screen_y, p_view.z)
