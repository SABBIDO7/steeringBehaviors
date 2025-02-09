from behaviors.arrival import Arrival
from vector import Vector2D


class TwoWay:
    def __init__(self):
        self.waypoints = [
            Vector2D(200, 200),
            Vector2D(600, 200),
            Vector2D(600, 400)
        ]
        self.current_waypoint = 0
        self.direction = 1  # 1 for forward, -1 for backward
    
    def calculate(self, agent_pos, agent_vel, target_pos, target_vel, max_speed, max_force):
        target = self.waypoints[self.current_waypoint]
        if agent_pos.distance_to(target) < 5:
            if self.direction == 1 and self.current_waypoint == len(self.waypoints) - 1:
                self.direction = -1
            elif self.direction == -1 and self.current_waypoint == 0:
                self.direction = 1
            else:
                self.current_waypoint += self.direction
            target = self.waypoints[self.current_waypoint]
        
        return Arrival().calculate(agent_pos, agent_vel, target, target_vel, max_speed, max_force)