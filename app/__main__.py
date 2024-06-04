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

# Parameters (initial values)
T = 10  # Motor torque (N*m)
r = 100  # Crank radius (pixels)
l = 200  # Connecting rod length (pixels)
omega = 0.05  # Angular velocity (radians per frame)

# Sliders
torque_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 520), (200, 30)), 
    start_value=T, value_range=(1, 50), manager=manager)
radius_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 560), (200, 30)), 
    start_value=r, value_range=(50, 150), manager=manager)
rod_length_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 600), (200, 30)), 
    start_value=l, value_range=(100, 300), manager=manager)
omega_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 640), (200, 30)), 
    start_value=omega, value_range=(0.01, 0.1), manager=manager)

# Center of crankshaft
cx, cy = WIDTH // 2, HEIGHT // 2 - 50

# Simulation loop
running = True
theta = 0
clock = pygame.time.Clock()

def calculate_force(torque, crank_radius):
    return torque / crank_radius

while running:
    time_delta = clock.tick(60) / 1000.0  # Frame time in seconds
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        manager.process_events(event)

    # Update parameters from sliders
    T = torque_slider.get_current_value()
    r = radius_slider.get_current_value()
    l = rod_length_slider.get_current_value()
    omega = omega_slider.get_current_value()

    screen.fill(WHITE)

    # Calculate crank pin position
    crank_x = cx + r * math.cos(theta)
    crank_y = cy + r * math.sin(theta)

    # Calculate piston position
    piston_x = cx
    piston_y = cy + r * math.sin(theta)

    # Calculate connecting rod end position (fixed rod end)
    fixed_rod_x = cx
    fixed_rod_y = cy + math.sqrtl**2 - (crank_x - cx)**2)

    # Calculate linear force
    force = calculate_force(T, r)

    # Draw crankshaft
    pygame.draw.line(screen, BLACK, (cx, cy), (crank_x, crank_y), 5)
    pygame.draw.circle(screen, RED, (int(crank_x), int(crank_y)), 10)

    # Draw connecting rod
    pygame.draw.line(screen, BLUE, (crank_x, crank_y), (fixed_rod_x, fixed_rod_y), 5)
    pygame.draw.circle(screen, BLACK, (int(fixed_rod_x), int(fixed_rod_y)), 10)

    # Draw fixed rod (constraining y-axis motion)
    pygame.draw.line(screen, BLACK, (piston_x, cy), (piston_x, fixed_rod_y), 5)

    # Display force and parameter values
    font = pygame.font.SysFont(None, 30)
    force_text = font.render(f'Force: {force:.2f} N', True, BLACK)
    torque_text = font.render(f'Torque: {T:.2f} N*m', True, BLACK)
    radius_text = font.render(f'Crank Radius: {r:.2f} px', True, BLACK)
    rod_length_text = font.render(f'Connecting Rod Length: {l:.2f} px', True, BLACK)
    omega_text = font.render(f'Angular Velocity: {omega:.2f} rad/s', True, BLACK)

    screen.blit(force_text, (250, 520))
    screen.blit(torque_text, (250, 550))
    screen.blit(radius_text, (250, 580))
    screen.blit(rod_length_text, (250, 610))
    screen.blit(omega_text, (250, 640))

    # Update GUI elements
    manager.update(time_delta)
    manager.draw_ui(screen)

    # Update display
    pygame.display.flip()

    # Update angle
    theta += omega
    if theta >= 2 * math.pi:
        theta -= 2 * math.pi

pygame.quit()
