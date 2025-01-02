from globals import *
import globals

# We have tries to make this project as OOP as possible, therefore almost everything is a class


class TrafficLight:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction  # Direction: "horizontal" or "vertical"
        self.state = "red"  # Initial state
        self.last_switch_time = time.time()
        self.switch_interval = 5  # Switch every 5 seconds

    def switch_state(self):
        """Alternates between red and green lights depending on thetype of the simulation"""
        if time.time() - self.last_switch_time >= self.switch_interval:
            if self.state == "red":
                self.state = "green"
            else:
                self.state = "red"
            # Updates the the last time of switch (relevant for the next switch)
            self.last_switch_time = time.time()

    def draw(self, screen):
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
        self.direction = direction # of momevemt
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
        self.current_road = None

        # Used for the choose route functionality
        self.violet_flag = False
        self.destination = None
        self.last_turn = None
        self.arrived = False
        self.last_intersection = None
        self.recent_intersections = []


    def get_hitbox(self):
        """Returns the hitbox of the vehicle, extended in the direction of movement."""
        # This way, vehicles coming from different directions in an intersesction won't collide
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

        # Movement is treated differentlly basen on the type of vehicle

        if self.violet_flag:
            if self.destination:
                self.navigate_to_destination(vehicles, intersections)
            else:
                self.move_along_road()
        
        else:
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
                # Updating the break count to be displayed in the stats window
                globals.break_count += 1
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
                    if random.random() < 0.4:  # 40% chance to change direction
                        self.change_direction()

                # Check for collisions
                if self.check_collision(vehicles, self.direction):
                    self.stop()
                    return

                # SLightly correcting the positioning on the lanes

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

    def move_along_road(self):
        if self.current_road:
            if self.direction == "right":
                self.x += self.speed

            elif self.direction == "left":
                self.x -= self.speed

            elif self.direction == "up":
                self.y -= self.speed

            elif self.direction == "down":
                self.y += self.speed


    def navigate_to_destination(self, vehicles, intersections):
        # Constants only relevant to this part
        MARGIN = 30  # Adjusted margin for directional adjustments
        DETECTION_MARGIN = 20  # Margin for detecting intersections
        DISTANCE_THRESHOLD = 20  # Distance to clear intersection
        TURN_COOLDOWN = 1  # Cooldown in seconds
        RECENT_VISITS_LIMIT = 5  # Limit for recently visited intersections

        # Handle turn cooldown
        if self.last_turn and (time.time() - self.last_turn) < TURN_COOLDOWN:
            return  # Skip further checks until cooldown expires

        # Handle current intersection
        if self.current_intersection:
            light_state = None
            if self.direction in ["left", "right"]:
                light_state = self.current_intersection.horizontal_light.state
            elif self.direction in ["up", "down"]:
                light_state = self.current_intersection.vertical_light.state

            if light_state == "red":
                self.stop()
                self.current_intersection.add_vehicle(self)
                return

            # Light is green; resume movement
            self.resume()
            self.current_intersection.remove_vehicle(self)
            self.last_intersection = self.current_intersection
            self.current_intersection = None  # Clear intersection after passing

        # Perform collision check before movement
        if self.check_collision(vehicles, self.direction):
            self.stop()
            return

        # Move the vehicle
        self.move_along_road()

        # Find the nearest intersection in front of the vehicle
        if not self.current_intersection:
            for intersection in intersections:
                if abs(self.x - intersection.x) < DETECTION_MARGIN and abs(self.y - intersection.y) < DETECTION_MARGIN:
                    if ((self.direction == "right" and self.x < intersection.x) or
                        (self.direction == "left" and self.x > intersection.x) or
                        (self.direction == "up" and self.y > intersection.y) or
                        (self.direction == "down" and self.y < intersection.y)):
                        
                        # Avoid re-entering recently visited intersections
                        if intersection not in self.recent_intersections:
                            self.current_intersection = intersection
                            self.recent_intersections.append(intersection)
                            if len(self.recent_intersections) > RECENT_VISITS_LIMIT:
                                self.recent_intersections.pop(0)
                            break

        # Clear the intersection if moved sufficiently far
        if self.current_intersection:
            if (abs(self.x - self.current_intersection.x) > DISTANCE_THRESHOLD or
                abs(self.y - self.current_intersection.y) > DISTANCE_THRESHOLD):
                self.current_intersection = None

        # Adjust direction based on destination
        if self.current_intersection:
            if self.direction == "right":
                if self.y < self.destination.y - MARGIN:
                    self.direction = "down"
                elif self.y > self.destination.y + MARGIN:
                    self.direction = "up"
            elif self.direction == "left":
                if self.y < self.destination.y - MARGIN:
                    self.direction = "down"
                elif self.y > self.destination.y + MARGIN:
                    self.direction = "up"
            elif self.direction == "up":
                if self.x < self.destination.x - MARGIN:
                    self.direction = "left"
                elif self.x > self.destination.x + MARGIN:
                    self.direction = "right"
            elif self.direction == "down":
                if self.x < self.destination.x - MARGIN:
                    self.direction = "right"
                elif self.x > self.destination.x + MARGIN:
                    self.direction = "left"

            # Update turn timestamp
            self.last_turn = time.time()
            self.last_intersection = self.current_intersection


        

    # Function that switches the axes, as this is relevant for how the movement is treated

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
        self.stopped = False
        self.moving = True
        if self.last_stop_time is not None:
            waiting_duration = time.time() - self.last_stop_time
            self.waiting_time += waiting_duration
            # Updating the global variable
            globals.total_waiting_time += waiting_duration
            self.last_stop_time = None
        if self.current_intersection and not self.counted:
            # Increments the car count in order to let the intersection decide when to toggle the trafficlights
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



    def draw(self, screen):
        # This function also allows spawning different vehicles

        if self.shape == "car" and self.violet_flag:
            pygame.draw.rect(screen, VIOLET_COLOR, (self.x, self.y, 20, 20))
            
        elif self.shape == "car":
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


    def draw(self, screen):
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

