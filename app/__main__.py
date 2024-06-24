import pygame
import pygame_gui
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 900, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Crankshaft Mechanism Simulation")

# Pygame GUI Manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

SCREEN_OFFSET_X = 250
SCREEN_OFFSET_Y = 40
COL_X_POS = [WIDTH/3, 2*WIDTH/3]
COL_Y_POS = [HEIGHT*6/8, HEIGHT*6/8 + SCREEN_OFFSET_Y, HEIGHT*6/8 + 2*SCREEN_OFFSET_Y, HEIGHT*6/8 + 3*SCREEN_OFFSET_Y, HEIGHT*6/8 + 4*SCREEN_OFFSET_Y]

def cm_to_pixels(cm):
    return cm * 37.7952755906  # 1 cm = 37.7952755906 pixels

def pixels_to_cm(pixels):
    return pixels / 37.7952755906  # 1 pixel = 0.0264583333 cm

def kgFcm_to_Ncm(kgFcm):
    return kgFcm * 9.80665  # 1 kgF.cm = 9.80665 N.cm

def Ncm_to_kgFcm(Ncm):
    return Ncm / 9.80665  # 1 N.cm = 0.1019716213 kgF.cm

# Parameters (initial values)
T = 10  # Motor torque (kgF*cm)
r = cm_to_pixels(3)  # Crank radius (pixels)
l = cm_to_pixels(15)  # Connecting rod length (pixels)
OFFSET = cm_to_pixels(20)  # Offset for fixed rod end
omega = 2*math.pi  # Angular velocity (radians per frame)

# Sliders
torque_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, COL_Y_POS[0]), (200, 30)), 
    start_value=T, value_range=(1, 200), manager=manager)
radius_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, COL_Y_POS[1]), (200, 30)), 
    start_value=r, value_range=(cm_to_pixels(1), cm_to_pixels(20)), manager=manager)
rod_length_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, COL_Y_POS[2]), (200, 30)), 
    start_value=l, value_range=(cm_to_pixels(5), cm_to_pixels(30)), manager=manager)
omega_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, COL_Y_POS[3]), (200, 30)), 
    start_value=omega, value_range=(math.pi, 6 * math.pi), manager=manager)
time_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, COL_Y_POS[4]), (200, 30)), 
    start_value=1.0, value_range=(0.1, 3.0), manager=manager)  # Time controller slider

# Center of crankshaft
cx, cy = WIDTH // 2, HEIGHT // 2 - 50

# Simulation loop
running = True
theta = 0
clock = pygame.time.Clock()

# Make the pygame canvas draggable
is_dragging = False
offset_x = 0
offset_y = 0

# Zoom level
zoom_level = 1.0

# Function to calculate linear force
def calculate_force(torque, crank_radius):
    return torque / pixels_to_cm(crank_radius) * (math.sin(theta + math.pi/2))

# Function to calculate maximum linear force
def calculate_max_force(torque, crank_radius):
    return torque / pixels_to_cm(crank_radius)

# Function to calculate body spring force - Hooke's Law
def calculate_body_spring_force(constant, displacement):
    return constant * displacement

