import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
BACKGROUND_COLOR = (255, 255, 255)
ROAD_COLOR = (0, 0, 0)
GRID_SIZE = 5
ROAD_WIDTH = WINDOW_WIDTH // GRID_SIZE
ROAD_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
FPS = 60
VEHICLE_SPAWN_RATE = 10  # 10 vehicles per second
VEHICLE_SPAWN_DURATION = 15  # 15 seconds

# Initialize screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Traffic Simulation")

# Classes (same as previous)
class TrafficLight:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction  # Direction: "horizontal" or "vertical"
        self.state = "red"  # Initial state
        self.last_switch_time = time.time()
        self.switch_interval = 5  # Switch every 5 seconds

    def switch_state(self):
        """Alternates between red and green lights every 5 seconds for each direction"""
        if time.time() - self.last_switch_time >= self.switch_interval:
            if self.state == "red":
                self.state = "green"
            else:
                self.state = "red"
            self.last_switch_time = time.time()

    def draw(self):
        """Draw the traffic light at the appropriate location"""
        if self.state == "red":
            color = (255, 0, 0)
        else:
            color = (0, 255, 0)
        pygame.draw.circle(screen, color, (self.x, self.y), 15)

class Vehicle:
    def __init__(self, x, y, shape, speed_range, direction):
        self.x = x
        self.y = y
        self.shape = shape
        self.speed = random.uniform(*speed_range)
        self.direction = direction
        self.stopped = False
        self.waiting = False  # Flag for waiting
        self.moving = True  # If the vehicle is allowed to move
        self.change_direction_requested = False  # Flag to ensure direction is only changed at intersection
        self.current_intersection = None  # Track the intersection the vehicle is approaching

    def move(self):
        if self.moving:
            if self.direction == "right":
                self.x += self.speed
            elif self.direction == "left":
                self.x -= self.speed
            elif self.direction == "down":
                self.y += self.speed
            elif self.direction == "up":
                self.y -= self.speed

    def stop(self):
        self.stopped = True
        self.moving = False

    def resume(self):
        self.stopped = False
        self.moving = True

    def change_direction(self):
        """Change the vehicle's direction randomly."""
        if not self.change_direction_requested:
            choice = random.random()
            if choice < 0.3:  # 30% chance to turn left
                if self.direction == "up":
                    self.direction = "left"
                elif self.direction == "down":
                    self.direction = "right"
                elif self.direction == "left":
                    self.direction = "down"
                elif self.direction == "right":
                    self.direction = "up"
            elif choice < 0.6:  # 30% chance to turn right
                if self.direction == "up":
                    self.direction = "right"
                elif self.direction == "down":
                    self.direction = "left"
                elif self.direction == "left":
                    self.direction = "up"
                elif self.direction == "right":
                    self.direction = "down"
            # 40% chance to continue in the same direction
            self.change_direction_requested = True  # Direction change request handled

    def draw(self):
        if self.shape == "car":
            pygame.draw.rect(screen, (0, 0, 255), (self.x, self.y, 20, 20))
        elif self.shape == "motorcycle":
            pygame.draw.polygon(screen, (0, 255, 0), [(self.x, self.y), (self.x + 10, self.y - 20), (self.x + 20, self.y)])
        elif self.shape == "truck":
            pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, 30, 20))

class Road:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Intersection:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.horizontal_light = TrafficLight(x, y - 20, "horizontal")
        self.vertical_light = TrafficLight(x - 20, y, "vertical")
        self.waiting_vehicles = []  # List of vehicles waiting at the intersection

    def update(self):
        """Update the state of both traffic lights"""
        # self.horizontal_light.switch_state()
        # self.vertical_light.switch_state()
        if self.horizontal_light.state == "red":
            self.vertical_light.switch_state()
        else:
            self.horizontal_light.switch_state()

        if self.vertical_light.state == "red":
            self.horizontal_light.switch_state()
        else:
            self.vertical_light.switch_state()


    def draw(self):
        """Draw both traffic lights"""
        self.horizontal_light.draw()
        self.vertical_light.draw()

    def add_vehicle(self, vehicle):
        self.waiting_vehicles.append(vehicle)

    def remove_vehicle(self, vehicle):
        if vehicle in self.waiting_vehicles:
            self.waiting_vehicles.remove(vehicle)

# Create roads and intersections
roads = []
intersections = []

# Calculate starting position for the grid (center the grid on the screen)
grid_width = GRID_SIZE * ROAD_WIDTH
grid_height = GRID_SIZE * ROAD_HEIGHT
start_x = (WINDOW_WIDTH - grid_width) // 2
start_y = (WINDOW_HEIGHT - grid_height) // 2

