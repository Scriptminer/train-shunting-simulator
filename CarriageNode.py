
from node import Node
from line import Line
from junctions import Standard_Points, Buffer

class State():
    def __init__(self, fractional_position, line_occupied, direction):
        self.fractional_position = fractional_position
        self.line_occupied = line_occupied
        self.direction = direction
    
    def as_dict(self):
        return {"fractional_position":self.fractional_position, "line_occupied":self.line_occupied, "direction":self.direction} # Position one step prior to current step
    
    @classmethod
    def from_dict(cls, state_dict):
        return cls(state_dict["fractional_position"], state_dict["line_occupied"], state_dict["direction"])
    
    @classmethod
    def from_carriage_node(cls, node):
        return cls(node.fractional_position, node.line_occupied, node.direction)
    
    def __str__(self):
        return f"{self.fractional_position} on line {self.line_occupied}, Direction: {self.direction}"
    
class Carriage_Node():
    def __init__(self, line_occupied, fractional_position=0):
        self.line_occupied = line_occupied
        self.fractional_position = fractional_position
        self.direction = 1 # 1 if the line segment is start - finish ()
        self.is_ends_node = False # Whether this node is a node at either end of the train. Set to True on train construction
        
        self.save_state()
    
    def save_state(self):
        self.previous_state = State.from_carriage_node(self)
        
    def get_state(self):
        return State.from_carriage_node(self).as_dict()
    
    def get_previous_state(self):
        return self.previous_state.as_dict()
    
    def undo_step(self):
        self.fractional_position = self.previous_state.fractional_position
        self.line_occupied = self.previous_state.line_occupied
        self.direction = self.previous_state.direction
    
    def step(self, velocity, save=False):
        """ Move forward a fixed distance. Returns True on any movement. """
        # Error codes: 0 - success, 1 - failure
        if save:
            self.save_state()
        
        velocity *= self.direction # The velocity in the direction in which the train is treating this segment of track
        line_length = self.line_occupied.length
        fractional_change = velocity / line_length
        new_fractional_position = self.fractional_position + fractional_change
        
        if new_fractional_position >= 0 and new_fractional_position <= 1:
            # Staying on same line
            self.fractional_position = new_fractional_position
            return 0
        else:
            if new_fractional_position < 0:
                #print(f"Hit start junction {str(self.line_occupied.start_junction)}")
                junction = self.line_occupied.start_junction
                overshoot = 0 - new_fractional_position
            else: # new_fractional_position > 1
                #print(f"Hit end junction {str(self.line_occupied.end_junction)}")
                junction = self.line_occupied.end_junction
                overshoot = new_fractional_position - 1
            
        # Switch onto new track:
        if type(junction) != Standard_Points:
            return 1 # Train terminates

        nextline = junction.next(self.line_occupied)
        if nextline == None: # Train can't go this way!
            return 1
            
        print(f"Node at {self.get_location()} steps over junction {junction}. Velocity is currently {velocity} and direction is {self.direction}")
        if self.is_ends_node:
            junction.toggle_occupied()
        overshoot = overshoot * line_length # Gives overshoot as an absolute distance
        fractional_overshoot = overshoot / nextline.length # Overshoot as a fraction of the new line

        nextline_starts_here = (nextline.start_junction == junction)
        thisline_starts_here = (self.line_occupied.start_junction == junction)

        if nextline_starts_here:
            self.previous_state.fractional_position = 0
            self.fractional_position = 0 + fractional_overshoot
        else:
            self.previous_state.fractional_position = 1
            self.fractional_position = 1 - fractional_overshoot

        # If tracks are either nose-nose or tail-tail flip direction, otherwise do nothing:
        if (nextline_starts_here and thisline_starts_here) or ((not nextline_starts_here) and (not thisline_starts_here)):
            self.direction *= -1


        self.line_occupied = nextline
        return 0

    def follow(self, ahead_carriage_node, carriage_length, train_velocity):
        # Error Codes: 0 - success, 1 - failure
        relative_train_velocity = train_velocity # Initial value, independent of direction
        train_velocity *= self.direction # The velocity in the direction in which the train is treating this segment of track (absolute velocity on segment)
        # Find all points which are a carriage length away from
        # ahead_carriage_node on this line
        intersections = self.line_occupied.intersects_circle(ahead_carriage_node.get_position(), carriage_length)

        if train_velocity == 0:
            return 0

        def ahead_of(carriage_node1, carriage_node2):
            if train_velocity > 0: # Positive velocity along this line
                return (carriage_node1 > carriage_node2)
            else: # Negative velocity along this line
                return (carriage_node1 < carriage_node2)

        candidate_positions = []

        # Filter out positions "behind" the current position, or ahead of ahead_carriage_node
        for intersection in intersections:
            # Check intersection is ahead of current position
            if ahead_of(intersection,self.fractional_position):
                if self.line_occupied == ahead_carriage_node.line_occupied:
                    # Then the next step must be behind ahead_carriage_node
                    if not ahead_of(intersection, ahead_carriage_node.fractional_position):
                        candidate_positions.append(intersection)
                else:
                    # Not on the same lines, so relative fractional_positions don't matter
                    candidate_positions.append(intersection)

        if len(candidate_positions) == 1:
            # Only one place to move to
            self.fractional_position = candidate_positions[0]
        elif len(candidate_positions) == 0:
            if self.line_occupied == ahead_carriage_node.line_occupied:
                # On same track as node in front, but nowhere to go, so can't move
                return 1
            else:
                # Nowhere to go on this track, but there may be somewhere on next track
                if train_velocity > 0:
                    # Put this node just beyond junction
                    self.fractional_position =  1.0001
                else:
                    # Put this node just beyond junction
                    self.fractional_position = -0.0001
                initial_line_occupied = self.line_occupied
                self.step(0) # Stepping will now switch this node onto the next line
                if self.line_occupied == initial_line_occupied:
                    raise SystemError(f"No valid position for following node at {self.get_location()}")
                else:
                    # Try following ahead_carriage_node, now this node is on the next line
                    self.follow(ahead_carriage_node, carriage_length, relative_train_velocity)
        else:
            raise SystemError(f"More than 1 position available to move following node at {self.get_location()}: {candidate_positions}")
        return 0
        
    def move_to(self, ahead_carriage_node):
        self.line_occupied = ahead_carriage_node.line_occupied
        self.fractional_position = ahead_carriage_node.fractional_position
        self.direction = ahead_carriage_node.direction

    def get_position(self):
        """ Interpolate position of node """
        position = self.line_occupied.interpolate_position(self.fractional_position)
        return position
    
    def get_location(self):
        """ Display position of node """
        return f"{self.get_position()} on line {self.line_occupied}"