while running:
    time_delta = clock.tick(60) / 1000.0  # Frame time in seconds
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if screen.get_rect().collidepoint(event.pos):
                    is_dragging = True
                    offset_x = event.pos[0]
                    offset_y = event.pos[1]
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if is_dragging:
                x, y = event.pos
                dx = x - offset_x
                dy = y - offset_y
                cx += dx
                cy += dy
                offset_x = x
                offset_y = y
        elif event.type == pygame.MOUSEWHEEL:
            zoom_level += event.y * 0.1
            zoom_level = max(0.1, min(zoom_level, 5))  # Clamp the zoom level between 0.1 and 5
        manager.process_events(event)

    # Update parameters from sliders
    T = torque_slider.get_current_value()
    r = radius_slider.get_current_value()
    l = rod_length_slider.get_current_value()
    omega = omega_slider.get_current_value()
    time_scale = time_slider.get_current_value()  # Get the time scaling factor

    screen.fill(WHITE)

    # Calculate zoomed crank pin position
    zoomed_r = r * zoom_level
    crank_x = cx + zoomed_r * math.cos(theta)
    crank_y = cy + zoomed_r * math.sin(theta)

    # Calculate zoomed piston position
    piston_x = cx
    piston_y = cy + zoomed_r * math.sin(theta)

    # Calculate zoomed connecting rod end position (fixed rod end)
    zoomed_offset = OFFSET * zoom_level
    fixed_rod_x = cx
    fixed_rod_y = cy + zoomed_offset + zoomed_r * math.sin(theta)
    initial_fixed_rod_y = cy + zoomed_offset + zoomed_r * math.sin(-math.pi/2)
    zoomed_l = l * zoom_level

    # Calculate linear force
    max_force = calculate_max_force(T, r)
    force = calculate_force(T, r)

    # Draw the frame
    FRAME_OFFSET_X = cm_to_pixels(50) * zoom_level
    FRAME_OFFSET_Y = cm_to_pixels(60) * zoom_level
    SECOND_LEVEL_Y_OFFSET = cm_to_pixels(30) * zoom_level
    pygame.draw.line(screen, GREEN, (cx - FRAME_OFFSET_X, cy), (cx + FRAME_OFFSET_X, cy), int(20 * zoom_level)) # Top Frame
    pygame.draw.line(screen, GREEN, (cx - FRAME_OFFSET_X, cy), (cx - FRAME_OFFSET_X, cy + FRAME_OFFSET_Y), int(20 * zoom_level)) # Left Frame
    pygame.draw.line(screen, GREEN, (cx + FRAME_OFFSET_X, cy), (cx + FRAME_OFFSET_X, cy + FRAME_OFFSET_Y), int(20 * zoom_level)) # Right Frame
    pygame.draw.line(screen, GREEN, (cx - FRAME_OFFSET_X, cy + SECOND_LEVEL_Y_OFFSET), (cx + FRAME_OFFSET_X, cy + SECOND_LEVEL_Y_OFFSET), int(20 * zoom_level)) # Holder Frame

    # Draw crankshaft
    pygame.draw.line(screen, BLACK, (cx, cy), (crank_x, crank_y), int(10 * zoom_level))
    pygame.draw.circle(screen, RED, (int(crank_x), int(crank_y)), int(10 * zoom_level))
    pygame.draw.circle(screen, GREEN, (cx, cy), int(zoomed_r), int(5 * zoom_level))

    # Draw connecting rod
    pygame.draw.line(screen, BLUE, (crank_x, crank_y), (fixed_rod_x, fixed_rod_y - int(50 * zoom_level) + 2*zoomed_r), int(15*zoom_level))
    pygame.draw.circle(screen, BLACK, (int(fixed_rod_x), int(fixed_rod_y + 2*zoomed_r)), int(10 * zoom_level))

    # Draw fixed rod (constraining y-axis motion)
    pygame.draw.line(screen, RED, (piston_x, int(crank_y + 4*zoomed_r)), (piston_x, fixed_rod_y + 4*zoomed_r + zoomed_l), int(10 * zoom_level))

    # Draw a fixed "human body" on the edge of the fixed rod
    OFFSET_BODY_X = cm_to_pixels(35) * zoom_level # Assumption: Human body width is 70 cm
    OFFSET_BODY_Y = cm_to_pixels(10) * zoom_level # Assumption: Human body depth is 20 cm
    pygame.draw.rect(screen, BLACK, (piston_x - OFFSET_BODY_X, initial_fixed_rod_y + 4*zoomed_r + zoomed_l, int(2*OFFSET_BODY_X), int(2*OFFSET_BODY_Y)), 0)
    
    # Draw the displacement caused by piston on the edge of the fixed rod
    pygame.draw.rect(screen, RED, (piston_x - OFFSET_BODY_X/8, fixed_rod_y + 4*zoomed_r + zoomed_l, int(OFFSET_BODY_X/4), int(OFFSET_BODY_Y/4)), 0)

    # Display force and parameter values
    font = pygame.font.SysFont(None, 30)
    torque_text = font.render(f'Torque: {T:.2f} kgF.cm', True, BLACK)
    radius_text = font.render(f'Crank Radius: {pixels_to_cm(r):.2f} cm', True, BLACK)
    rod_length_text = font.render(f'Rod Length: {pixels_to_cm(l):.2f} cm', True, BLACK)
    omega_text = font.render(f'Angular Velocity: {omega:.2f} rad/s', True, BLACK)
    time_text = font.render(f'Time Scale: {time_scale:.2f}', True, BLACK)
    pump_frequency = font.render(f'Pump Frequency: {omega/(2*math.pi) * 60:.2f} press/minute', True, BLACK)

    # Column 2
    SPRING_CONSTANT = 2 # Spring constant in N/cm
    body_spring_force = calculate_body_spring_force(SPRING_CONSTANT, 3*math.sin(theta) + 3)
    body_spring_force_text = font.render(f'Body Spring Force: {body_spring_force:.2f} N', True, BLACK)
    
    TOTAL_FORCE = kgFcm_to_Ncm(force) # - body_spring_force
    force_text = font.render(f'Force: {TOTAL_FORCE:.2f} N', True, BLACK)
    max_force_text = font.render(f'Max Force: {kgFcm_to_Ncm(max_force):.2f} N', True, BLACK)

    screen.blit(torque_text, (COL_X_POS[0], COL_Y_POS[0]))
    screen.blit(radius_text, (COL_X_POS[0], COL_Y_POS[1]))
    screen.blit(rod_length_text, (COL_X_POS[0], COL_Y_POS[2]))
    screen.blit(omega_text, (COL_X_POS[0], COL_Y_POS[3]))
    screen.blit(time_text, (COL_X_POS[0], COL_Y_POS[4]))

    screen.blit(force_text, (COL_X_POS[1], COL_Y_POS[0]))
    screen.blit(max_force_text, (COL_X_POS[1], COL_Y_POS[1]))
    screen.blit(body_spring_force_text, (COL_X_POS[1], COL_Y_POS[2]))
    screen.blit(pump_frequency, (COL_X_POS[1], COL_Y_POS[3]))

    # Update GUI elements
    manager.update(time_delta)
    manager.draw_ui(screen)

    # Update display
    pygame.display.flip()

    # Update angle
    theta += omega * time_delta * time_scale
    if theta >= 2 * math.pi:
        theta -= 2 * math.pi

pygame.quit()
