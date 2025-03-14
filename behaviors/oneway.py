from behaviors.arrival import Arrival
from behaviors.seek import Seek
from vector import Vector2D

class OneWay:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.waypoints = [
            Vector2D(200, 200),
            Vector2D(600, 200),
            Vector2D(600, 400)
        ]
        self.current_waypoint = 0
        self.finished = False
    
    def calculate(self, agent_pos, agent_vel, target_pos, target_vel, max_speed, max_force):
        if self.finished:
            # Arrival when finished to maintain position
            target = self.waypoints[-1]
            return Arrival().calculate(agent_pos, agent_vel, target, target_vel, max_speed, max_force)
            
        target = self.waypoints[self.current_waypoint]
        if agent_pos.distance_to(target) < 5:
            if self.current_waypoint < len(self.waypoints) - 1:
                self.current_waypoint += 1
            else:
                self.finished = True
            target = self.waypoints[self.current_waypoint]
        
        return Seek().calculate(agent_pos, agent_vel, target, target_vel, max_speed, max_force)