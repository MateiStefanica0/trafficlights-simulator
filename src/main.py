from globals import *
from classes import Vehicle
from classes import Road
from classes import Intersection
from classes import SmartIntersection
from classes import SpawnPoint
from classes import Button

import globals





def run_pygame_simulation(smart):
    # Initialisations
    global is_paused, vehicles, vehicle_spawn_timer, vehicle_spawned_count
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
                    # To decide what type of simulation it is
                    if smart:
                        intersections.append(SmartIntersection(intersection_x, intersection_y, intersection_index))
                    else:
                        intersections.append(Intersection(intersection_x, intersection_y, intersection_index))

                    intersection_index += 1

            # Draw vertical roads and intersections (not on the right-most column)
            if i < GRID_SIZE:  # Exclude right-most vertical line
                roads.append(Road(x + ROAD_WIDTH // 2 - 5, y, 10, ROAD_HEIGHT))


    def spawn_vehicle_on_road(spawn_point, shape, speed_range):
        # Use the assigned road
        road = spawn_point.road
        spawn_x, spawn_y = spawn_point.pos
        direction = None

        if road.width > road.height:  # Horizontal road
            if spawn_x < road.x + road.width // 2:
                direction = "right"
            else:
                direction = "left"
        else:  # Vertical road
            if spawn_y < road.y + road.height // 2:
                direction = "down"
            else:
                direction = "up"

        vehicle = Vehicle(spawn_x, spawn_y, shape, speed_range, direction)

        vehicle.spawn_x = spawn_x
        vehicle.spawn_y = spawn_y
        vehicle.current_road = road  # Assign current road

        return vehicle


    def draw_total_waiting_time(screen):
        font = pygame.font.Font(None, 36)
        # Using the glovals.total_waiting_time variable to see all the changes in all scopes
        text_surface = font.render(f"Total Waiting Time: {globals.total_waiting_time:.2f} s", True, (0, 0, 0))
        screen.blit(text_surface, (WINDOW_WIDTH - text_surface.get_width() - 10, WINDOW_HEIGHT - text_surface.get_height() - 10))

    def draw_violet_time(screen, violet_elapsed_time):
        font = pygame.font.Font(None, 24)  # Smaller font size
        violet_time_surface = font.render(f"Violet Time: {violet_elapsed_time:.2f} s", True, (0, 0, 0))
        screen.blit(violet_time_surface, (WINDOW_WIDTH - violet_time_surface.get_width() - 10, WINDOW_HEIGHT - violet_time_surface.get_height() - 90))

    def draw_elapsed_time(screen, start_time):
        global elapsed_time, simulation_ended
        if start_time is not None and not is_paused and not simulation_ended:
            elapsed_time = time.time() - start_time
            
        font = pygame.font.Font(None, 36)
        text_surface = font.render(f"Elapsed Time: {elapsed_time:.2f} s", True, (0, 0, 0))
        screen.blit(text_surface, (WINDOW_WIDTH - text_surface.get_width() - 10, WINDOW_HEIGHT - text_surface.get_height() - 50))


    # Vehicle spawning timer
    vehicle_spawn_timer = 0  # Timer to keep track of the elapsed time
    vehicle_spawned_count = 0  # Counter for the number of vehicles spawned
    total_vehicle_count = VEHICLE_SPAWN_RATE * VEHICLE_SPAWN_DURATION  # Total vehicles to spawn

    vehicles = []

    # Define spawn points at the edges of the screen
    spawn_points = []
    spawn_point_index = 1

    for road in roads:
        if road.width > road.height:  # Horizontal road
            # Indexing the spawn points
            if road.x == start_x:  # Left edge
                spawn_points.append(SpawnPoint((road.x + 30, road.y + road.height // 2), road, spawn_point_index))
                spawn_point_index += 1
            elif road.x + road.width == start_x + grid_width:  # Right edge
                spawn_points.append(SpawnPoint((road.x + road.width - 30, road.y + road.height // 2), road, spawn_point_index))
                spawn_point_index += 1
        else:  # Vertical road
            if road.y == start_y:  # Top edge
                spawn_points.append(SpawnPoint((road.x + road.width // 2, road.y + 30), road, spawn_point_index))
                spawn_point_index += 1
            elif road.y + road.height == start_y + grid_height:  # Bottom edge
                spawn_points.append(SpawnPoint((road.x + road.width // 2, road.y + road.height - 30), road, spawn_point_index))
                spawn_point_index += 1



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

        # Switch the button
        play_pause_button.text = "Pause" if not is_paused else "Play"

          


    def reset_simulation():
        # resetting all the relevant global variables
        global vehicles, vehicle_spawn_timer, vehicle_spawned_count, is_paused, elapsed_time, is_raining, simulation_ended, \
                paused_time, start_time, violet_vehicle_spawned, violet_elapsed_time, violet_start_time
        vehicles = []
        vehicle_spawn_timer = 0
        vehicle_spawned_count = 0
        is_paused = True
        play_pause_button.text = "Play"
        globals.total_waiting_time = 0
        globals.break_count = 0
        elapsed_time = 0
        is_raining = False
        simulation_ended = False
        paused_time = 0
        start_time = None
        violet_vehicle_spawned = False
        violet_start_time = 0
        violet_elapsed_time = 0

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
        stats_window.geometry("800x950")

        # Display some statistics
        stats_label = tk.Label(stats_window, text="Statistics will be displayed here.")
        stats_label.pack(pady=10)

        # Display break count
        break_text = f"Times a car broke: {globals.break_count}\n"
        breaks_label = tk.Label(stats_window, text=break_text)
        breaks_label.pack(pady=10)

        # Display elapsed time
        elapsed_time_text = f"Elapsed Time: {elapsed_time:.2f} s\n"
        elapsed_time_label = tk.Label(stats_window, text=elapsed_time_text)
        elapsed_time_label.pack(pady=10)  # Reduced padding

        # Display violet time
        violet_time_label = tk.Label(stats_window, text=f"Violet Vehicle Time: {violet_elapsed_time:.2f} s")
        violet_time_label.pack(pady=10)

        # Calculating stats
        total_cars = sum(intersection.car_count for intersection in intersections)
        intersection_indices = [intersection.index for intersection in intersections]
        car_counts = [intersection.car_count for intersection in intersections]
        total_cars = sum(intersection.car_count for intersection in intersections)

        stats_text = f"Total Cars: {total_cars}\n"

        # Plotting tha data

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

        # Buttons

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
        # Increasing/Decreasing speen when raining
        if is_raining:
            for vehicle in vehicles:
                vehicle.speed *= RAINING_QUOTIENT  # Reduce speed to 60%
        else:
            for vehicle in vehicles:
                vehicle.speed /= RAINING_QUOTIENT  # Restore original speed

    def open_select_route_window():
        def create_window():
            root = tk.Tk()
            root.withdraw()  # Hide the unnecessary root window

            # Create a new Tkinter window
            route_window = tk.Toplevel()
            route_window.title("Select Route")
            route_window.geometry("600x500")

            # Create a frame to hold the listboxes side by side
            frame = tk.Frame(route_window)
            frame.pack(pady=20)

            
            tk.Label(frame, text="Select a departure point:").grid(row=0, column=0, padx=10)
            tk.Label(frame, text="Select a destination point:").grid(row=0, column=1, padx=10)

            # Create a listbox to display the range of departure spawn points
            departure_listbox = tk.Listbox(frame)
            for spawn_point in spawn_points:
                departure_listbox.insert(tk.END, f"Spawn Point {spawn_point.index}")
            departure_listbox.grid(row=1, column=0, padx=10)

            # Create a listbox to display the range of destination spawn points
            destination_listbox = tk.Listbox(frame)
            for intersection in intersections:
                destination_listbox.insert(tk.END, f"Intersection {intersection.index}")
            destination_listbox.grid(row=1, column=1, padx=10)

            # Shared state to hold the selections
            global shared_state
            

            def confirm_selection_departure():
                selection = departure_listbox.curselection()
                if not selection:
                    messagebox.showerror("Error", "Please select a departure point.")
                    return
                global shared_state
                
                shared_state["departure_index"] = departure_listbox.get(selection[0])
                messagebox.showinfo("Success", f"Departure point selected: {shared_state['departure_index']}")

            def confirm_selection_destination():
                # Also includes errors
                selection = destination_listbox.curselection()
                if not selection:
                    messagebox.showerror("Error", "Please select a destination point.")
                    return
                
                global shared_state


                shared_state["destination_index"] = destination_listbox.get(selection[0])

                if shared_state["departure_index"] is None:
                    messagebox.showerror("Error", "Please select a departure point first.")
                    return

                if shared_state["departure_index"] == shared_state["destination_index"]:
                    messagebox.showerror("Error", "Departure and destination points cannot be the same.")
                else:
                    messagebox.showinfo(
                        "Success",
                        f"Route selected: {shared_state['departure_index']} to {shared_state['destination_index']}",
                    )
                    route_window.destroy()

            # Add buttons to confirm the selection
            confirm_departure_button = tk.Button(
                route_window, text="Confirm Departure", command=confirm_selection_departure
            )
            confirm_departure_button.pack(pady=10)

            confirm_destination_button = tk.Button(
                route_window, text="Confirm Destination", command=confirm_selection_destination
            )
            confirm_destination_button.pack(pady=10)

            # Add a button to close the window
            close_button = tk.Button(route_window, text="Close", command=route_window.destroy)
            close_button.pack(pady=10)

            route_window.mainloop()


        # Start the Tkinter window in a separate thread
        # This might cause some trouble because of how Tkinter and Pygame manage threads
        threading.Thread(target=create_window, daemon=True).start()

    # Buttons

    play_pause_button = Button(WINDOW_WIDTH - 110, 10, 100, 50, "Play", toggle_play_pause)
    reset_button = Button(WINDOW_WIDTH - 110, 70, 100, 50, "Reset", reset_simulation)
    menu_button = Button(10, 10, 100, 50, "Menu", show_menu)
    stats_button = Button(WINDOW_WIDTH - 110, 130, 100, 50, "Stats", show_stats) 
    exit_button = Button(10, 70, 100, 50, "Exit", exit_program)
    rain_button = Button(10, WINDOW_HEIGHT - 60, 175, 50, "Starts raining", start_raining)
    select_route_button = Button(WINDOW_WIDTH // 2 - 100, 10, 200, 50, "Select Route", open_select_route_window)
    

   

    # Main game loop

    # Initialisations
    running = True
    clock = pygame.time.Clock()
    global is_raining
    is_raining = False
    violet_start_time = None  # Initialize violet vehicle start time
    violet_elapsed_time = 0  # Initialize violet vehicle elapsed time

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                # Turning on and off the spawnpoints
                for spawn_point in spawn_points:
                    if spawn_point.is_clicked(mouse_pos):
                        spawn_point.toggle_active()
                # Handle button events
                play_pause_button.handle_event(event)
                reset_button.handle_event(event)
                menu_button.handle_event(event)
                stats_button.handle_event(event)
                exit_button.handle_event(event)
                rain_button.handle_event(event)
                select_route_button.handle_event(event)

        # Get the elapsed time since the game started
        current_time = pygame.time.get_ticks()
        

        """ The roads, background, spawnpoints, intersections and trafficlights are drawn nevertheless, but all the 
        events and all animations depend on the state of the Play/Pause button """

         # Fill the screen with a slightly bluer color if raining
        if is_raining:
            screen.fill(RAINING_BG_COLOR)
        else:
            screen.fill(BACKGROUND_COLOR)

        # Draw roads
        for road in roads:
            road.draw(screen)
            pygame.draw.line(screen, (0, 255, 255), 
                        (road.x, road.y), 
                        (road.x + road.width, road.y + road.height), 1)

        # Draw spawn points
        for spawn_point in spawn_points:
            spawn_point.draw(screen)

        # Draw intersections
        for intersection in intersections:
            intersection.draw(screen)
            pygame.draw.circle(screen, (255, 0, 255), (intersection.x, intersection.y), 5)

        # The following only happens if the simulation is running, aka not in in Pause state

        if not is_paused:
            # Checking how many more vehicles to spawn
            if vehicle_spawned_count < total_vehicle_count:
                if current_time // 1000 > vehicle_spawn_timer:
                    for spawn_point in spawn_points:
                        if spawn_point.active:
                            # Only using active spawnpoints
                            for _ in range(VEHICLE_SPAWN_RATE):
                                vehicles.append(spawn_vehicle_on_road(spawn_point, "car", (1, 2)))  # Adjust shape/speed if needed
                                vehicle_spawned_count += 1
                    vehicle_spawn_timer = current_time // 1000  # Update the timer


             # Check if half of the total vehicles have been spawned and spawn a violet vehicle
            global shared_state, violet_vehicle_spawned
            if vehicle_spawned_count >= total_vehicle_count // 2 and not violet_vehicle_spawned:
                # Only if a specific route has been chosen
                if shared_state["departure_index"] is not None and shared_state["destination_index"] is not None:
                    # Getting the departure and the destination
                    departure_spawn_point = next(sp for sp in spawn_points if f"Spawn Point {sp.index}" == shared_state["departure_index"])
                    destination_intersection = next(i for i in intersections if f"Intersection {i.index}" == shared_state["destination_index"])

                    # Instantienting and setting all te flags to highlight the violet vehicle
                    violet_vehicle = Vehicle(departure_spawn_point.pos[0], departure_spawn_point.pos[1], "car", (1, 2), "right")
                    violet_vehicle.color = VIOLET_COLOR  # Violet color
                    violet_vehicle.violet_flag = True
                    violet_vehicle.current_road = departure_spawn_point.road  # Assign the road of the spawn point
                    violet_vehicle.destination = destination_intersection  # Set the destination

                    # Setting the direction depending on the spawn
                    if violet_vehicle.x - 50 < 0:
                        violet_vehicle.direction = "right"
                    elif violet_vehicle.x + 50 > WINDOW_WIDTH:
                        violet_vehicle.direction = "left"
                    elif violet_vehicle.y -50 < 0:
                        violet_vehicle.direction = "down"
                    else:
                        violet_vehicle.direction = "up"

                    vehicles.append(violet_vehicle)
                    violet_vehicle_spawned = True
                    violet_start_time = current_time  # Start the violet vehicle timer

            # Update the violet vehicle elapsed time
            if violet_vehicle_spawned and violet_start_time is not None:
                violet_elapsed_time = (current_time - violet_start_time) / 1000  # Calculate elapsed time in seconds

            for intersection in intersections:
                intersection.update_cars_waiting(vehicles)
                intersection.toggle_traffic_lights()

            for vehicle in vehicles:
                vehicle_near_intersection = False
                for intersection in intersections:
                    # Check proximity to the intersection based on direction and how close to the intersection the vehicle is
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
            vehicle.draw(screen)

        # Despawning vehicles to improve performance
        vehicles = [vehicle for vehicle in vehicles if vehicle.x >= 0 and vehicle.x <= WINDOW_WIDTH and vehicle.y >= 0 and vehicle.y <= WINDOW_HEIGHT]
        

        for vehicle in vehicles:
            # idem, but for the violet vehicle
            # also manages to stop of the violet timer
            if vehicle.violet_flag and violet_start_time and vehicle.current_intersection == vehicle.destination:
                violet_elapsed_time = (current_time - violet_start_time) / 1000  # Finalize elapsed time
                violet_start_time = None  # Stop the timer
                # violet_vehicle_arrived = True  # Set the flag to indicate arrival
                vehicles.remove(vehicle)  # Despawn the violet vehicle

        # Buttons

        play_pause_button.draw(screen)
        reset_button.draw(screen)
        menu_button.draw(screen)
        stats_button.draw(screen)
        exit_button.draw(screen)
        rain_button.draw(screen)
        select_route_button.draw(screen)

        # Calculate and draw total waiting time
        draw_total_waiting_time(screen)

        # Draw elapsed time
        draw_elapsed_time(screen, start_time)

         # Draw violet vehicle elapsed time
        draw_violet_time(screen, violet_elapsed_time)


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
            # Saving user's information
            global GRID_SIZE, VEHICLE_SPAWN_RATE, VEHICLE_SPAWN_DURATION, ROAD_WIDTH, ROAD_HEIGHT
            GRID_SIZE = int(grid_size_entry.get())
            VEHICLE_SPAWN_RATE = int(car_number_entry.get())
            VEHICLE_SPAWN_DURATION = int(seconds_entry.get())
            # Calculating user depending data
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

    # Initialisations

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


    # Create a frame for buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)

    # Create the start smart simulation button
    start_smart_button = tk.Button(button_frame, text="Start Smart Simulation", command=lambda: start_simulation(root, True))
    start_smart_button.pack(expand=True, pady=10)

    # Create the start simulation button
    start_button = tk.Button(button_frame, text="Start Simulation", command=lambda: start_simulation(root, False))
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

def start_simulation(root, smart):
    root.destroy()  # Close the Tkinter window
    run_pygame_simulation(smart)  # Function to run the Pygame simulation

def show_menu():
    # Before going back to the menu, this function also effectively acts as a reset button
    global vehicles, vehicle_spawn_timer, vehicle_spawned_count, is_paused, elapsed_time, is_raining, simulation_ended, \
                paused_time, start_time, violet_vehicle_spawned, violet_elapsed_time, violet_start_time
    vehicles = []
    vehicle_spawn_timer = 0
    vehicle_spawned_count = 0
    is_paused = True
    globals.total_waiting_time = 0
    globals.break_count = 0
    elapsed_time = 0
    is_raining = False
    simulation_ended = False
    paused_time = 0
    start_time = None
    violet_vehicle_spawned = False
    violet_start_time = 0
    violet_elapsed_time = 0
    pygame.quit()
    initialize_tkinter_window()

def exit_simulation():
    pygame.quit()
    sys.exit()  # Terminate the program

def exit_program():
    sys.exit()


if __name__ == "__main__":
    initialize_tkinter_window()