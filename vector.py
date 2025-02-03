
import math

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
    
    def __truediv__(self, scalar):
        if scalar != 0:
            return Vector2D(self.x / scalar, self.y / scalar)
        return Vector2D()
    
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def distance_to(self, other):
        return (other - self).length()
    
    def normalized(self):
        length = self.length()
        if length != 0:
            return self / length
        return Vector2D()