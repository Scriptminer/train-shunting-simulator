import math

from node import Node
from junctions import Buffer

class Line:
    def __init__(self, nodes):
        self.nodes = nodes
        self.start = nodes[0]
        self.end   = nodes[-1]
        # Set placeholder values:
        self.start_junction = Buffer(position=self.start, line=self)
        self.end_junction   = Buffer(position=self.end  , line=self)

        self.calculate_length()

    def set_start_junction(self, junction):
        if type(self.start_junction) != Buffer:
            raise ValueError(f"Attempted to override start junction of the line {str(self)}")
        self.start_junction = junction
    def set_end_junction(self, junction):
        if type(self.end_junction) != Buffer:
            raise ValueError(f"Attempted to override end junction of the line {str(self)}.")
        self.end_junction = junction

    def calculate_length(self):
        length = 0
        segment_lengths = []
        for i in range(len(self.nodes)-1):
            node = self.nodes[i]
            next_node = self.nodes[i+1]
            segment_length = node.distance_to(next_node)
            length += segment_length
            segment_lengths.append(segment_length)
        self.segment_lengths = segment_lengths
        self.fractional_segment_lengths = [segment_length / length for segment_length in segment_lengths]
        self.length = length

    def interpolate_position(self,fractional_position):
        length_so_far = 0
        for i in range(len(self.nodes)-1):
            node = self.nodes[i]
            next_node = self.nodes[i+1]
            if length_so_far + self.fractional_segment_lengths[i] >= fractional_position:
                # Then position lies between node and the next node
                section_position = (fractional_position - length_so_far) / self.fractional_segment_lengths[i]
                x = node.x + (next_node.x - node.x)*section_position
                y = node.y + (next_node.y - node.y)*section_position
                return Node(x,y)
            length_so_far += self.fractional_segment_lengths[i]

    def intersects_circle(self, circle_centre, circle_radius):
        intersection_points = [] # Under normal circumstances will only contain 0, 1 or 2 elements

        length_so_far = 0
        for i in range(len(self.nodes) - 1):
            segment_length = self.fractional_segment_lengths[i]
            segment_start = self.nodes[i]
            segment_end   = self.nodes[i+1]
            # See https://www.desmos.com/calculator/4rex488t3d for method
            x1,y1 = segment_start.x, segment_start.y
            x2,y2 = segment_end.x, segment_end.y
            cx,cy = circle_centre.x, circle_centre.y
            r = circle_radius

            dx = x2 - x1 # The number such that x1 + dx = x2
            dy = y2 - y1 # The number such that y1 + dy = y2

            # Coefficients of the quadratic formula to find f,
            # the fractional position on the line segment (can be
            # outside 0-1) which intersects the circle of radius of
            # the carriage length, e.g., the solution to:
            # ((x1 + fdx) - cx)^2 + ((y1 + fdy) - cy)^2 = r^2
            A = dx**2 + dy**2
            B = 2*x1*dx - 2*dx*cx + 2*y1*dy - 2*dy*cy
            C = x1**2 - 2*cx*x1 + cx**2 + y1**2 - 2*cy*y1 + cy**2 - r**2

            # Implementation of quadratic formula:
            discriminant = B**2 - 4*A*C

            if discriminant >= 0:
                root_dicriminant = math.sqrt(discriminant)
                f_plus  = (-B + root_dicriminant) / (2*A)
                f_minus = (-B - root_dicriminant) / (2*A)
                # Add only those points which lie on a line segment
                if f_plus >= 0 and f_plus <= 1:
                    # Convert f position on segment to position on line
                    line_position = (f_plus*segment_length) + length_so_far
                    intersection_points.append(line_position)
                if f_minus >= 0 and f_minus <= 1:
                    # Convert f position on segment to position on line
                    line_position = (f_minus*segment_length) + length_so_far
                    intersection_points.append(line_position)
            length_so_far += segment_length

        # Remove any points which are (very close to) identical
        intersection_points.sort()
        for i in range(len(intersection_points)-1):
            prev_point, point = intersection_points[i], intersection_points[i+1]
            if abs(prev_point - point) < 0.000000001:
                intersection_points[i] = None # Mark prev_point for removal, it is almost identical to point
        intersection_points = [pt for pt in intersection_points if pt != None] # Remove points marked for removal
        return intersection_points

    def __str__(self):
        return f"{str(self.start)}->{str(self.end)}"
