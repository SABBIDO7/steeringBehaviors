class Arrival:
    def calculate(self, agent_pos, agent_vel, target_pos, target_vel, max_speed, max_force):
        direction = target_pos - agent_pos
        distance = direction.length()
        
        if distance < 100:  # Slowing radius
            desired_speed = max_speed * (distance / 100)
        else:
            desired_speed = max_speed
            
        desired_velocity = direction.normalized() * desired_speed
        steering = desired_velocity - agent_vel
        
        if steering.length() > max_force:
            steering = steering.normalized() * max_force
        return steering