import pygame
from Mesh import Mesh
from Camera import Camera
from Pipeline import Pipeline
from Spacecraft import Spacecraft
from ObjectLoader import ObjectLoader
from Space import Starfield, Planet
from MatrixMath import Vector3, Matrix4

# --- SETUP ---
pygame.init()
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
HUD_font = pygame.font.Font("Y224-2vdae.ttf", 25)
small_font = pygame.font.Font("Y224-2vdae.ttf", 11)
# LOCK MOUSE (Hide cursor and get input)
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# --- INIT ENGINE OBJECTS ---
player = Spacecraft(0, 0, 0)
mesh_ship = ObjectLoader.load_obj("ship.obj")
camera = Camera()
starfield = Starfield(num_stars=1500)  # 1500 stars
pipeline = Pipeline(WIDTH, HEIGHT)
mesh_arrow = Mesh.make_pyramid(base_size=0.5, height=2.0)
time_warp = 1.0
show_vectors = True
# Planet Info:
# 1 Unit = 1 kilometer
# Position (0, 7000, 0)
# Radius 6371 km
# μ = 398600 km^3 /s^2
planet = Planet(0, 7000, 0, 6371, 398600)

# Generate Sphere
# Resolution (25x25)
mesh_planet = Mesh.make_sphere(radius=1.0, rings=25, sectors=25)


# --- RENDER FUNCTIONS ---
def render_mesh(screen, pipeline, mesh, camera, world_matrix, face_color=(255, 255, 255), wire_color=(0, 0, 0), draw_wires=True):

    processed_tris = pipeline.process_mesh(
        mesh, camera, world_matrix, base_color=face_color)
    # 2. Draw the triangles
    for tri_data in processed_tris:
        tri_points = tri_data[0]
        tri_color = tri_data[2]
        flags = tri_data[3]

        p1 = (tri_points[0].x, tri_points[0].y)
        p2 = (tri_points[1].x, tri_points[1].y)
        p3 = (tri_points[2].x, tri_points[2].y)

        # Draw faces (color calculated by pipeline)
        pygame.draw.polygon(screen, tri_color, [p1, p2, p3])

        # Wireframe
        if draw_wires:
            if flags[0]:
                pygame.draw.line(screen, wire_color, p1, p2, 1)
            if flags[1]:
                pygame.draw.line(screen, wire_color, p2, p3, 1)
            if flags[2]:
                pygame.draw.line(screen, wire_color, p3, p1, 1)
    return


def render_stars(screen, pipeline, stars, camera):
    # Create Rotation Matrices
    mat_rot_y = Matrix4.make_rotation_y(-camera.yaw)
    mat_rot_x = Matrix4.make_rotation_x(camera.pitch)

    # Combined Rotation Matrix
    mat_view_rot = mat_rot_x @ mat_rot_y

    # Iterate through every star
    white = (255, 255, 255)
    width = pipeline.width
    height = pipeline.height

    for star_vec in stars:
        # Apply View Rotation
        p_view = mat_view_rot.multiply_vector(star_vec)

        # Check if it's behind us
        # Rely on the Projection Matrix for this
        if p_view.z < 0.1:
            continue  # Star is behind player, no need to draw

        # Apply Projection
        p_proj = pipeline.mat_proj.multiply_vector(p_view)

        # Perspective Divide
        if p_proj.w != 0:
            x = p_proj.x / p_proj.w
            y = p_proj.y / p_proj.w
        else:
            continue

        # Screen Coordinates $ Draw
        screen_x = (x + 1.0) * 0.5 * width
        screen_y = (1.0 - y) * 0.5 * height

        if 0 <= screen_x < width and 0 <= screen_y < height:
            screen.set_at((int(screen_x), int(screen_y)), white)


