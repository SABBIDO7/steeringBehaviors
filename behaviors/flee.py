class Flee:
    def calculate(self, agent_pos, agent_vel, target_pos, target_vel, max_speed, max_force):
        desired_velocity = (agent_pos - target_pos).normalized() * max_speed
        steering = desired_velocity - agent_vel
        if steering.length() > max_force:
            steering = steering.normalized() * max_force
        return steering