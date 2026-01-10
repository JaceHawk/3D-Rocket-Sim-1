from MatrixMath import Vector3


class Triangle:
    def __init__(self, p1, p2, p3, flags=None):
        self.p = [p1, p2, p3]
        self.normal = Vector3()
        self.color = (255, 255, 255)

        if flags is None:
            self.edge_flags = [True, True, True]
        else:
            self.edge_flags = flags


class Mesh:
    def __init__(self):
        self.triangles = []  # List of Triangle objects

    @staticmethod
    def make_cube():
        mesh = Mesh()
        verts = [
            Vector3(-0.5, -0.5, -0.5), Vector3(-0.5, 0.5, -0.5),
            Vector3(0.5, 0.5, -0.5),   Vector3(0.5, -
                                               0.5, -0.5),

            Vector3(-0.5, -0.5, 0.5),  Vector3(-0.5, 0.5, 0.5),
            Vector3(0.5, 0.5, 0.5),    Vector3(
                0.5, -0.5, 0.5)
        ]

        # Indices (Connecting the dots)
        # Each group of 3 is one triangle
        indices = [
            0, 1, 2, 0, 2, 3,
            3, 2, 6, 3, 6, 7,
            7, 6, 5, 7, 5, 4,
            4, 5, 1, 4, 1, 0,
            1, 5, 6, 1, 6, 2,
            4, 0, 3, 4, 3, 7
        ]

        # Loop through indices 3 at a time
        for i in range(0, len(indices), 3):
            p1 = verts[indices[i]]
            p2 = verts[indices[i+1]]
            p3 = verts[indices[i+2]]
            mesh.triangles.append(Triangle(p1, p2, p3))

        return mesh

    @staticmethod
    def make_sphere(radius=1.0, rings=20, sectors=20):

        verts = []
        import math

        # Latitude (Rings) - Pi to 0
        for i in range(rings + 1):
            theta = (i / rings) * math.pi
            y = math.cos(theta) * radius
            r_sin = math.sin(theta) * radius  # Radius at this height

            # Longitude (Sectors) - 0 to 2*Pi
            for j in range(sectors + 1):
                phi = (j / sectors) * 2 * math.pi

                x = r_sin * math.cos(phi)
                z = r_sin * math.sin(phi)

                verts.append(Vector3(x, y, z))

        tris = []
        for i in range(rings):
            for j in range(sectors):
                # 2 Triangles per quad
                # p1 -- p2
                # |      |
                # p3 -- p4

                p1 = i * (sectors + 1) + j
                p2 = p1 + 1
                p3 = (i + 1) * (sectors + 1) + j
                p4 = p3 + 1

                # Triangle 1 (Top Left)
                tris.append(Triangle(verts[p1], verts[p2], verts[p3]))

                # Triangle 2 (Bottom Right)
                tris.append(Triangle(verts[p2], verts[p4], verts[p3]))

        for t in tris:
            # Simple flat shading normal calculation
            line1 = t.p[1] - t.p[0]
            line2 = t.p[2] - t.p[0]
            t.normal = line1.cross(line2).normalize()

        mesh = Mesh()
        mesh.triangles = tris
        return mesh

    @staticmethod
    def make_pyramid(base_size=1.0, height=2.0):
        mesh = Mesh()
        # Tip is at +Y (Up)
        tip = Vector3(0, height, 0)

        # Base corners (centered on x,z)
        b1 = Vector3(-base_size, 0, -base_size)
        b2 = Vector3(base_size, 0, -base_size)
        b3 = Vector3(base_size, 0, base_size)
        b4 = Vector3(-base_size, 0, base_size)

        # Triangular Sides
        # Wind them counter-clockwise so normals face out
        mesh.triangles.append(Triangle(tip, b3, b2))  # Front
        mesh.triangles.append(Triangle(tip, b2, b1))  # Left
        mesh.triangles.append(Triangle(tip, b1, b4))  # Back
        mesh.triangles.append(Triangle(tip, b4, b3))  # Right

        # Square Base (To be seen from behind)
        mesh.triangles.append(Triangle(b1, b2, b3))
        mesh.triangles.append(Triangle(b1, b3, b4))

        return mesh
