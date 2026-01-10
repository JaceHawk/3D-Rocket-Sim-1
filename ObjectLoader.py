from MatrixMath import Vector3
from Mesh import Mesh, Triangle


class ObjectLoader:
    @staticmethod
    def load_obj(filename):
        mesh = Mesh()
        verts = []

        try:
            with open(filename, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    parts = line.split()
                    if not parts:
                        continue

                    if parts[0] == 'v':
                        verts.append(
                            Vector3(float(parts[1]), float(parts[2]), float(parts[3])))

                    elif parts[0] == 'f':
                        # Parse all vertices in the line first
                        face_indices = []
                        for i in range(1, len(parts)):
                            # Split "1/1/1" -> "1"
                            val = parts[i].split('/')[0]
                            face_indices.append(int(val))

                        count = len(face_indices)
                        for i in range(2, count):
                            i0 = face_indices[0] - 1
                            i1 = face_indices[i-1] - 1
                            i2 = face_indices[i] - 1

                            p1 = verts[i0]
                            p2 = verts[i1]
                            p3 = verts[i2]

                            # Edge 0 (p1->p2): Real ONLY if it's the first triangle in the fan
                            e0 = True if (i == 2) else False

                            # Edge 1 (p2->p3): Always Real (it walks the rim of the polygon)
                            e1 = True

                            # Edge 2 (p3->p1): Real ONLY if it's the last triangle in the fan
                            e2 = True if (i == count - 1) else False

                            # Create triangle with these flags
                            mesh.triangles.append(
                                Triangle(p1, p2, p3, flags=[e0, e1, e2]))

            print(f"Loaded {filename}: {len(mesh.triangles)} triangles.")
            return mesh

        except FileNotFoundError:
            print(f"ERROR: Could not find {filename}. Loading Cube.")
            return Mesh.make_cube()