class SmartIntersection:
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
        self.car_count = 0 # How many cars are waiting

    def update_cars_waiting(self, vehicles):
        # Reset counters
        self.cars_waiting_up_down = 0 
        self.cars_waiting_left_right = 0

        # Relevant function for toggling the trafficlights 

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
        # The smart trafficlights toggling heuristics 
        if (current_time - self.last_toggle_time > 2):
            if self.cars_waiting_up_down > 7 or self.cars_waiting_left_right > 7:
                if self.light_state == "green_up_down":
                    self.light_state = "green_left_right"
                else:
                    self.light_state = "green_up_down"
                self.last_toggle_time = current_time
            elif current_time - self.last_toggle_time > 7:
                if self.light_state == "green_up_down":
                    self.light_state = "green_left_right"
                else:
                    self.light_state = "green_up_down"
                self.last_toggle_time = current_time


    def update(self):
        """Update the state of both traffic lights"""

        if self.horizontal_light.state == "red":
            self.vertical_light.switch_state()
        else:
            self.horizontal_light.switch_state()

        if self.vertical_light.state == "red":
            self.horizontal_light.switch_state()
        else:
            self.vertical_light.switch_state()


    def draw(self, screen):
        """Draw both traffic lights"""
        if self.light_state == "green_up_down":
            self.vertical_light.state = "green"
            self.horizontal_light.state = "red"
        else:
            self.vertical_light.state = "red"
            self.horizontal_light.state = "green"

        self.horizontal_light.draw(screen)
        self.vertical_light.draw(screen)

        font = pygame.font.Font(None, 36)
        text_surface = font.render(str(self.index), True, (0, 0, 0))
        pygame.draw.rect(screen, (255, 255, 255), (self.x + 20, self.y - 30, text_surface.get_width(), text_surface.get_height()))
        screen.blit(text_surface, (self.x + 25, self.y - 25))

    def add_vehicle(self, vehicle):
        self.waiting_vehicles.append(vehicle)

    

    def remove_vehicle(self, vehicle):
        if vehicle in self.waiting_vehicles:
            self.waiting_vehicles.remove(vehicle)

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
        if current_time - self.last_toggle_time > 7:
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


    def draw(self, screen):
        """Draw both traffic lights"""
        if self.light_state == "green_up_down":
            self.vertical_light.state = "green"
            self.horizontal_light.state = "red"
        else:
            self.vertical_light.state = "red"
            self.horizontal_light.state = "green"
        self.horizontal_light.draw(screen)
        self.vertical_light.draw(screen)
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
    def __init__(self, pos, road, index):
        self.pos = pos
        self.active = False
        self.road = road # Associated road
        self.index = index

    def toggle_active(self):
        self.active = not self.active

    def draw(self, screen):
        color = (0, 255, 0) if self.active else (0, 0, 0)
        pygame.draw.circle(screen, color, self.pos, 10)
        font = pygame.font.Font(None, 24)
        text_surface = font.render(str(self.index), True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.pos)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, mouse_pos):
        # Handle the event
        x, y = self.pos
        mx, my = mouse_pos
        return (x - 10 <= mx <= x + 10) and (y - 10 <= my <= y + 10)

class Button:
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height) # Shape
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