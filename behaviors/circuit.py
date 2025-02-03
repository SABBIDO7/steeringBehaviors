from behaviors.seek import Seek
from vector import Vector2D


class Circuit:
    def __init__(self):
        self.waypoints = [
            Vector2D(200, 200),
            Vector2D(600, 200),
            Vector2D(600, 400),
            Vector2D(200, 400)
        ]
        self.current_waypoint = 0
    
    def calculate(self, agent_pos, agent_vel, target_pos, target_vel, max_speed, max_force):
        target = self.waypoints[self.current_waypoint]
        if agent_pos.distance_to(target) < 20:
            self.current_waypoint = (self.current_waypoint + 1) % len(self.waypoints)
            target = self.waypoints[self.current_waypoint]
        
        return Seek().calculate(agent_pos, agent_vel, target, target_vel, max_speed, max_force)