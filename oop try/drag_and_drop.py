import pygame
import math
from intersection import Intersection
from road import Road

# --- constants --- (UPPER_CASE names)

SCREEN_WIDTH = 0
SCREEN_HEIGHT = 0

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

FPS = 60

# --- main ---

# - init -

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Tracking System")

# Initial circle position
initial_circle_pos = (100, 300)
initial_circle_radius = 20

# Initial rectangle position and size (below the circle, proportional size, and 200 pixels lower)
initial_rect_pos = (initial_circle_pos[0] - initial_circle_radius, initial_circle_pos[1] + initial_circle_radius + 210)
initial_rect_size = (100, 5)  # Constant size for the road

# Create a list to hold Intersection and Road instances
objects = []

# Variables to keep track of the selected road and intersections
selected_road = None
selected_intersections = []

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            # Check if the initial circle is clicked
            distance = ((initial_circle_pos[0] - mouse_pos[0]) ** 2 + (initial_circle_pos[1] - mouse_pos[1]) ** 2) ** 0.5
            if distance <= initial_circle_radius:
                new_intersection = Intersection(screen, mouse_pos)
                objects.append(new_intersection)
            # Check if the initial rectangle is clicked
            elif initial_rect_pos[0] <= mouse_pos[0] <= initial_rect_pos[0] + initial_rect_size[0] and initial_rect_pos[1] <= mouse_pos[1] <= initial_rect_pos[1] + initial_rect_size[1]:
                new_road = Road(screen, mouse_pos, initial_rect_size)
                objects.append(new_road)
            # Check if any existing intersection is clicked
            for obj in objects:
                if isinstance(obj, Intersection) and obj.is_mouse_on_intersection(mouse_pos):
                    selected_intersections.append(obj)
                    if len(selected_intersections) == 2:
                        pos1 = selected_intersections[1].position  # Second selected intersection
                        pos2 = selected_intersections[0].position  # First selected intersection
                        road_pos = ((pos1[0] + pos2[0]) // 2, (pos1[1] + pos2[1]) // 2)
                        road_length = math.hypot(pos2[0] - pos1[0], pos2[1] - pos1[1])
                        road_size = (road_length, 5)  # Length fits between intersections, width is constant
                        angle = math.degrees(math.atan2(pos1[1] - pos2[1], pos1[0] - pos2[0]))
                        new_road = Road(screen, road_pos, road_size)
                        new_road.rotate(-angle)
                        objects.append(new_road)
                        selected_intersections = []
                    break
            # Check if any existing road is clicked
            for obj in objects:
                if isinstance(obj, Road) and obj.is_mouse_on_road(mouse_pos):
                    selected_road = obj
                    break
        elif event.type == pygame.KEYDOWN:
            if selected_road:
                if event.key == pygame.K_r:
                    selected_road.rotate(15)  # Rotate 15 degrees clockwise
                elif event.key == pygame.K_l:
                    selected_road.rotate(-15)  # Rotate 15 degrees counterclockwise
                elif event.key == pygame.K_DELETE:
                    objects.remove(selected_road)
                    selected_road = None
        for obj in objects:
            obj.handle_event(event)

    screen.fill(WHITE)
    pygame.draw.circle(screen, BLACK, initial_circle_pos, initial_circle_radius)
    pygame.draw.rect(screen, BLACK, (*initial_rect_pos, *initial_rect_size))
    for obj in objects:
        obj.draw()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()