def draw_vector_3d(screen, pipeline, camera, start_pos, vector, color):

    # Draw the Shaft (Line)
    end_pos = start_pos + vector

    start_screen = pipeline.project_point(start_pos, camera)
    end_screen = pipeline.project_point(end_pos, camera)

    if start_screen and end_screen:
        # Dynamic Thickness: Thicker when closer (Simple depth cue)
        # start_screen[2] is the Z-depth returned by project_point
        depth = start_screen[2]
        thickness = max(1, int(100 / depth)) if depth > 0 else 1

        pygame.draw.line(screen, color,
                         (start_screen[0], start_screen[1]),
                         (end_screen[0], end_screen[1]), thickness)

    # Rotation
    mat_rot = Matrix4.make_alignment(vector)

    # Translation: Move to tip of line
    mat_trans = Matrix4.make_translation(end_pos.x, end_pos.y, end_pos.z)

    scale = 1.0  # Adjustable size factor
    mat_scale = Matrix4.make_scaling(scale, scale, scale)

    # Position * Rotation * Scale
    mat_arrow = mat_trans @ (mat_rot @ mat_scale)

    # Render the arrowhead mesh
    render_mesh(screen, pipeline, mesh_arrow, camera, mat_arrow,
                face_color=color, wire_color=color, draw_wires=False)


