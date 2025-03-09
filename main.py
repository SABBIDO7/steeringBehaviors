import tkinter as tk
from tkinter import ttk
import random
from vector import Vector2D
from behaviors.seek import Seek

class RescueSimulation:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Rescue Simulation")

        # Canvas setup
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='lightgray')
        self.canvas.pack(side=tk.TOP, pady=10)

        # Game elements
        self.grid_size = 50
        self.city_blocks = []
        self.victims = []
        self.hospitals = []
        self.npc_pos = Vector2D(0, 0)  # Initial position of the NPC
        self.npc_vel = Vector2D(1, 0)  # Initial velocity
        self.player_pos = Vector2D(700, 500)
        self.player_vel = Vector2D(0, 0)
        self.player_target = None

        # Game state
        self.npc_carrying_victim = None
        self.player_carrying_victim = None
        self.max_speed = 3
        self.max_force = 0.5

        # Initialize behaviors
        self.seek = Seek()

        # Initialize game elements
        self.setup_city()
        self.spawn_victims(5)  # Spawn 5 victims
        self.create_hospitals()

        # NPC initial target
        self.npc_target = None

        # Bind mouse click for movement
        self.root.bind("<Button-1>", self.on_mouse_click)

        # Start game loop
        self.update()

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

    def is_valid_position(self, x, y, radius=15):
        """Check if position collides with a city block."""
        for block in self.city_blocks:
            if (x > block['x'] - radius and x < block['x'] + block['width'] + radius and
                y > block['y'] - radius and y < block['y'] + block['height'] + radius):
                return False  # Invalid position
        return True  # Valid position

    def spawn_victims(self, count):
        """Randomly place victims avoiding obstacles."""
        for _ in range(count):
            while True:
                x = random.randint(50, 750)
                y = random.randint(50, 550)
                if self.is_valid_position(x, y):
                    self.victims.append(Vector2D(x, y))
                    break

    def create_hospitals(self):
        """Places hospitals in fixed positions."""
        self.hospitals.append(Vector2D(50, 50))
        self.hospitals.append(Vector2D(750, 550))

    def find_closest(self, entity, entities):
        """Find the closest entity to a given position."""
        if not entities:
            return None
        return min(entities, key=lambda e: entity.distance_to(e))

    def update_npc(self):
        """NPC moves to the nearest victim, picks it up, then moves to the hospital."""

        if self.npc_carrying_victim is None:
            self.npc_target = self.find_closest(self.npc_pos, self.victims)
            if self.npc_target is None: # No more victims
                return # Or give the NPC a new task/behavior

            if self.npc_target and self.npc_pos.distance_to(self.npc_target) < 10:
                self.npc_carrying_victim = self.npc_target
                self.victims.remove(self.npc_target)
                self.npc_target = self.find_closest(self.npc_pos, self.hospitals) # Find a hospital *after* picking up victim

        elif self.npc_target and self.npc_pos.distance_to(self.npc_target) < 10:  # Check for hospital and drop-off
            self.npc_carrying_victim = None
            self.npc_target = self.find_closest(self.npc_pos, self.victims) # Look for another victim
            if self.npc_target is None:
                return  # Or assign a new task


        # IMPORTANT: Check for a valid target *before* using it
        if self.npc_target:  # Only proceed if there's a target
            steering = self.seek.calculate(
                self.npc_pos, self.npc_vel,
                self.npc_target, Vector2D(0, 0),  # Use Vector2D(0, 0) for static target velocity
                self.max_speed, self.max_force
            )
            self.npc_vel += steering

            if self.npc_vel.length() > self.max_speed:
                self.npc_vel = self.npc_vel.normalized() * self.max_speed

            new_pos = self.npc_pos + self.npc_vel

            collision_detected = False
            if not self.is_valid_position(new_pos.x, new_pos.y):
                collision_detected = True

            if collision_detected:
                print(f"Collision detected at {new_pos.x}, {new_pos.y}. Finding new path...")
                self.resolve_collision() # New collision resolution function
            else:
                self.npc_pos = new_pos

    def resolve_collision(self):
        """Attempts to find a valid position by rotating and checking a few nearby positions."""

        for _ in range(36):  # Try 36 different angles (every 10 degrees)
            self.npc_vel.rotate(20)
            new_pos = self.npc_pos + self.npc_vel
            if self.is_valid_position(new_pos.x, new_pos.y):
                self.npc_pos = new_pos
                return  # Found a valid position, exit the loop
            
        # If all else fails, more drastic action: teleport short distance or backtrack
        print("Stuck! Teleporting slightly...")
        valid_position_found = False
        for _ in range(50): # Try 50 random nearby locations
          random_offset = Vector2D(random.uniform(-30, 30), random.uniform(-30, 30)) # Random offset
          potential_pos = self.npc_pos + random_offset
          if self.is_valid_position(potential_pos.x, potential_pos.y):
            self.npc_pos = potential_pos
            valid_position_found = True
            break # Exit after a valid position is found
        if not valid_position_found:
            print("Still Stuck!!!")
            # Implement backtracking logic here if desired
    def on_mouse_click(self, event):
        """Set the player's target position when clicking."""
        target_x, target_y = event.x, event.y
        if self.is_valid_position(target_x, target_y):
            self.player_target = Vector2D(target_x, target_y)

    def update_player(self):
        """Move player toward target and pick up/drop off victims."""
        if self.player_target:
            steering = self.seek.calculate(
                self.player_pos, self.player_vel,
                self.player_target, Vector2D(0, 0),
                self.max_speed, self.max_force
            )

            self.player_vel += steering
            if self.player_vel.length() > self.max_speed:
                self.player_vel = self.player_vel.normalized() * self.max_speed

            # Predict new position and move only if valid
            new_pos = self.player_pos + self.player_vel
            if self.is_valid_position(new_pos.x, new_pos.y):
                self.player_pos = new_pos

            # Stop moving when close to target
            if self.player_pos.distance_to(self.player_target) < 5:
                self.player_target = None
                self.player_vel = Vector2D(0, 0)

        # Pick up a victim
        if self.player_carrying_victim is None:
            for victim in self.victims:
                if self.player_pos.distance_to(victim) < 15:
                    self.player_carrying_victim = victim
                    self.victims.remove(victim)
                    break

        # Drop off at hospital
        if self.player_carrying_victim:
            nearest_hospital = self.find_closest(self.player_pos, self.hospitals)
            if nearest_hospital and self.player_pos.distance_to(nearest_hospital) < 15:
                self.player_carrying_victim = None

    def draw(self):
        self.canvas.delete("all")

        # Draw city blocks
        for block in self.city_blocks:
            self.canvas.create_rectangle(
                block['x'], block['y'],
                block['x'] + block['width'],
                block['y'] + block['height'],
                fill='gray'
            )

        # Draw hospitals
        for hospital in self.hospitals:
            self.canvas.create_rectangle(hospital.x - 20, hospital.y - 20, hospital.x + 20, hospital.y + 20, fill='white', outline='red')

        # Draw victims
        for victim in self.victims:
            self.canvas.create_oval(victim.x - 10, victim.y - 10, victim.x + 10, victim.y + 10, fill='yellow')

        # Draw NPC and player
        self.canvas.create_oval(self.npc_pos.x - 15, self.npc_pos.y - 15, self.npc_pos.x + 15, self.npc_pos.y + 15, fill='blue')
        self.canvas.create_oval(self.player_pos.x - 15, self.player_pos.y - 15, self.player_pos.x + 15, self.player_pos.y + 15, fill='green')

    def update(self):
        self.update_npc()
        self.update_player()
        self.draw()
        self.root.after(16, self.update)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = RescueSimulation()
    game.run()
