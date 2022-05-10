from CarriageNode import Carriage_Node

class Carriage:
    def __init__(self, line_occupied, fractional_position, length, type="default"):
        self.length = length
        self.type = type
        self.front = Carriage_Node(line_occupied, fractional_position)
        self.back =  Carriage_Node(line_occupied, fractional_position)
    
    def get_leader(self, velocity):
        if velocity > 0:
            return self.front
        else:
            return self.back
    
    def get_follower(self,velocity):
        if velocity > 0:
            return self.back
        else:
            return self.front