# --- MAIN LOOP ---
running = True
while running:
    # 1. EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # TIME WARP CONTROLS
            if event.key == pygame.K_r:
                time_warp = 1.0    # Reset
            if event.key == pygame.K_t:
                time_warp = 10.0   # Fast
            if event.key == pygame.K_y:
                time_warp = 50.0  # Faster
            # CAMERA MODE TOGGLE
            if event.key == pygame.K_c:
                camera.switch_mode()
            # TOGGLE VECTORS
            if event.key == pygame.K_v:
                show_vectors = not show_vectors
        if event.type == pygame.MOUSEWHEEL:
            if camera.mode == 'follow' or 'chase':
                # event.y is +1 for scroll up, -1 for scroll down
                # Multiply by some factor for smooth zooming
                camera.adjust_distance(-event.y * 2.0)
    # 2. PHYSICS UPDATE
    keys = pygame.key.get_pressed()
    mouse_delta = pygame.mouse.get_rel()
    player.apply_gravity(planet, dt=time_warp)
    player.update(keys, mouse_delta, dt=time_warp,
                  controls_enabled=(camera.mode == 'chase'))
    player.check_collision(planet)

    # HUD info calculations
    altitude = player.pos.distance_to(planet.pos) - planet.radius
    speed = player.vel.magnitude() * 60
    hud_fps = HUD_font.render(
        f"FPS: {int(clock.get_fps())}", True, (255, 255, 0))
    hud_altitude = HUD_font.render(
        f"Altitude: {altitude:7.1f}  km", True, (255, 255, 0))
    hud_speed = HUD_font.render(
        f"Speed: {speed:10.1f}  km/s", True, (255, 255, 0))
    hud_camera_mode = small_font.render(
        f"Camera Mode: {camera.mode.upper()}", True, (255, 0, 0))
    hud_time_warp = small_font.render(
        f"Time Warp: {time_warp:.1f}x", True, (255, 0, 255))
    # 3. CAMERA UPDATE
    if camera.mode == 'chase':
        camera.chase(player)
    elif camera.mode == 'free':
        camera.update(keys, mouse_delta)
    elif camera.mode == 'follow':
        camera.follow(player, mouse_delta)
    # 4. RENDER
    screen.fill((0, 0, 0))
    # --- DRAW BACKGROUND STARS ---
    render_stars(screen, pipeline, starfield.stars, camera)
    # --- DRAW PLANET ---
    scale = planet.radius
    mat_scale = Matrix4.make_scaling(scale, scale, scale)
    mat_scale.m = [
        [scale, 0, 0, 0],
        [0, scale, 0, 0],
        [0, 0, scale, 0],
        [0, 0, 0, 1]
    ]

    mat_trans = Matrix4.make_translation(
        planet.pos.x, planet.pos.y, planet.pos.z)

    # Model Matrix = Translate * Scale
    mat_planet = mat_trans @ mat_scale

    # --- DRAW PLAYER ---
    mat_fix = Matrix4.make_rotation_x(90)  # Rocket model faces +X by default
    mat_rot_y = Matrix4.make_rotation_y(player.yaw)
    mat_rot_x = Matrix4.make_rotation_x(player.pitch)
    mat_trans = Matrix4.make_translation(
        player.pos.x, player.pos.y, player.pos.z)

    player_matrix = mat_trans @ (mat_rot_y @ mat_rot_x) @ mat_fix
    # RENDER ORDER BASED ON CAMERA DISTANCE
    if camera.pos.distance_to(planet.pos) < camera.pos.distance_to(player.pos):
        render_mesh(screen, pipeline, mesh_ship, camera, player_matrix,
                    face_color=(150, 150, 150), wire_color=(255, 255, 255))

        render_mesh(screen, pipeline, mesh_planet, camera, mat_planet,
                    face_color=(0, 0, 200), wire_color=(0, 150, 0), draw_wires=False)
    elif camera.pos.distance_to(planet.pos) >= camera.pos.distance_to(player.pos):
        render_mesh(screen, pipeline, mesh_planet, camera, mat_planet,
                    face_color=(0, 0, 200), wire_color=(0, 150, 0), draw_wires=False)

        render_mesh(screen, pipeline, mesh_ship, camera, player_matrix,
                    face_color=(150, 150, 150), wire_color=(255, 255, 255))

    # --- VECTOR VISUALIZATION ---
    if show_vectors:
        # Velocity (Green)
        draw_vector_3d(screen, pipeline, camera, player.pos,
                       player.vel * 2.0, (0, 255, 0))

        # Gravity (Red)
        grav_dir = (planet.pos - player.pos).normalize() * 12.5
        draw_vector_3d(screen, pipeline, camera,
                       player.pos, grav_dir, (255, 0, 0))

        # Heading / Thrust (Yellow)
        # Recalculated with same math as Spacecraft.py
        import math
        rad_yaw = math.radians(player.yaw)
        rad_pitch = math.radians(player.pitch)
        fx = math.sin(rad_yaw) * math.cos(rad_pitch)
        fy = -math.sin(rad_pitch)
        fz = math.cos(rad_yaw) * math.cos(rad_pitch)
        forward_vec = Vector3(fx, fy, fz) * 5.0

        draw_vector_3d(screen, pipeline, camera, player.pos,
                       forward_vec, (255, 255, 0))
        # --- DRAW LEGEND ---
        # Draw on the right side of the screen
        legend_x = 900
        legend_y = 200  # A bit lower down

        vec_font = small_font

        # Guide Text
        text_guide = vec_font.render("VECTORS:", True, (255, 255, 255))
        screen.blit(text_guide, (legend_x, legend_y - 20))
        # Green Text
        text_vel = vec_font.render("VELOCITY", True, (0, 255, 0))
        screen.blit(text_vel, (legend_x, legend_y))

        # Red Text
        text_grav = vec_font.render("GRAVITY", True, (255, 0, 0))
        screen.blit(text_grav, (legend_x, legend_y + 15))

        # Yellow Text
        text_head = vec_font.render("HEADING", True, (255, 255, 0))
        screen.blit(text_head, (legend_x, legend_y + 30))

    # DRAW HUD
    screen.blit(hud_altitude, (10, 10))
    screen.blit(hud_speed, (10, 35))
    screen.blit(hud_time_warp, (10, 135))
    screen.blit(hud_camera_mode, (10, 160))
    screen.blit(small_font.render("W / D = Forward / Back",
                True, (255, 0, 0)), (10, HEIGHT - 90))
    screen.blit(small_font.render("Mouse = Look",
                True, (255, 0, 0)), (10, HEIGHT - 72))
    screen.blit(small_font.render("C = Switch Camera",
                True, (255, 0, 0)), (10, HEIGHT - 54))
    screen.blit(small_font.render("R / T / Y = Time Warp",
                True, (255, 0, 0)), (10, HEIGHT - 36))
    screen.blit(small_font.render("V = Toggle Vectors",
                True, (255, 0, 0)), (10, HEIGHT - 18))
    screen.blit(hud_fps, (WIDTH - 200, 10))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
