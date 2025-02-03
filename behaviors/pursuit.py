from behaviors.seek import Seek


class Pursuit:
    def calculate(self, agent_pos, agent_vel, target_pos, target_vel, max_speed, max_force):
        prediction = 1.0
        future_pos = target_pos + target_vel * prediction
        return Seek().calculate(agent_pos, agent_vel, future_pos, target_vel, max_speed, max_force)