# Create roads and intersections
for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        x = start_x + i * ROAD_WIDTH
        y = start_y + j * ROAD_HEIGHT

        # Draw horizontal roads and intersections (not on the bottom row)
        if j < GRID_SIZE:  # Exclude bottom-most horizontal line
            # roads.append((x, y + ROAD_HEIGHT // 2 - 5, ROAD_WIDTH, 10))
            roads.append(Road(x, y + ROAD_HEIGHT // 2 - 5, ROAD_WIDTH, 10))
            if i < GRID_SIZE - 1:  # Only add traffic lights where horizontal and vertical roads meet
                intersections.append(Intersection(x + ROAD_WIDTH // 2, y + ROAD_HEIGHT // 2))

        # Draw vertical roads and intersections (not on the right-most column)
        if i < GRID_SIZE:  # Exclude right-most vertical line
            # roads.append((x + ROAD_WIDTH // 2 - 5, y, 10, ROAD_HEIGHT))
            roads.append(Road(x + ROAD_WIDTH // 2 - 5, y, 10, ROAD_HEIGHT))
            if j < GRID_SIZE - 1:  # Only add traffic lights where horizontal and vertical roads meet
                intersections.append(Intersection(x + ROAD_WIDTH // 2, y + ROAD_HEIGHT // 2))

# Vehicle spawning at the outer edges of the roads
def spawn_vehicle_on_road(shape, speed_range):
    # Select only the roads at the edges of the screen
    edge_roads = []

    # Add horizontal roads at the top and bottom edges (only the beginning of the roads)
    for road in roads:
        # x, y, width, height = road
        if road.y == 0:  # Top edge (beginning of the road)
            edge_roads.append(road)
        if road.y + road.height == WINDOW_HEIGHT:  # Bottom edge (beginning of the road)
            edge_roads.append(road)

    # Add vertical roads at the left and right edges (only the beginning of the roads)
    for road in roads:
        # x, y, width, height = road
        if road.x == 0:  # Left edge (beginning of the road)
            edge_roads.append(road)
        if road.x + road.width == WINDOW_WIDTH:  # Right edge (beginning of the road)
            edge_roads.append(road)

    # Randomly select an edge road
    road = random.choice(edge_roads)
    # x, y, width, height = road

    # Determine the spawn location based on whether the road is horizontal or vertical
    if road.width > road.height:  # Horizontal road
        spawn_x = road.x  # Spawn at the leftmost part of the road
        spawn_y = road.y + road.height // 2  # Center on the road vertically

        if road.y < WINDOW_HEIGHT / 2:  # If it's the topmost horizontal road
            direction = "right"  # Vehicle moves to the right
        else:  # If it's the bottommost horizontal road
            direction = "left"  # Vehicle moves to the left

    else:  # Vertical road
        spawn_x = road.x + road.width // 2  # Center on the road horizontally
        spawn_y = road.y  # Spawn at the topmost part of the road

        if road.x < WINDOW_WIDTH / 2:  # If it's the leftmost vertical road
            direction = "down"  # Vehicle moves down
        else:  # If it's the rightmost vertical road
            direction = "up"  # Vehicle moves up


    return Vehicle(spawn_x, spawn_y, shape, speed_range, direction)

# Vehicle spawning timer
vehicle_spawn_timer = 0  # Timer to keep track of the elapsed time
vehicle_spawned_count = 0  # Counter for the number of vehicles spawned
total_vehicle_count = VEHICLE_SPAWN_RATE * VEHICLE_SPAWN_DURATION  # Total vehicles to spawn

vehicles = []

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get the elapsed time since the game started
    current_time = pygame.time.get_ticks()

    # Spawn vehicles progressively at 10 vehicles per second for 15 seconds
    if vehicle_spawned_count < total_vehicle_count and (current_time // 1000) < VEHICLE_SPAWN_DURATION:
        if current_time // 1000 > vehicle_spawn_timer:
            for _ in range(VEHICLE_SPAWN_RATE):  # Spawn 10 vehicles
                vehicles.append(spawn_vehicle_on_road("car", (1, 2)))  # You can change the shape and speed as needed
                vehicle_spawned_count += 1
            vehicle_spawn_timer = current_time // 1000  # Update the timer

    screen.fill(BACKGROUND_COLOR)

    # Draw roads
    for road in roads:
        pygame.draw.rect(screen, ROAD_COLOR, (road.x, road.y, road.width, road.height))

    # Update and draw intersections
    for intersection in intersections:
        intersection.update()
        intersection.draw()

    # Update and draw vehicles
    for vehicle in vehicles:
        # Check if the vehicle is at an intersection and the light is red
        for intersection in intersections:
            if (
                intersection.x - 15 <= vehicle.x <= intersection.x + 15 and
                intersection.y - 15 <= vehicle.y <= intersection.y + 15
            ):
                vehicle.current_intersection = intersection  # Store the intersection vehicle is at

                # Handle horizontal traffic light
                if vehicle.direction in ["left", "right"]:
                    if intersection.horizontal_light.state == "red":
                        vehicle.stop()
                        intersection.add_vehicle(vehicle)
                    else:
                        if vehicle in intersection.waiting_vehicles:
                            intersection.remove_vehicle(vehicle)
                        vehicle.resume()

                # Handle vertical traffic light
                elif vehicle.direction in ["up", "down"]:
                    if intersection.vertical_light.state == "red":
                        vehicle.stop()
                        intersection.add_vehicle(vehicle)
                    else:
                        if vehicle in intersection.waiting_vehicles:
                            intersection.remove_vehicle(vehicle)
                        vehicle.resume()

                # Change direction at the intersection if the light is green
                vehicle.change_direction()

        vehicle.move()
        vehicle.draw()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
