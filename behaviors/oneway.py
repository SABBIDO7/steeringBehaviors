from behaviors.arrival import Arrival
from behaviors.seek import Seek
from vector import Vector2D


class OneWay:
    def __init__(self):
        self.waypoints = [
            Vector2D(200, 300),
            Vector2D(400, 200),
            Vector2D(600, 300)
        ]
        self.current_waypoint = 0
        self.finished = False
    
    def calculate(self, agent_pos, agent_vel, target_pos, target_vel, max_speed, max_force):
        if self.finished:
            return Vector2D()
            
        target = self.waypoints[self.current_waypoint]
        if agent_pos.distance_to(target) < 20:
            if self.current_waypoint < len(self.waypoints) - 1:
                self.current_waypoint += 1
            else:
                self.finished = True
                return Arrival().calculate(agent_pos, agent_vel, target, target_vel, max_speed, max_force)
        
        return Seek().calculate(agent_pos, agent_vel, target, target_vel, max_speed, max_force)
