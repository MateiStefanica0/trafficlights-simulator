import pygame
import random
import time
from queue import Queue

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
BACKGROUND_COLOR = (255, 255, 255)
ROAD_COLOR = (0, 0, 0)
GRID_SIZE = 2
ROAD_WIDTH = WINDOW_WIDTH // GRID_SIZE
ROAD_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
FPS = 60
VEHICLE_SPAWN_RATE = 3  # 10 vehicles per second
VEHICLE_SPAWN_DURATION = 60  # 15 seconds

DISTANCE_FROM_INTERSECTION = 30

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
        if direction == "up" or direction == "down":
            self.axis = "vertical"
        else:
            self.axis = "horizontal"

    def get_hitbox(self):
        """Returns the hitbox of the vehicle, extended in the direction of movement."""
        if self.direction == "up":
            return pygame.Rect(self.x, self.y - 5, 20, 25)  # Extend upward
        elif self.direction == "down":
            return pygame.Rect(self.x, self.y, 20, 25)  # Extend downward
        elif self.direction == "left":
            return pygame.Rect(self.x - 5, self.y, 25, 20)  # Extend left
        elif self.direction == "right":
            return pygame.Rect(self.x, self.y, 25, 20)  # Extend right
        return pygame.Rect(self.x, self.y, 20, 20)  # Default


    def check_collision(self, vehicles, direction):
        """Checks if the vehicle collides with any other vehicles in the direction of movement."""
        for vehicle in vehicles:
            if vehicle != self and vehicle.direction == self.direction:  # Skip itself
                if self.get_hitbox().colliderect(vehicle.get_hitbox()):
                    # Ensure the vehicle is in front based on direction
                    if direction == "up" and vehicle.y < self.y:
                        return True
                    elif direction == "down" and vehicle.y > self.y:
                        return True
                    elif direction == "left" and vehicle.x < self.x:
                        return True
                    elif direction == "right" and vehicle.x > self.x:
                        return True
        return False

    def is_waiting_at_intersection(self, intersection):
        # Check if the vehicle is waiting at the given intersection
        if self.direction == "up" and self.y <= intersection.y + (WINDOW_HEIGHT / GRID_SIZE) and abs(self.x - intersection.x) < 30:
            return True
        elif self.direction == "down" and self.y >= intersection.y - (WINDOW_HEIGHT / GRID_SIZE) and abs(self.x - intersection.x) < 30:
            return True
        elif self.direction == "left" and self.x <= intersection.x + (WINDOW_WIDTH / GRID_SIZE) and abs(self.y - intersection.y) < 30:
            return True
        elif self.direction == "right" and self.x >= intersection.x - (WINDOW_WIDTH / GRID_SIZE) and abs(self.y - intersection.y) < 30:
            return True
        return False

    def move(self, vehicles, intersections):
        if self.current_intersection:
            # Check if the vehicle is waiting at an intersection
            if self.direction in ["left", "right"]:
                if self.current_intersection.horizontal_light.state == "red":
                    self.stop()
                    self.current_intersection.add_vehicle(self)
                    return
            elif self.direction in ["up", "down"]:
                if self.current_intersection.vertical_light.state == "red":
                    self.stop()
                    self.current_intersection.add_vehicle(self)
                    return

            # Light is green; resume movement and remove from queue
            self.resume()
            self.current_intersection.remove_vehicle(self)
            self.current_intersection = None  # Clear intersection after passing

            # Add a chance to change direction at the intersection
            if random.random() < 0.3:  # 50% chance to change direction
                self.change_direction()

        # Check for collisions
        if self.check_collision(vehicles, self.direction):
            self.stop()
            return

        if self.direction == "right" or self.direction == "left":
            target_lane_y = self.current_road.get_lane_positions(self.direction)
            if target_lane_y is not None and abs(self.y - target_lane_y) > 1:  # Correct position gradually
                self.y += (target_lane_y - self.y) * 0.1

        elif self.direction == "down" or self.direction == "up":
            target_lane_x = self.current_road.get_lane_positions(self.direction)
            if target_lane_x is not None and abs(self.x - target_lane_x) > 1:  # Correct position gradually
                self.x += (target_lane_x - self.x) * 0.1

        # Continue moving in the current direction
        if self.direction == "right":
            self.x += self.speed
        elif self.direction == "left":
            self.x -= self.speed
        elif self.direction == "down":
            self.y += self.speed
        elif self.direction == "up":
            self.y -= self.speed




    def switch_axis(self):
        if self.axis == "horizontal":
            self.axis = "vertical"
        else:
            self.axis = "horizontal"

                

    def stop(self):
        self.stopped = True
        self.moving = False

    def resume(self):
        self.stopped = False
        self.moving = True

    def change_direction(self):
        """Change the vehicle's direction randomly and update its position first."""
        if not self.change_direction_requested:
            choice = random.random()
            if choice < 0.3:  # 30% chance to turn left
                if self.direction == "up":
                    self.y -= DISTANCE_FROM_INTERSECTION / 2
                    self.direction = "left"
                elif self.direction == "down":
                    self.y += DISTANCE_FROM_INTERSECTION / 2 
                    self.direction = "right"
                elif self.direction == "left":
                    self.x -= DISTANCE_FROM_INTERSECTION / 2
                    self.direction = "down"
                elif self.direction == "right":
                    self.x += DISTANCE_FROM_INTERSECTION / 2
                    self.direction = "up"
            elif choice < 0.6:  # 30% chance to turn right
                if self.direction == "up":
                    self.y -= DISTANCE_FROM_INTERSECTION / 2
                    self.direction = "right"
                elif self.direction == "down":
                    self.y += DISTANCE_FROM_INTERSECTION / 2
                    self.direction = "left"
                elif self.direction == "left":
                    self.x -= DISTANCE_FROM_INTERSECTION / 2
                    self.direction = "up"
                elif self.direction == "right":
                    self.x += DISTANCE_FROM_INTERSECTION / 2
                    self.direction = "down"
            
            # Align the vehicle's position to the nearest grid line
            self.x = round(self.x / GRID_SIZE) * GRID_SIZE
            self.y = round(self.y / GRID_SIZE) * GRID_SIZE
            
            self.switch_axis()
            # 40% chance to continue in the same direction (no position change)
            self.change_direction_requested = True  # Direction change request handled



    def draw(self):
        if self.shape == "car":
            pygame.draw.rect(screen, (0, 0, 255), (self.x, self.y, 20, 20))
        elif self.shape == "motorcycle":
            pygame.draw.polygon(screen, (0, 255, 0), [(self.x, self.y), (self.x + 10, self.y - 20), (self.x + 20, self.y)])
        elif self.shape == "truck":
            pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, 30, 20))

    def check_window_bounds(self, vehicles):
        if self.x != self.spawn_x and self.y != self.spawn_y:
            if self.x > WINDOW_WIDTH or self.x < WINDOW_WIDTH or self.y > WINDOW_HEIGHT or self.y > WINDOW_WIDTH:
                vehicles.remove(self)

