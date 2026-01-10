# Python 3D Orbital Physics Engine

A custom-built 3D rendering and physics engine written in pure Python. This project demonstrates a from-scratch implementation of the graphics pipeline (rasterization, matrix transformations) and Newtonian orbital mechanics without relying on external game engines or 3D libraries (like OpenGL or Unity).

## Features

### 1. Custom Graphics Pipeline
* **Software Rasterizer:** Implements 3D-to-2D projection, viewport scaling, and wireframe/filled polygon rendering using Pygame only for the final pixel buffer.
* **Matrix Mathematics:** Custom `Matrix4` and `Vector3` classes handling Translation, Rotation, Scaling, and Perspective Projection.
* **Visuals:** Supports flat shading (Dot Product lighting), back-face culling, and z-depth sorting (Painter's Algorithm).

### 2. Physics Simulation
* **Newtonian Gravity:** Implements Universal Gravitation ($F = G \frac{m_1 m_2}{r^2}$) for realistic orbital trajectories.
* **Collision Detection:** Simple radial collision detection with surface constraint resolution.
* **Vector Visualization:** Real-time rendering of Velocity, Gravity, and Heading vectors for debugging flight forces.

### 3. Flight Systems
* **5-DOF Control:** Full pitch, yaw, and thrust controls.
* **Time Warp:** Dynamic time-step simulation allowing 1x to 50x simulation speeds.
* **Instrumentation:** Heads-Up Display (HUD) showing altitude, orbital velocity, and camera modes.

## Controls

| Key | Action |
| :--- | :--- |
| **W / S** | Pitch Nose Down / Up |
| **Mouse** | Look Around (Yaw / Pitch) |
| **R** | Reset Time Warp (1x) |
| **T** | Time Warp (10x) |
| **Y** | Time Warp (50x) |
| **V** | Toggle Physics Vector Overlay |
| **C** | Switch Camera Mode (Chase / Follow / Free) |
| **ESC** | Exit Simulation |

## Technical Implementation

The engine uses a Right-Handed Coordinate System. The core loop performs the following steps:
1.  **Physics Step:** Applies gravity forces and updates velocity/position vectors.
2.  **Camera Step:** Generates the View Matrix based on camera mode (Euler Angles).
3.  **Pipeline Step:**
    * Transforms local mesh vertices to World Space.
    * Applies View and Projection matrices.
    * Performs Perspective Division ($x/w, y/w$).
    * Rasterizes triangles to the screen buffer.

## Dependencies
* Python 3.x
* Pygame (for window management and 2D drawing primitives)
