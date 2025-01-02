import pygame
import random
import time
from queue import Queue
import tkinter as tk
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator

is_paused = True

# Constants
global GRID_SIZE
global VEHICLE_SPAWN_RATE
global VEHICLE_SPAWN_DURATION
global ROAD_WIDTH
global ROAD_HEIGHT
global TIME_TO_REPAIR
global is_raining

GRID_SIZE = 3
VEHICLE_SPAWN_RATE = 2
VEHICLE_SPAWN_DURATION = 15

TIME_TO_REPAIR = 3

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
BACKGROUND_COLOR = (255, 255, 255)
RAINING_BG_COLOR = (199, 235, 252)
ROAD_COLOR = (0, 0, 0)


FPS = 60


DISTANCE_FROM_INTERSECTION = 30


total_waiting_time = 0
break_count = 0
global start_time
start_time = None
elapsed_time = 0
simulation_ended = False



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
        self.waiting_time = 0  # Time spent waiting at intersections
        self.last_stop_time = None  # Last time the vehicle stopped
        if direction == "up" or direction == "down":
            self.axis = "vertical"
        else:
            self.axis = "horizontal"
        self.counted = False
        self.broken = False  # Flag to indicate if the vehicle is broken
        self.break_time = None  # Time when the vehicle broke down
        self.chance_to_break = 0.0001  # 0.1% chance to break while moving
        self.animation_start_time = None  # Time when the animation started

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
        if self.direction == "up" and self.y <= intersection.y + (WINDOW_HEIGHT / GRID_SIZE) \
             and abs(self.x - intersection.x) < 30:
            return True
        elif self.direction == "down" and self.y >= intersection.y - (WINDOW_HEIGHT / GRID_SIZE) \
            and abs(self.x - intersection.x) < 30:
            return True
        elif self.direction == "left" and self.x <= intersection.x + (WINDOW_WIDTH / GRID_SIZE) \
            and abs(self.y - intersection.y) < 30:
            return True
        elif self.direction == "right" and self.x >= intersection.x - (WINDOW_WIDTH / GRID_SIZE) \
            and abs(self.y - intersection.y) < 30:
            return True
        return False

    def move(self, vehicles, intersections):

        global break_count

        if self.broken and self.break_time:
            if time.time() - self.break_time >= TIME_TO_REPAIR:  # 3 seconds to repair
                self.broken = False
                self.resume()
            return

        rand = random.random()
        if rand < self.chance_to_break:
            self.broken = True
            self.break_time = time.time()
            self.animation_start_time = time.time()
            self.stop()
            break_count += 1
            return
        if not self.broken:
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
        if self.last_stop_time is None:
            self.last_stop_time = time.time()

    def resume(self):
        global total_waiting_time
        self.stopped = False
        self.moving = True
        if self.last_stop_time is not None:
            waiting_duration = time.time() - self.last_stop_time
            self.waiting_time += waiting_duration
            total_waiting_time += waiting_duration
            self.last_stop_time = None
        if self.current_intersection and not self.counted:
            self.current_intersection.increment_car_count()
            self.counted = True
        

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

        if self.broken and self.animation_start_time and time.time() - self.animation_start_time <= 1:
            pygame.draw.circle(screen, (255, 0, 0), (self.x + 30, self.y), 10)

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
    def __init__(self, x, y, index):
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
        self.index = index
        self.car_count = 0

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

    def increment_car_count(self):
        self.car_count += 1

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
        font = pygame.font.Font(None, 36)
        text_surface = font.render(str(self.index), True, (0, 0, 0))
        pygame.draw.rect(screen, (255, 255, 255), (self.x + 20, self.y - 30, text_surface.get_width(), text_surface.get_height()))
        screen.blit(text_surface, (self.x + 25, self.y - 25))

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



