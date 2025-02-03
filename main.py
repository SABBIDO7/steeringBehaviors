
import tkinter as tk
from tkinter import ttk
import math
from behaviors.seek import Seek
from behaviors.flee import Flee
from behaviors.pursuit import Pursuit
from behaviors.evade import Evade
from behaviors.arrival import Arrival
from behaviors.circuit import Circuit
from behaviors.oneway import OneWay
from behaviors.twoway import TwoWay
from vector import Vector2D

class SteeringGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Steering Behaviors")
        
        # Canvas setup
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='lightblue')
        self.canvas.pack(side=tk.TOP, pady=10)
        
        # Draw grid
        self.draw_grid()
        
        # Control panel
        self.control_panel = ttk.Frame(self.root)
        self.control_panel.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        # Sliders frame
        self.sliders_frame = ttk.Frame(self.root)
        self.sliders_frame.pack(side=tk.TOP, fill=tk.X, padx=10)
        
        # Speed slider
        ttk.Label(self.sliders_frame, text="Speed").pack(side=tk.TOP, anchor=tk.W)
        self.speed_slider = ttk.Scale(self.sliders_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.speed_slider.set(50)
        self.speed_slider.pack(fill=tk.X)
        
        # Force slider
        ttk.Label(self.sliders_frame, text="Force").pack(side=tk.TOP, anchor=tk.W)
        self.force_slider = ttk.Scale(self.sliders_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.force_slider.set(50)
        self.force_slider.pack(fill=tk.X)
        
        # Create behavior buttons
        self.behaviors = ['Seek', 'Flee', 'Pursuit', 'Evade', 'Arrival', 'Circuit', 'One Way', 'Two Ways']
        self.current_behavior = None
        self.create_behavior_buttons()
        
        # Initialize agents
        self.agent_pos = Vector2D(400, 300)
        self.agent_vel = Vector2D(0, 0)
        self.target_pos = Vector2D(600, 300)
        self.target_vel = Vector2D(0, 0)
        
        # Initialize behavior instances
        self.behavior_instances = {}
        
        # Draw initial state
        self.draw_agent()
        self.draw_target()
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        
        # Animation
        self.is_running = True
        self.update()
    
    def draw_grid(self):
        # Draw vertical lines
        for i in range(0, 800, 50):
            self.canvas.create_line(i, 0, i, 600, fill='gray90')
        # Draw horizontal lines
        for i in range(0, 600, 50):
            self.canvas.create_line(0, i, 800, i, fill='gray90')
    
    def create_behavior_buttons(self):
        for behavior in self.behaviors:
            btn = ttk.Button(self.control_panel, text=behavior,
                           command=lambda b=behavior: self.set_behavior(b))
            btn.pack(side=tk.LEFT, padx=5)
    
    def set_behavior(self, behavior):
        self.current_behavior = behavior
        # Reset agent velocity when changing behaviors
        self.agent_vel = Vector2D(0, 0)
        # Reset the behavior instance if it exists
        if behavior in self.behavior_instances:
            if hasattr(self.behavior_instances[behavior], 'reset'):
                self.behavior_instances[behavior].reset()
        # Update title
        self.root.title(f"Steering Behaviors - Current Mode: {behavior}")
    
    def draw_agent(self):
        self.canvas.delete("agent")
        x, y = self.agent_pos.x, self.agent_pos.y
        
        # Calculate angle based on velocity
        if self.agent_vel.length() > 0.1:
            angle = math.atan2(self.agent_vel.y, self.agent_vel.x)
        else:
            # Use previous angle or default if no velocity
            angle = 0
            
        # Create triangle points
        size = 10
        points = [
            (x + size * math.cos(angle), y + size * math.sin(angle)),
            (x + size * math.cos(angle + 2.6), y + size * math.sin(angle + 2.6)),
            (x + size * math.cos(angle - 2.6), y + size * math.sin(angle - 2.6))
        ]
        self.canvas.create_polygon(points, fill='red', tags="agent")
    
    def draw_target(self):
        self.canvas.delete("target")
        x, y = self.target_pos.x, self.target_pos.y
        size = 10
        self.canvas.create_oval(x-size, y-size, x+size, y+size, 
                              outline='black', width=2, tags="target")
        self.canvas.create_line(x-size, y, x+size, y, 
                              fill='black', width=2, tags="target")
        self.canvas.create_line(x, y-size, x, y+size, 
                              fill='black', width=2, tags="target")
    
    def on_click(self, event):
        self.target_pos = Vector2D(event.x, event.y)
        self.draw_target()
    
    def on_drag(self, event):
        self.target_pos = Vector2D(event.x, event.y)
        self.draw_target()
    
    def get_behavior_instance(self, behavior_name):
        if behavior_name not in self.behavior_instances:
            # Handle special case for "Two Ways"
            if behavior_name == "Two Ways":
                behavior_class = TwoWay
            else:
                behavior_class = globals()[behavior_name.replace(" ", "")]
            self.behavior_instances[behavior_name] = behavior_class()
        return self.behavior_instances[behavior_name]
    
    def update(self):
        if self.current_behavior:
            # Get behavior instance
            behavior = self.get_behavior_instance(self.current_behavior)
            
            # Get max speed and force from sliders
            max_speed = self.speed_slider.get() * 0.5  # Reduced multiplier
            max_force = self.force_slider.get() * 0.2  # Reduced multiplier
            
            # Calculate steering force
            steering = behavior.calculate(
                self.agent_pos, self.agent_vel,
                self.target_pos, self.target_vel,
                max_speed, max_force
            )
            
            # Update velocity with steering force
            self.agent_vel += steering
            
            # Limit velocity to max speed
            speed = self.agent_vel.length()
            if speed > max_speed:
                self.agent_vel = self.agent_vel.normalized() * max_speed
            
            # Update position
            dt = 0.16  # Time step
            self.agent_pos += self.agent_vel * dt
            
            # Keep agent within bounds with bounce
            if self.agent_pos.x < 0:
                self.agent_pos.x = 0
                self.agent_vel.x *= -0.5
            elif self.agent_pos.x > 800:
                self.agent_pos.x = 800
                self.agent_vel.x *= -0.5
                
            if self.agent_pos.y < 0:
                self.agent_pos.y = 0
                self.agent_vel.y *= -0.5
            elif self.agent_pos.y > 600:
                self.agent_pos.y = 600
                self.agent_vel.y *= -0.5
            
            # Redraw agent
            self.draw_agent()
        
        # Schedule next update
        if self.is_running:
            self.root.after(16, self.update)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = SteeringGame()
    game.run()