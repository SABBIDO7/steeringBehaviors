
import math

class Vector2D:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def rotate(self, angle):
        """Rotate this vector by a given angle (in degrees)."""
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        print("trying to rotate")
        new_x = self.x * cos_a - self.y * sin_a
        new_y = self.x * sin_a + self.y * cos_a
        self.x, self.y = new_x, new_y  # Update in place


    
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