def run_pygame_simulation():
    global is_paused, vehicles, vehicle_spawn_timer, vehicle_spawned_count, total_waiting_time
    total_waiting_time = 0
    is_paused = True
    vehicles = []
    vehicle_spawn_timer = 0
    vehicle_spawned_count = 0
    pygame.init()

    global screen
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("TrafficLights Simulation")

    # Create roads and intersections
    roads = []
    intersections = []

    # Calculate starting position for the grid (center the grid on the screen)
    grid_width = GRID_SIZE * ROAD_WIDTH
    grid_height = GRID_SIZE * ROAD_HEIGHT
    start_x = (WINDOW_WIDTH - grid_width) // 2
    start_y = (WINDOW_HEIGHT - grid_height) // 2

    # Create roads and intersections
    intersection_index = 1  # Start indexing from 1
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
                    intersections.append(Intersection(intersection_x, intersection_y, intersection_index))  # Place intersection at road crossing
                    intersection_index += 1

            # Draw vertical roads and intersections (not on the right-most column)
            if i < GRID_SIZE:  # Exclude right-most vertical line
                roads.append(Road(x + ROAD_WIDTH // 2 - 5, y, 10, ROAD_HEIGHT))
                # if j < GRID_SIZE:  # Only add traffic lights where horizontal and vertical roads meet
                #     intersection_x = x + ROAD_WIDTH // 2
                #     intersection_y = y + ROAD_HEIGHT // 2
                #     intersections.append(Intersection(intersection_x, intersection_y, int(intersection_index / 2)))  # Place intersection at road crossing
                #     intersection_index += 1

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

    def get_total_waiting_time():
        global total_waiting_time
        return total_waiting_time

    def draw_total_waiting_time(screen, total_waiting_time):
        font = pygame.font.Font(None, 36)
        text_surface = font.render(f"Total Waiting Time: {total_waiting_time:.2f} s", True, (0, 0, 0))
        screen.blit(text_surface, (WINDOW_WIDTH - text_surface.get_width() - 10, WINDOW_HEIGHT - text_surface.get_height() - 10))


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



    def toggle_play_pause():
        global is_paused, start_time, paused_time
        is_paused = not is_paused
        if not is_paused:
            if start_time is None:
                start_time = time.time()  # Set the start time when play is pressed
            else:
                # Adjust start_time to account for the paused duration
                start_time += time.time() - paused_time
        else:
            paused_time = time.time()  # Record the time when paused

        play_pause_button.text = "Pause" if not is_paused else "Play"


    def draw_elapsed_time(screen, start_time):
        global elapsed_time, simulation_ended
        if start_time is not None and not is_paused and not simulation_ended:
            elapsed_time = time.time() - start_time

        font = pygame.font.Font(None, 36)
        text_surface = font.render(f"Elapsed Time: {elapsed_time:.2f} s", True, (0, 0, 0))
        screen.blit(text_surface, (WINDOW_WIDTH - text_surface.get_width() - 10, WINDOW_HEIGHT - text_surface.get_height() - 50))
            


    def reset_simulation():
        global vehicles, vehicle_spawn_timer, vehicle_spawned_count, is_paused, total_waiting_time, break_count, elapsed_time, is_raining, simulation_ended
        vehicles = []
        vehicle_spawn_timer = 0
        vehicle_spawned_count = 0
        is_paused = True
        play_pause_button.text = "Play"
        total_waiting_time = 0
        break_count = 0
        elapsed_time = 0
        is_raining = False
        simulation_ended = False

    def draw_simulation_ended_message(screen):
        font = pygame.font.Font(None, 72)
        text_surface = font.render("Simulation ended", True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        screen.blit(text_surface, text_rect)

    def show_stats():
        global running, stats_window, break_count
        running = False  # Stop the Pygame event loop
        pygame.quit()  # Quit Pygame

        # Suppress the root Tkinter window
        root = tk.Tk()
        root.withdraw()  # Hide the main Tkinter window

        # Create the statistics window
        stats_window = tk.Toplevel()
        stats_window.title("Statistics")
        stats_window.geometry("1200x1000")

        # Display some statistics
        stats_label = tk.Label(stats_window, text="Statistics will be displayed here.")
        stats_label.pack(pady=10)

        # Display break count
        break_text = f"Times a car broke: {break_count}\n"
        breaks_label = tk.Label(stats_window, text=break_text)
        breaks_label.pack(pady=10)

        # Display elapsed time
        elapsed_time_text = f"Elapsed Time: {elapsed_time:.2f} s\n"
        elapsed_time_label = tk.Label(stats_window, text=elapsed_time_text)
        elapsed_time_label.pack(pady=10)  # Reduced padding


        # Example statistics

        total_cars = sum(intersection.car_count for intersection in intersections)
        intersection_indices = [intersection.index for intersection in intersections]
        car_counts = [intersection.car_count for intersection in intersections]
        total_cars = sum(intersection.car_count for intersection in intersections)

        stats_text = f"Total Cars: {total_cars}\n"

        fig, ax = plt.subplots()
        ax.bar(intersection_indices, car_counts)
        ax.set_xlabel('Intersection Index')
        ax.set_ylabel('Number of Cars')
        ax.set_title('Number of Cars Passed Through Each Intersection')

        # Only use integers
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))


        # Embed the bar graph in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=stats_window)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)

        stats_label.config(text=stats_text)

        # Add "Back to the simulation" button
        back_button = tk.Button(stats_window, text="Back to the simulation", command=back_to_menu)
        back_button.pack(pady=20)

        # Add "Exit" button
        exit_button = tk.Button(stats_window, text="Exit", command=exit_program)
        exit_button.pack(pady=20)

        # Keep the statistics window open
        stats_window.mainloop()

    def back_to_menu():
        global stats_window
        stats_window.destroy()  # Close the stats window
        initialize_tkinter_window()  # Restart the Tkinter window to start the simulation again

    def start_raining():
        global is_raining
        is_raining = not is_raining
        if is_raining:
            for vehicle in vehicles:
                vehicle.speed *= 0.4  # Reduce speed to 60%
        else:
            for vehicle in vehicles:
                vehicle.speed /= 0.4  # Restore original speed

    # Buttons

    play_pause_button = Button(WINDOW_WIDTH - 110, 10, 100, 50, "Play", toggle_play_pause)
    reset_button = Button(WINDOW_WIDTH - 110, 70, 100, 50, "Reset", reset_simulation)
    menu_button = Button(10, 10, 100, 50, "Menu", show_menu)
    stats_button = Button(WINDOW_WIDTH - 110, 130, 100, 50, "Stats", show_stats)  # Add Stats button in upper right corner
    exit_button = Button(10, 70, 100, 50, "Exit", exit_program)
    rain_button = Button(10, WINDOW_HEIGHT - 60, 150, 50, "Starts raining", start_raining)

    
    
    

   

    # Main game loop
    running = True
    clock = pygame.time.Clock()
    global is_raining
    is_raining = False

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
                menu_button.handle_event(event)
                stats_button.handle_event(event)
                exit_button.handle_event(event)
                rain_button.handle_event(event)

        # Get the elapsed time since the game started
        current_time = pygame.time.get_ticks()

        # Spawn vehicles progressively at the specified rate
        

         # Fill the screen with a slightly bluer color if raining
        if is_raining:
            screen.fill(RAINING_BG_COLOR)
        else:
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
            intersection.draw()
            pygame.draw.circle(screen, (255, 0, 255), (intersection.x, intersection.y), 5)


        if not is_paused:
            

            if vehicle_spawned_count < total_vehicle_count:
                if current_time // 1000 > vehicle_spawn_timer:
                    for spawn_point in spawn_points:
                        if spawn_point.active:
                            for _ in range(VEHICLE_SPAWN_RATE):
                                vehicles.append(spawn_vehicle_on_road(spawn_point, "car", (1, 2)))  # Adjust shape/speed if needed
                                vehicle_spawned_count += 1
                    vehicle_spawn_timer = current_time // 1000  # Update the timer

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
        menu_button.draw(screen)
        stats_button.draw(screen)
        exit_button.draw(screen)
        rain_button.draw(screen)

        # Calculate and draw total waiting time
        total_waiting_time = get_total_waiting_time()
        draw_total_waiting_time(screen, total_waiting_time)

        # Draw elapsed time
        draw_elapsed_time(screen, start_time)
        global simulation_ended
        if len(vehicles) == 0 and vehicle_spawned_count >= total_vehicle_count:
            simulation_ended = True
            draw_simulation_ended_message(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()




def initialize_tkinter_window():
    def open_settings():
        settings_window = tk.Toplevel(root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")

        tk.Label(settings_window, text="Grid Size:").pack(pady=5)
        grid_size_entry = tk.Entry(settings_window)
        grid_size_entry.insert(0, str(GRID_SIZE))
        grid_size_entry.pack(pady=5)

        tk.Label(settings_window, text="Car Number:").pack(pady=5)
        car_number_entry = tk.Entry(settings_window)
        car_number_entry.insert(0, str(VEHICLE_SPAWN_RATE))
        car_number_entry.pack(pady=5)

        tk.Label(settings_window, text="Number of Seconds:").pack(pady=5)
        seconds_entry = tk.Entry(settings_window)
        seconds_entry.insert(0, str(VEHICLE_SPAWN_DURATION))
        seconds_entry.pack(pady=5)

        def save_settings():
            global GRID_SIZE, VEHICLE_SPAWN_RATE, VEHICLE_SPAWN_DURATION, ROAD_WIDTH, ROAD_HEIGHT
            GRID_SIZE = int(grid_size_entry.get())
            VEHICLE_SPAWN_RATE = int(car_number_entry.get())
            VEHICLE_SPAWN_DURATION = int(seconds_entry.get())
            ROAD_WIDTH = WINDOW_WIDTH // GRID_SIZE
            ROAD_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
            settings_window.destroy()
            update_settings_display()

        save_button = tk.Button(settings_window, text="Save", command=save_settings)
        save_button.pack(pady=20)

    def update_settings_display():
        settings_text.set(f"Grid Size: {GRID_SIZE}\nCar Number: {VEHICLE_SPAWN_RATE}\nNumber of Seconds: {VEHICLE_SPAWN_DURATION}")

    # Initialize default settings
    GRID_SIZE = 2
    VEHICLE_SPAWN_RATE = 2
    VEHICLE_SPAWN_DURATION = 15

    root = tk.Tk()
    root.title("Traffic Simulation")
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    # Create a menu bar
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    # Add a "Settings" menu
    settings_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Settings", menu=settings_menu)
    settings_menu.add_command(label="Open Settings", command=open_settings)

    # Create and center the start button
    start_button = tk.Button(root, text="Start Simulation", command=lambda: start_simulation(root))
    start_button.pack(expand=True)

    # Create the exit button
    exit_button = tk.Button(root, text="Exit", command=exit_program)
    exit_button.pack(pady=20)

    # Display current settings
    settings_text = tk.StringVar()
    settings_label = tk.Label(root, textvariable=settings_text)
    settings_label.pack(pady=20)
    update_settings_display()

    root.mainloop()

def start_simulation(root):
    root.destroy()  # Close the Tkinter window
    run_pygame_simulation()  # Function to run the Pygame simulation

def show_menu():
    pygame.quit()
    initialize_tkinter_window()

def exit_simulation():
    pygame.quit()
    sys.exit()  # Terminate the program

def exit_program():
    sys.exit()

if __name__ == "__main__":
    initialize_tkinter_window()