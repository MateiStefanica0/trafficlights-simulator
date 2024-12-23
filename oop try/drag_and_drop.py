import pygame
from intersection import Intersection

# --- constants --- (UPPER_CASE names)

SCREEN_WIDTH = 430
SCREEN_HEIGHT = 410

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

FPS = 60

# --- main ---

# - init -

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
pygame.display.set_caption("Tracking System")

# Initial circle position
initial_circle_pos = (100, 300)
initial_circle_radius = 20

# Create a list to hold Intersection instances
intersections = []

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            distance = ((initial_circle_pos[0] - mouse_pos[0]) ** 2 + (initial_circle_pos[1] - mouse_pos[1]) ** 2) ** 0.5
            if distance <= initial_circle_radius:
                new_intersection = Intersection(screen, mouse_pos)
                intersections.append(new_intersection)
        for intersection in intersections:
            intersection.handle_event(event)

    screen.fill(WHITE)
    pygame.draw.circle(screen, BLACK, initial_circle_pos, initial_circle_radius)
    for intersection in intersections:
        intersection.draw()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()