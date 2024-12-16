import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BACKGROUND_COLOR = (255, 255, 255)
ROAD_COLOR = (0, 0, 0)
GRID_SIZE = 5
ROAD_WIDTH = WINDOW_WIDTH // GRID_SIZE
ROAD_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Define offsets for centering the grid within the window
GRID_OFFSET_X = (WINDOW_WIDTH - (ROAD_WIDTH * GRID_SIZE)) // 2
GRID_OFFSET_Y = (WINDOW_HEIGHT - (ROAD_HEIGHT * GRID_SIZE)) // 2
FPS = 60

# Initialize screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Traffic Simulation")

# Classes
class TrafficLight:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = "red"  # Initial state
        self.last_switch_time = time.time()
        self.switch_interval = 5  # Switch every 5 seconds

    def switch_state(self):
        if time.time() - self.last_switch_time >= self.switch_interval:
            self.state = "green" if self.state == "red" else "red"
            self.last_switch_time = time.time()

    def draw(self):
        color = (255, 0, 0) if self.state == "red" else (0, 255, 0)
        pygame.draw.circle(screen, color, (self.x, self.y), 15)

class Vehicle:
    def __init__(self, x, y, shape, speed_range, direction):
        self.x = x
        self.y = y
        self.shape = shape
        self.speed = random.uniform(*speed_range)
        self.direction = direction
        self.stopped = False

    def move(self):
        if not self.stopped:
            if self.direction == "right":
                self.x += self.speed
            elif self.direction == "left":
                self.x -= self.speed
            elif self.direction == "down":
                self.y += self.speed
            elif self.direction == "up":
                self.y -= self.speed

    def draw(self):
        if self.shape == "car":
            pygame.draw.rect(screen, (0, 0, 255), (self.x, self.y, 20, 20))
        elif self.shape == "motorcycle":
            pygame.draw.polygon(screen, (0, 255, 0), [(self.x, self.y), (self.x + 10, self.y - 20), (self.x + 20, self.y)])
        elif self.shape == "truck":
            pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, 30, 20))

class Intersection:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.traffic_light = TrafficLight(x, y)

    def update(self):
        self.traffic_light.switch_state()

    def draw(self):
        self.traffic_light.draw()

# Create roads and intersections
roads = []
intersections = []

for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        x = GRID_OFFSET_X + i * ROAD_WIDTH
        y = GRID_OFFSET_Y + j * ROAD_HEIGHT

        # Draw horizontal roads and intersections (not on the bottom row)
        if j < GRID_SIZE - 1:  # Exclude bottom-most horizontal line
            roads.append((x, y + ROAD_HEIGHT // 2 - 5, ROAD_WIDTH, 10))
            intersections.append(Intersection(x + ROAD_WIDTH, y + ROAD_HEIGHT // 2))

        # Draw vertical roads and intersections (not on the right-most column)
        if i < GRID_SIZE - 1:  # Exclude right-most vertical line
            roads.append((x + ROAD_WIDTH // 2 - 5, y, 10, ROAD_HEIGHT))
            intersections.append(Intersection(x + ROAD_WIDTH // 2, y + ROAD_HEIGHT))

# Vehicle spawning
def spawn_vehicle_on_road(shape, speed_range):
    road = random.choice(roads)
    x, y, width, height = road

    if width > height:  # Horizontal road
        spawn_x = random.randint(x, x + width - 20)
        spawn_y = y + height // 2
        direction = random.choice(["left", "right"])
    else:  # Vertical road
        spawn_x = x + width // 2
        spawn_y = random.randint(y, y + height - 20)
        direction = random.choice(["up", "down"])

    return Vehicle(spawn_x, spawn_y, shape, speed_range, direction)

vehicles = []
for _ in range(150):  # Cars
    vehicles.append(spawn_vehicle_on_road("car", (1, 2)))
for _ in range(50):  # Motorcycles
    vehicles.append(spawn_vehicle_on_road("motorcycle", (3, 4)))
for _ in range(50):  # Trucks
    vehicles.append(spawn_vehicle_on_road("truck", (0.5, 1.5)))

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BACKGROUND_COLOR)

    # Draw roads
    for road in roads:
        pygame.draw.rect(screen, ROAD_COLOR, road)

    # Update and draw intersections
    for intersection in intersections:
        intersection.update()
        intersection.draw()

    # Update and draw vehicles
    for vehicle in vehicles:
        vehicle.move()

        # Stop at red lights
        for intersection in intersections:
            if (
                intersection.x - 15 <= vehicle.x <= intersection.x + 15 and
                intersection.y - 15 <= vehicle.y <= intersection.y + 15 and
                intersection.traffic_light.state == "red"
            ):
                vehicle.stopped = True
                break
        else:
            vehicle.stopped = False

        vehicle.draw()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
