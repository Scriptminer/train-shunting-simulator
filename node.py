import math

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance_to(self,other):
        return math.sqrt(self.distance_squared_to(other))

    def distance_squared_to(self,other):
        return (other.x - self.x)**2 + (other.y - self.y)**2

    def __str__(self):
        return f"({self.x},{self.y})"

    def __eq__(self,other):
        return self.x == other.x and self.y == other.y
