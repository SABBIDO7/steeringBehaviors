import tkinter as tk
import random
import math
from collections import deque

class Vector2D:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)

    def __eq__(self, other):
        if isinstance(other, Vector2D):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self):
        return hash((self.x, self.y))

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def length_squared(self):
        return self.x * self.x + self.y * self.y

    def distance_to(self, other):
        return (other - self).length()

    def normalized(self):
        length = self.length()
        if length == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / length, self.y / length)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def cross(self, other):
        return self.x * other.y - self.y * other.x
        
    def __repr__(self):
        return f"Vector2D({self.x}, {self.y})"

class Seek:
    def calculate(self, agent_pos, agent_vel, target_pos, target_vel, max_speed, max_force):
        desired_velocity = (target_pos - agent_pos).normalized() * max_speed
        steering = desired_velocity - agent_vel
        if steering.length() > max_force:
            steering = steering.normalized() * max_force
        return steering

class RescueSimulation:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Rescue Simulation")

        # Canvas setup
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='lightgray')
        self.canvas.pack(side=tk.TOP, pady=10)

        # Game controls
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        # Status label
        self.status_label = tk.Label(self.control_frame, text="Rescue Simulation Running")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Reset button
        self.reset_button = tk.Button(self.control_frame, text="Reset Simulation", command=self.reset_simulation)
        self.reset_button.pack(side=tk.RIGHT, padx=10)
        
        # Victim count input
        self.victim_frame = tk.Frame(self.control_frame)
        self.victim_frame.pack(side=tk.RIGHT, padx=10)
        tk.Label(self.victim_frame, text="Victims:").pack(side=tk.LEFT)
        self.victim_var = tk.StringVar(value="8")
        self.victim_entry = tk.Entry(self.victim_frame, textvariable=self.victim_var, width=3)
        self.victim_entry.pack(side=tk.LEFT)

        # Game elements
        self.grid_size = 50
        self.city_blocks = []
        self.victims = []
        self.hospitals = []
        self.waypoints = []
        self.waypoint_graph = {}
        
        # Entity states
        self.npc_pos = Vector2D(50, 50)
        self.npc_vel = Vector2D(0, 0)
        self.npc_target = None
        self.npc_carrying_victim = None
        self.npc_state = "searching"  # searching, rescuing, delivering
        
        self.player_pos = Vector2D(700, 500)
        self.player_vel = Vector2D(0, 0)
        self.player_target = None
        self.player_carrying_victim = None
        
        # Game parameters
        self.max_speed = 3
        self.max_force = 0.5
        self.seek = Seek()
        
        # Path finding variables
        self.npc_path = []
        self.current_waypoint_index = 0
        self.rescued_count = 0
        
        # Initialize game setup
        self.setup_game()
        
        # Bind mouse click for player movement
        self.canvas.bind("<Button-1>", self.on_mouse_click)
        
        # Start game loop
        self.update()

    def setup_game(self):
        """Initialize the game world with all elements"""
        self.setup_city()
        self.setup_waypoints()
        self.create_hospitals()
        self.spawn_victims(int(self.victim_var.get()))

    def reset_simulation(self):
        """Reset the simulation state"""
        # Clear existing game objects
        self.victims = []
        self.npc_pos = Vector2D(50, 50)
        self.npc_vel = Vector2D(0, 0)
        self.npc_target = None
        self.npc_carrying_victim = None
        self.npc_state = "searching"
        self.npc_path = []
        self.current_waypoint_index = 0
        
        self.player_pos = Vector2D(700, 500)
        self.player_vel = Vector2D(0, 0)
        self.player_target = None
        self.player_carrying_victim = None
        
        self.rescued_count = 0
        
        # Spawn new victims
        self.spawn_victims(int(self.victim_var.get()))
        
        # Update status
        self.status_label.config(text=f"Simulation Reset. Victims: {len(self.victims)}")

    def setup_city(self):
        """Creates obstacles as city blocks."""
        for x in range(2, 14, 3):
            for y in range(2, 10, 3):
                block = {
                    'x': x * self.grid_size,
                    'y': y * self.grid_size,
                    'width': self.grid_size * 2,
                    'height': self.grid_size * 2
                }
                self.city_blocks.append(block)

    def setup_waypoints(self):
        """Setup the waypoints and their connections"""
        # Create key waypoints - representing street intersections
        self.waypoints = [
            Vector2D(50, 50),    # 0: Top-left
            Vector2D(750, 50),   # 1: Top-right
            Vector2D(750, 550),  # 2: Bottom-right
            Vector2D(50, 550),   # 3: Bottom-left
            Vector2D(50, 225),   # 4: Middle-left
            Vector2D(750, 225),  # 5: Middle-right
            Vector2D(50, 375),   # 6: Lower-middle-left
            Vector2D(750, 375),  # 7: Lower-middle-right
            Vector2D(225, 50),   # 8: Top-middle-left
            Vector2D(225, 550),  # 9: Bottom-middle-left
            Vector2D(375, 50),   # 10: Top-middle //here
            Vector2D(375, 550),  # 11: Bottom-middle
            Vector2D(525, 50),   # 12: Top-middle-right
            Vector2D(525, 550),  # 13: Bottom-middle-right
            Vector2D(225, 225),  # 14: Upper crossroad left
            Vector2D(375, 225),  # 15: Upper crossroad middle
            Vector2D(525, 225),  # 16: Upper crossroad right
            Vector2D(225, 375),  # 17: Lower crossroad left
            Vector2D(375, 375),  # 18: Lower crossroad middle
            Vector2D(525, 375)   # 19: Lower crossroad right
        ]
        
        # Define connections between waypoints (representing streets)
        self.waypoint_graph = {
            # Top row connections
            self.waypoints[0]: [self.waypoints[8], self.waypoints[4], self.waypoints[3]],
            self.waypoints[8]: [self.waypoints[0], self.waypoints[10], self.waypoints[14]],
            self.waypoints[10]: [self.waypoints[8], self.waypoints[12], self.waypoints[15]],
            self.waypoints[12]: [self.waypoints[10], self.waypoints[1], self.waypoints[16]],
            self.waypoints[1]: [self.waypoints[12], self.waypoints[5], self.waypoints[2]],
            
            # Middle row connections
            self.waypoints[4]: [self.waypoints[0], self.waypoints[14], self.waypoints[6]],
            self.waypoints[14]: [self.waypoints[8], self.waypoints[4], self.waypoints[15], self.waypoints[17]],
            self.waypoints[15]: [self.waypoints[10], self.waypoints[14], self.waypoints[16], self.waypoints[18]],
            self.waypoints[16]: [self.waypoints[12], self.waypoints[15], self.waypoints[5], self.waypoints[19]],
            self.waypoints[5]: [self.waypoints[1], self.waypoints[16], self.waypoints[7]],
            
            # Lower middle row connections
            self.waypoints[6]: [self.waypoints[4], self.waypoints[17], self.waypoints[3]],
            self.waypoints[17]: [self.waypoints[14], self.waypoints[6], self.waypoints[18], self.waypoints[9]],
            self.waypoints[18]: [self.waypoints[15], self.waypoints[17], self.waypoints[19], self.waypoints[11]],
            self.waypoints[19]: [self.waypoints[16], self.waypoints[18], self.waypoints[7], self.waypoints[13]],
            self.waypoints[7]: [self.waypoints[5], self.waypoints[19], self.waypoints[2]],
            
            # Bottom row connections
            self.waypoints[3]: [self.waypoints[0], self.waypoints[6], self.waypoints[9]],
            self.waypoints[9]: [self.waypoints[3], self.waypoints[17], self.waypoints[11]],
            self.waypoints[11]: [self.waypoints[9], self.waypoints[18], self.waypoints[13]],
            self.waypoints[13]: [self.waypoints[11], self.waypoints[19], self.waypoints[2]],
            self.waypoints[2]: [self.waypoints[1], self.waypoints[7], self.waypoints[13]]
        }

    def spawn_victims(self, count):
        """Place victims on the map avoiding obstacles."""
        self.victims = []
        attempted = 0
        while len(self.victims) < count and attempted < 100:
            attempted += 1
            # Try placing at waypoints first (more realistic - victims on streets)
            if len(self.victims) < count * 0.7 and self.waypoints:
                waypoint = random.choice(self.waypoints)
                # Add slight variation to position
                x = waypoint.x + random.randint(-15, 15)
                y = waypoint.y + random.randint(-15, 15)
            else:
                # Place randomly ensuring not too close to edges
                x = random.randint(50, 750)
                y = random.randint(50, 550)
            
            # Check if valid position
            if self.is_valid_position(x, y):
                # Check if not too close to existing victims
                too_close = False
                for victim in self.victims:
                    if Vector2D(x, y).distance_to(victim) < 30:
                        too_close = True
                        break
                
                # Check if not too close to hospitals
                for hospital in self.hospitals:
                    if Vector2D(x, y).distance_to(hospital) < 50:
                        too_close = True
                        break
                        
                if not too_close:
                    self.victims.append(Vector2D(x, y))
                    
        self.status_label.config(text=f"Victims spawned: {len(self.victims)}")

    def create_hospitals(self):
        """Places hospitals at fixed positions."""
        self.hospitals = []
        self.hospitals.append(Vector2D(50, 50))  # Top-left hospital
        self.hospitals.append(Vector2D(750, 550))  # Bottom-right hospital

    def find_closest(self, position, entities):
        """Find the closest entity to a given position."""
        if not entities:
            return None
        return min(entities, key=lambda e: position.distance_to(e))

    def is_valid_position(self, x, y, radius=15):
        """Check if position collides with a city block."""
        for block in self.city_blocks:
            if (x > block['x'] - radius and x < block['x'] + block['width'] + radius and
                y > block['y'] - radius and y < block['y'] + block['height'] + radius):
                return False
        return True

    def get_closest_waypoint(self, position):
        """Find the closest waypoint to the given position."""
        if not self.waypoints:
            return None
        return min(self.waypoints, key=lambda w: position.distance_to(w))

    def bfs_find_path(self, start_pos, end_pos):
        """Find path from start to end using BFS on waypoint graph."""
        # First get closest waypoints to start and end positions
        start_waypoint = self.get_closest_waypoint(start_pos)
        end_waypoint = self.get_closest_waypoint(end_pos)
        
        if start_waypoint is None or end_waypoint is None:
            return [start_pos, end_pos]  # Direct line if no waypoints
            
        # If start and end are close enough, go direct
        if start_pos.distance_to(end_pos) < 100:
            return [start_pos, end_pos]
        
        # Use BFS to find path between waypoints
        queue = deque([(start_waypoint, [start_waypoint])])
        visited = set([start_waypoint])
        
        while queue:
            current, path = queue.popleft()
            
            if current == end_waypoint:
                # Complete path found, add start and end points
                complete_path = [start_pos]
                complete_path.extend(path)
                complete_path.append(end_pos)
                return complete_path
                
            for neighbor in self.waypoint_graph.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
                    
        # No path found between waypoints, try direct path
        return [start_pos, end_pos]

    def update_npc(self):
        """Update NPC behavior based on state and targets."""
        # State machine for NPC behavior
        if self.npc_state == "searching":
            # If not carrying a victim, find the closest one
            if not self.victims:
                self.status_label.config(text="All victims rescued!")
                return
                
            # Find closest victim if we don't have a target
            if self.npc_target is None:
                self.npc_target = self.find_closest(self.npc_pos, self.victims)
                if self.npc_target:
                    self.npc_path = self.bfs_find_path(self.npc_pos, self.npc_target)
                    self.current_waypoint_index = 0
            
            # If target exists but was rescued by player, find new target
            elif self.npc_target not in self.victims:
                self.npc_target = self.find_closest(self.npc_pos, self.victims)
                if self.npc_target:
                    self.npc_path = self.bfs_find_path(self.npc_pos, self.npc_target)
                    self.current_waypoint_index = 0
            
            # Check if NPC reached a victim
            if self.npc_target and self.npc_pos.distance_to(self.npc_target) < 15:
                self.npc_carrying_victim = self.npc_target
                if self.npc_target in self.victims:
                    self.victims.remove(self.npc_target)
                
                # Switch to delivering state
                self.npc_state = "delivering"
                self.npc_target = self.find_closest(self.npc_pos, self.hospitals)
                if self.npc_target:
                    self.npc_path = self.bfs_find_path(self.npc_pos, self.npc_target)
                    self.current_waypoint_index = 0

        elif self.npc_state == "delivering":
            # If carrying a victim, head to hospital
            if self.npc_target is None or self.npc_target not in self.hospitals:
                self.npc_target = self.find_closest(self.npc_pos, self.hospitals)
                if self.npc_target:
                    self.npc_path = self.bfs_find_path(self.npc_pos, self.npc_target)
                    self.current_waypoint_index = 0
            
            # Check if NPC reached a hospital
            if self.npc_target and self.npc_pos.distance_to(self.npc_target) < 15:
                self.npc_carrying_victim = None
                self.rescued_count += 1
                self.status_label.config(text=f"Victims rescued: {self.rescued_count} | Remaining: {len(self.victims)}")
                
                # Switch back to searching state
                self.npc_state = "searching"
                self.npc_target = self.find_closest(self.npc_pos, self.victims)
                if self.npc_target:
                    self.npc_path = self.bfs_find_path(self.npc_pos, self.npc_target)
                    self.current_waypoint_index = 0
        
        # Move NPC along path regardless of state
        self.move_along_path()
    
    def move_along_path(self):
        """Move NPC along the calculated path."""
        if not self.npc_path or self.current_waypoint_index >= len(self.npc_path):
            return
            
        current_target = self.npc_path[self.current_waypoint_index]
        
        # If close to current waypoint, move to next one
        if self.npc_pos.distance_to(current_target) < 10:
            self.current_waypoint_index += 1
            if self.current_waypoint_index >= len(self.npc_path):
                # End of path reached
                self.npc_vel = Vector2D(0, 0)
                return
            current_target = self.npc_path[self.current_waypoint_index]
        
        # Calculate steering force towards current waypoint
        steering = self.seek.calculate(
            self.npc_pos, self.npc_vel,
            current_target, Vector2D(0, 0),
            self.max_speed, self.max_force
        )
        
        # Apply steering force
        self.npc_vel = self.npc_vel + steering
        
        # Limit speed
        if self.npc_vel.length() > self.max_speed:
            self.npc_vel = self.npc_vel.normalized() * self.max_speed
            
        # Move NPC
        new_pos = self.npc_pos + self.npc_vel
        
        # Check if new position is valid (not inside obstacle)
        if self.is_valid_position(new_pos.x, new_pos.y):
            self.npc_pos = new_pos
        else:
            # If invalid, try to steer around obstacle
            self.avoid_obstacle()
            
    def avoid_obstacle(self):
        """Simple obstacle avoidance behavior."""
        # Get the closest waypoint
        closest_waypoint = self.get_closest_waypoint(self.npc_pos)
        
        if closest_waypoint:
            # Try steering towards the closest waypoint
            steering = self.seek.calculate(
                self.npc_pos, self.npc_vel,
                closest_waypoint, Vector2D(0, 0),
                self.max_speed, self.max_force * 2  # Stronger force to avoid obstacle
            )
            
            # Apply steering
            self.npc_vel = self.npc_vel + steering
            
            # Limit speed
            if self.npc_vel.length() > self.max_speed:
                self.npc_vel = self.npc_vel.normalized() * self.max_speed
                
            # Move NPC
            new_pos = self.npc_pos + self.npc_vel
            
            # Check if new position is valid
            if self.is_valid_position(new_pos.x, new_pos.y):
                self.npc_pos = new_pos
            else:
                # If still invalid, try random direction
                self.npc_vel = Vector2D(random.uniform(-1, 1), random.uniform(-1, 1)).normalized() * self.max_speed
                
    def on_mouse_click(self, event):
        """Handle mouse click for player movement."""
        x, y = event.x, event.y
        
        # Check if clicking on a victim (to pick up)
        if not self.player_carrying_victim:
            for victim in self.victims:
                if victim.distance_to(Vector2D(x, y)) < 15:
                    # Set target to victim position for pickup
                    self.player_target = victim
                    return
        
        # Check if clicking on a hospital (to drop off)
        if self.player_carrying_victim:
            for hospital in self.hospitals:
                if hospital.distance_to(Vector2D(x, y)) < 30:
                    # Set target to hospital position for dropoff
                    self.player_target = hospital
                    return
        
        # Otherwise, set target to mouse position if valid
        if self.is_valid_position(x, y):
            self.player_target = Vector2D(x, y)
    
    def update_player(self):
        """Update player position and actions."""
        if self.player_target:
            # Calculate steering force
            steering = self.seek.calculate(
                self.player_pos, self.player_vel,
                self.player_target, Vector2D(0, 0),
                self.max_speed, self.max_force
            )
            
            # Apply steering
            self.player_vel = self.player_vel + steering
            
            # Limit speed
            if self.player_vel.length() > self.max_speed:
                self.player_vel = self.player_vel.normalized() * self.max_speed
                
            # Move player
            new_pos = self.player_pos + self.player_vel
            
            # Check if new position is valid
            if self.is_valid_position(new_pos.x, new_pos.y):
                self.player_pos = new_pos
            
            # Check if reached target
            if self.player_pos.distance_to(self.player_target) < 10:
                # Check if target is a victim (for pickup)
                if not self.player_carrying_victim and self.player_target in self.victims:
                    self.player_carrying_victim = self.player_target
                    self.victims.remove(self.player_target)
                    self.status_label.config(text=f"Player picked up victim. Remaining: {len(self.victims)}")
                
                # Check if target is a hospital (for dropoff)
                elif self.player_carrying_victim:
                    for hospital in self.hospitals:
                        if self.player_pos.distance_to(hospital) < 20:
                            self.player_carrying_victim = None
                            self.rescued_count += 1
                            self.status_label.config(text=f"Victims rescued: {self.rescued_count} | Remaining: {len(self.victims)}")
                            break
                
                # Reset target
                self.player_target = None
                self.player_vel = Vector2D(0, 0)
    
    def draw(self):
        """Draw all game elements to the canvas."""
        self.canvas.delete("all")
        
        # Draw waypoint connections (streets)
        for waypoint, neighbors in self.waypoint_graph.items():
            for neighbor in neighbors:
                self.canvas.create_line(
                    waypoint.x, waypoint.y, 
                    neighbor.x, neighbor.y, 
                    fill='darkgray', width=5
                )
        
        # Draw city blocks (buildings)
        for block in self.city_blocks:
            self.canvas.create_rectangle(
                block['x'], block['y'],
                block['x'] + block['width'],
                block['y'] + block['height'],
                fill='gray', outline='black'
            )
        
        # Draw waypoints
        for waypoint in self.waypoints:
            self.canvas.create_oval(
                waypoint.x - 3, waypoint.y - 3,
                waypoint.x + 3, waypoint.y + 3,
                fill='gray', outline='gray'
            )
        
        # Draw hospitals
        for hospital in self.hospitals:
            self.canvas.create_rectangle(
                hospital.x - 20, hospital.y - 20,
                hospital.x + 20, hospital.y + 20,
                fill='white', outline='red', width=2
            )
            self.canvas.create_text(
                hospital.x, hospital.y,
                text="H", fill='red', font=("Arial", 16, "bold")
            )
        
        # Draw victims
        for victim in self.victims:
            self.canvas.create_oval(
                victim.x - 10, victim.y - 10,
                victim.x + 10, victim.y + 10,
                fill='yellow', outline='black'
            )
            self.canvas.create_text(
                victim.x, victim.y,
                text="V", fill='black', font=("Arial", 10)
            )
        
        # Draw NPC's path
        if self.npc_path and len(self.npc_path) > 1:
            for i in range(len(self.npc_path) - 1):
                self.canvas.create_line(
                    self.npc_path[i].x, self.npc_path[i].y,
                    self.npc_path[i+1].x, self.npc_path[i+1].y,
                    fill='blue', width=2, dash=(4, 4)
                )
        
        # Draw NPC
        self.canvas.create_oval(
            self.npc_pos.x - 15, self.npc_pos.y - 15,
            self.npc_pos.x + 15, self.npc_pos.y + 15,
            fill='blue', outline='black'
        )
        self.canvas.create_text(
            self.npc_pos.x, self.npc_pos.y,
            text="NPC", fill='white', font=("Arial", 8)
        )
        
        # Draw carried victim for NPC
        if self.npc_carrying_victim:
            self.canvas.create_oval(
                self.npc_pos.x - 5, self.npc_pos.y - 5,
                self.npc_pos.x + 5, self.npc_pos.y + 5,
                fill='yellow', outline='black'
            )
        
        # Draw player
        self.canvas.create_oval(
            self.player_pos.x - 15, self.player_pos.y - 15,
            self.player_pos.x + 15, self.player_pos.y + 15,
            fill='green', outline='black'
        )
        self.canvas.create_text(
            self.player_pos.x, self.player_pos.y,
            text="P", fill='white', font=("Arial", 10)
        )
        
        # Draw carried victim for player
        if self.player_carrying_victim:
            self.canvas.create_oval(
                self.player_pos.x - 5, self.player_pos.y - 5,
                self.player_pos.x + 5, self.player_pos.y + 5,
                fill='yellow', outline='black'
            )
    
    def update(self):
        """Main game loop."""
        self.update_npc()
        self.update_player()
        self.draw()
        self.root.after(30, self.update)  # Update every 30ms (approx 33 FPS)
    
    def run(self):
        """Start the game."""
        self.root.mainloop()

if __name__ == "__main__":
    game = RescueSimulation()
    game.run()