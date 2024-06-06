import pygame
import pygame_gui
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Crankshaft Mechanism Simulation")

# Pygame GUI Manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

def cm_to_pixels(cm):
    return cm * 37.7952755906  # 1 cm = 37.7952755906 pixels

# Parameters (initial values)
T = 10  # Motor torque (N*m)
r = cm_to_pixels(6)  # Crank radius (pixels)
l = cm_to_pixels(20)  # Connecting rod length (pixels)
OFFSET = cm_to_pixels(6)  # Offset for fixed rod end
omega = 0.05  # Angular velocity (radians per frame)

# Sliders
torque_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 520), (200, 30)), 
    start_value=T, value_range=(1, 100), manager=manager)
radius_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 560), (200, 30)), 
    start_value=r, value_range=(cm_to_pixels(1), cm_to_pixels(20)), manager=manager)
rod_length_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 600), (200, 30)), 
    start_value=l, value_range=(cm_to_pixels(10), cm_to_pixels(50)), manager=manager)
omega_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 640), (200, 30)), 
    start_value=omega, value_range=(math.pi, 6 * math.pi), manager=manager)
time_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 680), (200, 30)), 
    start_value=1.0, value_range=(0.1, 5.0), manager=manager)  # Time controller slider

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
    return torque / crank_radius

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

    # Calculate linear force
    force = calculate_force(T, zoomed_r)

    # Draw crankshaft
    pygame.draw.line(screen, BLACK, (cx, cy), (crank_x, crank_y), 5)
    pygame.draw.circle(screen, RED, (int(crank_x), int(crank_y)), int(10 * zoom_level))
    pygame.draw.circle(screen, GREEN, (cx, cy), int(zoomed_r), int(5 * zoom_level))

    # Draw connecting rod
    pygame.draw.line(screen, BLUE, (crank_x, crank_y), (fixed_rod_x, fixed_rod_y - int(50 * zoom_level)), 5)
    pygame.draw.circle(screen, BLACK, (int(fixed_rod_x), int(fixed_rod_y)), int(10 * zoom_level))

    # Draw fixed rod (constraining y-axis motion)
    pygame.draw.line(screen, RED, (piston_x, int(crank_y)), (piston_x, fixed_rod_y), int(10 * zoom_level))

    # Display force and parameter values
    font = pygame.font.SysFont(None, 30)
    force_text = font.render(f'Force: {force:.2f} N', True, BLACK)
    torque_text = font.render(f'Torque: {T:.2f} N*m', True, BLACK)
    radius_text = font.render(f'Crank Radius: {zoomed_r:.2f} px', True, BLACK)
    rod_length_text = font.render(f'Connecting Rod Length: {l:.2f} px', True, BLACK)
    omega_text = font.render(f'Angular Velocity: {omega:.2f} rad/s', True, BLACK)
    time_text = font.render(f'Time Scale: {time_scale:.2f}', True, BLACK)

    screen.blit(force_text, (250, 520))
    screen.blit(torque_text, (250, 550))
    screen.blit(radius_text, (250, 580))
    screen.blit(rod_length_text, (250, 610))
    screen.blit(omega_text, (250, 640))
    screen.blit(time_text, (250, 670))

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