class Road:
    def __init__(self, x, y, width, height, lanes=2):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.lanes = lanes  # Number of lanes per direction

    def get_lane_positions(self, direction):
        """Return the center lane position based on the direction of travel."""
        if self.width > self.height:  # Horizontal road
            center_y = self.y + self.height // 2  # Center of the road
            if direction == "right":
                return center_y - 10  # Adjust if needed
            elif direction == "left":
                return center_y + 10  # Adjust if needed
        else:  # Vertical road
            center_x = self.x + self.width // 2  # Center of the road
            if direction == "down":
                return center_x - 10  # Adjust if needed
            elif direction == "up":
                return center_x + 10  # Adjust if needed
        return None


    def draw(self):
        """Draw the road with lanes."""
        pygame.draw.rect(screen, ROAD_COLOR, (self.x, self.y, self.width, self.height))
        
        # Draw lane dividers
        if self.width > self.height:  # Horizontal road
            for i in range(1, self.lanes):  # Skip the outer edges
                pygame.draw.line(screen, (200, 200, 200), 
                                 (self.x, self.y + i * (self.height // self.lanes)), 
                                 (self.x + self.width, self.y + i * (self.height // self.lanes)), 2)
        else:  # Vertical road
            for i in range(1, self.lanes):  # Skip the outer edges
                pygame.draw.line(screen, (200, 200, 200), 
                                 (self.x + i * (self.width // self.lanes), self.y), 
                                 (self.x + i * (self.width // self.lanes), self.y + self.height), 2)



class Intersection:
    def __init__(self, x, y):
        # Set logical center for intersection
        self.x = x
        self.y = y
        self.horizontal_light = TrafficLight(x, y - 20, "horizontal")
        self.vertical_light = TrafficLight(x - 20, y, "vertical")
        self.waiting_vehicles = []  # List of vehicles waiting at the intersection
        self.cars_waiting_up_down = 0
        self.cars_waiting_left_right = 0
        self.light_state = "green_up_down"  # Initial state
        self.last_toggle_time = time.time()

    def update_cars_waiting(self, vehicles):
        # Reset counters
        self.cars_waiting_up_down = 0
        self.cars_waiting_left_right = 0

        for vehicle in vehicles:
            if vehicle.is_waiting_at_intersection(self):
                if vehicle.direction in ["up", "down"]:
                    self.cars_waiting_up_down += 1
                elif vehicle.direction in ["left", "right"]:
                    self.cars_waiting_left_right += 1

    def toggle_traffic_lights(self):
        current_time = time.time()
        if (current_time - self.last_toggle_time > 2):
            if self.cars_waiting_up_down > 7 or self.cars_waiting_left_right > 7:
                if self.light_state == "green_up_down":
                    self.light_state = "green_left_right"
                else:
                    self.light_state = "green_up_down"
                self.last_toggle_time = current_time
            elif current_time - self.last_toggle_time > 5:
                if self.light_state == "green_up_down":
                    self.light_state = "green_left_right"
                else:
                    self.light_state = "green_up_down"
                self.last_toggle_time = current_time


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
        if self.light_state == "green_up_down":
            self.vertical_light.state = "green"
            self.horizontal_light.state = "red"
        else:
            self.vertical_light.state = "red"
            self.horizontal_light.state = "green"
        self.horizontal_light.draw()
        self.vertical_light.draw()

    def add_vehicle(self, vehicle):
        self.waiting_vehicles.append(vehicle)

    

    def remove_vehicle(self, vehicle):
        if vehicle in self.waiting_vehicles:
            self.waiting_vehicles.remove(vehicle)

class SpawnPoint:
    def __init__(self, pos, road):
        self.pos = pos
        self.active = False
        self.road = road

    def toggle_active(self):
        self.active = not self.active

    def draw(self, screen):
        color = (0, 255, 0) if self.active else (0, 0, 0)
        pygame.draw.circle(screen, color, self.pos, 10)

    def is_clicked(self, mouse_pos):
        x, y = self.pos
        mx, my = mouse_pos
        return (x - 10 <= mx <= x + 10) and (y - 10 <= my <= y + 10)

class Button:
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, 36)
        self.color = (0, 0, 0)
        self.hover_color = (100, 100, 100)
        self.active_color = self.color

    def draw(self, screen):
        pygame.draw.rect(screen, self.active_color, self.rect)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.active_color = self.hover_color
            else:
                self.active_color = self.color
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()

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
            roads.append(Road(x, y + ROAD_HEIGHT // 2 - 5, ROAD_WIDTH, 10))
            if i < GRID_SIZE:  # Only add traffic lights where horizontal and vertical roads meet
                intersection_x = x + ROAD_WIDTH // 2
                intersection_y = y + ROAD_HEIGHT // 2
                intersections.append(Intersection(intersection_x, intersection_y))  # Place intersection at road crossing

        # Draw vertical roads and intersections (not on the right-most column)
        if i < GRID_SIZE:  # Exclude right-most vertical line
            roads.append(Road(x + ROAD_WIDTH // 2 - 5, y, 10, ROAD_HEIGHT))
            if j < GRID_SIZE:  # Only add traffic lights where horizontal and vertical roads meet
                intersection_x = x + ROAD_WIDTH // 2
                intersection_y = y + ROAD_HEIGHT // 2
                intersections.append(Intersection(intersection_x, intersection_y))  # Place intersection at road crossing


# Ensure roads match the grid layout correctly


def spawn_vehicle_on_road(spawn_point, shape, speed_range):
    road = spawn_point.road
    spawn_x, spawn_y = spawn_point.pos
    direction = None

    if road.width > road.height:  # Horizontal road
        direction = "right" if spawn_x < road.x + road.width // 2 else "left"
    else:  # Vertical road
        direction = "down" if spawn_y < road.y + road.height // 2 else "up"

    vehicle = Vehicle(spawn_x, spawn_y, shape, speed_range, direction)


    vehicle.spawn_x = spawn_x
    vehicle.spawn_y = spawn_y
    vehicle.current_road = road  # Assign current road
    return vehicle




# Vehicle spawning timer
vehicle_spawn_timer = 0  # Timer to keep track of the elapsed time
vehicle_spawned_count = 0  # Counter for the number of vehicles spawned
total_vehicle_count = VEHICLE_SPAWN_RATE * VEHICLE_SPAWN_DURATION  # Total vehicles to spawn

vehicles = []

# Define spawn points at the edges of the screen
spawn_points = []

for road in roads:
    if road.width > road.height:  # Horizontal road
        if road.x == start_x:  # Left edge
            spawn_points.append(SpawnPoint((road.x + 30, road.y + road.height // 2), road))
        elif road.x + road.width == start_x + grid_width:  # Right edge
            spawn_points.append(SpawnPoint((road.x + road.width - 30, road.y + road.height // 2), road))
    else:  # Vertical road
        if road.y == start_y:  # Top edge
            spawn_points.append(SpawnPoint((road.x + road.width // 2, road.y + 30), road))
        elif road.y + road.height == start_y + grid_height:  # Bottom edge
            spawn_points.append(SpawnPoint((road.x + road.width // 2, road.y + road.height - 30), road))

is_paused = True

def toggle_play_pause():
    global is_paused
    is_paused = not is_paused
    play_pause_button.text = "Pause" if not is_paused else "Play"


def reset_simulation():
    global vehicles, vehicle_spawn_timer, vehicle_spawned_count, is_paused
    vehicles = []
    vehicle_spawn_timer = 0
    vehicle_spawned_count = 0
    is_paused = True
    play_pause_button.text = "Play"

play_pause_button = Button(WINDOW_WIDTH - 110, 10, 100, 50, "Play", toggle_play_pause)
reset_button = Button(WINDOW_WIDTH - 110, 70, 100, 50, "Reset", reset_simulation)


# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for spawn_point in spawn_points:
                if spawn_point.is_clicked(mouse_pos):
                    spawn_point.toggle_active()
            play_pause_button.handle_event(event)
            reset_button.handle_event(event)

    # Get the elapsed time since the game started
    current_time = pygame.time.get_ticks()

    # Spawn vehicles progressively at the specified rate
    if vehicle_spawned_count < total_vehicle_count and (current_time // 1000) < VEHICLE_SPAWN_DURATION:
        if current_time // 1000 > vehicle_spawn_timer:
            for spawn_point in spawn_points:
                if spawn_point.active:
                    for _ in range(VEHICLE_SPAWN_RATE):
                        vehicles.append(spawn_vehicle_on_road(spawn_point, "car", (1, 2)))  # Adjust shape/speed if needed
                        vehicle_spawned_count += 1
            vehicle_spawn_timer = current_time // 1000  # Update the timer

    screen.fill(BACKGROUND_COLOR)

    # Draw roads
    for road in roads:
        road.draw()
        pygame.draw.line(screen, (0, 255, 255), 
                     (road.x, road.y), 
                     (road.x + road.width, road.y + road.height), 1)

    # Draw spawn points
    for spawn_point in spawn_points:
        spawn_point.draw(screen)

    # Update and draw intersections
    for intersection in intersections:
        # print(time.time())
        intersection.draw()
        pygame.draw.circle(screen, (255, 0, 255), (intersection.x, intersection.y), 5)


    if not is_paused:
        for intersection in intersections:
            intersection.update_cars_waiting(vehicles)
            intersection.toggle_traffic_lights()

        for vehicle in vehicles:
            vehicle_near_intersection = False
            for intersection in intersections:
                # Check proximity to the intersection based on direction
                if (
                    (vehicle.direction == "left" and 
                    vehicle.x - intersection.x <= DISTANCE_FROM_INTERSECTION and
                    vehicle.x > intersection.x and  # Ensure approaching, not passed
                    abs(vehicle.y - intersection.y) < ROAD_WIDTH // 2) or
                    (vehicle.direction == "right" and 
                    intersection.x - vehicle.x <= DISTANCE_FROM_INTERSECTION and
                    vehicle.x < intersection.x and
                    abs(vehicle.y - intersection.y) < ROAD_WIDTH // 2) or
                    (vehicle.direction == "up" and 
                    vehicle.y - intersection.y <= DISTANCE_FROM_INTERSECTION and
                    vehicle.y > intersection.y and
                    abs(vehicle.x - intersection.x) < ROAD_HEIGHT // 2) or
                    (vehicle.direction == "down" and 
                    intersection.y - vehicle.y <= DISTANCE_FROM_INTERSECTION and
                    vehicle.y < intersection.y and
                    abs(vehicle.x - intersection.x) < ROAD_HEIGHT // 2)
                ):
                    vehicle.current_intersection = intersection  # Assign intersection
                    vehicle_near_intersection = True

                    # Handle stopping at red light
                    if (vehicle.direction in ["left", "right"] and 
                        intersection.horizontal_light.state == "red") or \
                    (vehicle.direction in ["up", "down"] and 
                        intersection.vertical_light.state == "red"):
                        vehicle.stop()
                    else:
                        vehicle.resume()
                    break  # No need to check other intersections once it's assigned

            if not vehicle_near_intersection:
                vehicle.current_intersection = None  # Reset if not near an intersection

            # Update vehicle movement and draw
            vehicle.move(vehicles, intersections)  # Pass list of vehicles and intersections for logic
        

    # Update and draw vehicles
    for vehicle in vehicles:
        vehicle.draw()

    vehicles = [vehicle for vehicle in vehicles if vehicle.x >= 0 and vehicle.x <= WINDOW_WIDTH and vehicle.y >= 0 and vehicle.y <= WINDOW_HEIGHT]
    play_pause_button.draw(screen)
    reset_button.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()