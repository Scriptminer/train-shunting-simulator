import tkinter as tk

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

class Buffer:
    """ End of a line segment """
    def __init__(self, position, line=None, visible=False):
        self.position = position
        self.line = line # The line / points branch connected to this buffer
        self.visible = visible

    def __str__(self):
        return f"B{str(self.position)}"

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

MAINLINE = True
BRANCHLINE = False

class Standard_Points:
    direction = MAINLINE
    def __init__(self, points_position, start_line, main_line, branch_line):
        self.position = points_position

        self.start_line = start_line
        self.main_line = main_line
        self.branch_line = branch_line

        # Connect the lines to the junction
        self.connect_line(self.start_line)
        self.connect_line(self.main_line)
        self.connect_line(self.branch_line)

    def switch(self, direction=None):
        if direction:
            self.direction = direction
        else:
            self.direction = not self.direction

    def connect_line(self, line):
        if line.start == self.position: # If the line's path starts at this junction
            line.set_start_junction(self) # Set the line to start at this junction
        elif line.end == self.position: # If the line's path ends at this junction
            line.set_end_junction(self) # Set the line to end at this junction
        else:
            print(line.start,line.end,self.position)
            raise ValueError(f"Inconsistency making connections for junction {str(self)}! The line {str(line)} doesn't start or end here.")

    def next(self, from_line):
        if from_line == self.start_line:
            print("FROM STARTLINE!")
            if self.direction == MAINLINE:
                return self.main_line
            else:
                return self.branch_line
        elif from_line == self.main_line:
            print("FROM MAINLINE!")
            if self.direction == MAINLINE:
                return self.start_line
            else:
                return None # Train cannot go this way
        elif from_line == self.branch_line:
            print("FROM BRANCHLINE!")
            if self.direction == MAINLINE:
                return None # Train cannot go this way
            else:
                return self.start_line
        else:
            raise ValueError(f"Cannot find next line at junction {str(self)}: line {str(from_line)} not a connection.")

    def __str__(self):
        return f"J{str(self.position)}"

class CarriageNode():
    def __init__(self, line_occupied, fractional_position=0):
        self.line_occupied = line_occupied
        self.fractional_position = fractional_position
        self.direction = 1 # 1 if the line segment is start - finish ()

    def step(self, velocity):
        """ Move forward a fixed distance. Returns True on any movement. """
        #print(f"I'm on line {self.line_occupied}, DIR: {self.direction}")
        velocity *= self.direction # The velocity in the direction in which the train is treating this segment of track
        line_length = self.line_occupied.length
        fractional_change = velocity / line_length
        old_fractional_position = self.fractional_position
        new_fractional_position = self.fractional_position + fractional_change
        # Switch track even if directly on junction (not past it)
        if new_fractional_position < 0:
            print(f"Hit start junction {str(self.line_occupied.start_junction)}")
            self.fractional_position = 0 # Move node to end of track in case train terminates here
            junction = self.line_occupied.start_junction
            overshoot = 0 - new_fractional_position
        elif new_fractional_position > 1:
            print(f"Hit end junction {str(self.line_occupied.end_junction)}")
            self.fractional_position = 1
            junction = self.line_occupied.end_junction
            overshoot = new_fractional_position - 1
        else:
            self.fractional_position = new_fractional_position
            return True

        # Switch onto new track:
        if type(junction) != Standard_Points:
            return False # Train terminates

        nextline = junction.next(self.line_occupied)
        if nextline == None: # Train can't go this way!
            if self.fractional_position == old_fractional_position:
                return False
            else:
                return True

        overshoot = overshoot * line_length # Gives overshoot as an absolute distance
        fractional_overshoot = overshoot / nextline.length # Overshoot as a fraction of the new line

        print(f"Nextline is {nextline}")
        nextline_starts_here = (nextline.start_junction == junction)
        thisline_starts_here = (self.line_occupied.start_junction == junction)

        if nextline_starts_here:
            self.fractional_position = 0 + fractional_overshoot
        else:
            self.fractional_position = 1 - fractional_overshoot

        # If tracks are either nose-nose or tail-tail flip direction, otherwise do nothing:
        if (nextline_starts_here and thisline_starts_here) or ((not nextline_starts_here) and (not thisline_starts_here)):
            self.direction *= -1


        self.line_occupied = nextline
        return True

    def follow(self, ahead_carriage_node, carriage_length, train_velocity):
        train_velocity *= self.direction # The velocity in the direction in which the train is treating this segment of track
        # Find all points which are a carriage length away from
        # ahead_carriage_node on this line
        intersections = self.line_occupied.intersects_circle(ahead_carriage_node.get_position(), carriage_length)

        if train_velocity == 0:
            return

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
                # print("Can't Move!")
                pass
            else:
                # Nowhere to go on this track, but there may be somewhere on next track
                if train_velocity > 0:
                    # Put this node just beyond junction
                    self.fractional_position =  1.0001
                else:
                    print("TV:",train_velocity)
                    # Put this node just beyond junction
                    self.fractional_position = -0.0001
                self.step(0) # Stepping will now switch this node onto the next line
                train_velocity *= self.direction # Undo effects of previous multiplication
                # Try following ahead_carriage_node, now this node is on the next line
                self.follow(ahead_carriage_node, carriage_length, train_velocity)
        else:
            print("TOO MANY OPTIONS!")

    def move_to(self, ahead_carriage_node):
        self.line_occupied = ahead_carriage_node.line_occupied
        self.fractional_position = ahead_carriage_node.fractional_position
        self.direction = ahead_carriage_node.direction

    def get_position(self):
        """ Interpolate position of node """
        position = self.line_occupied.interpolate_position(self.fractional_position)
        return position

class Train:
    def __init__(self, carriages):
        self.carriages = carriages
        self.velocity = 0
        #self.a_temporary_second_node = a_temporary_second_node

    @classmethod
    def from_carriage_data(cls, line, fractional_position, carriage_data):
        carriages = []
        for carriage in carriage_data:
            carriages.append( Carriage(line, fractional_position, length=carriage) )
        return cls(carriages)


    def step(self):
        if self.velocity > 0:
            carriage = self.carriages[0]
            # Move lead node
            if not carriage.front.step(self.velocity):
                return False # If moving lead node fails, return
            carriage.back.follow(carriage.front, carriage.length, self.velocity)

            previous_carriage = carriage
            for carriage in self.carriages[1:]:
                carriage.front.move_to(previous_carriage.back)
                carriage.back.follow(carriage.front, carriage.length, self.velocity)
                previous_carriage = carriage
        else:
            carriage = self.carriages[-1]
            if not carriage.back.step(self.velocity): # Move lead node
                return False # If moving lead node fails, return
            carriage.front.follow(carriage.back, carriage.length, self.velocity)

            previous_carriage = carriage
            for carriage in self.carriages[-2::-1]:
                carriage.back.move_to(previous_carriage.front)
                carriage.front.follow(carriage.back, carriage.length, self.velocity)
                previous_carriage = carriage
        return True
        # success = self.front.step(self.velocity) # May not be the way it is done in the end
        # self.a_temporary_second_node.follow(self.front,1,self.velocity)
        # return success

class Carriage:
    def __init__(self, line_occupied, fractional_position, length, type="default"):
        self.length = length
        self.type = type
        self.front = CarriageNode(line_occupied, fractional_position)
        self.back =  CarriageNode(line_occupied, fractional_position)

#########################################################

import json

junctions = {}
lines = {}

with open("sample_line.json") as file:
    data = json.load(file)
    lines_data = data["lines"]
    junctions_data = data["junctions"]

    for line_name, line in lines_data.items():
        nodes = [Node(node[0],node[1]) for node in line["nodes"]]
        lines[line_name] = Line(nodes=nodes)

    for junction_name, junction in junctions_data.items():
        if junction["type"] == "StandardPoints":
            position = Node(junction["position"][0], junction["position"][1])
            start_line  = lines[junction["startline"]]
            main_line   = lines[junction["mainline"]]
            branch_line = lines[junction["branchline"]]
            junctions[junction_name] = Standard_Points(position, start_line=start_line, main_line=main_line, branch_line=branch_line)
        elif junction["type"] == "Idontknowthisone":
            pass
        else:
            raise ValueError(f"Unrecognised junction type {junction['type']} for junction {junction_name}.")


# junctions = [[]]*4
# lines = [[]]*8
#
# # Main Line
# lines[0] = Line(nodes=[Node(0,0),Node(1,0.5),Node(2,1),Node(3,0.5),Node(4,0),Node(5,0)])
# lines[1] = Line(nodes=[Node(5,0),Node(15,0)])
# lines[5] = Line(nodes=[Node(15,0),Node(20,0)])
# lines[6] = Line(nodes=[Node(7,2),Node(13,2),Node(15,0)])
# # Branch Line
# lines[2] = Line(nodes=[Node(5,0),Node(7,2)])
# lines[7] = Line(nodes=[Node(7,2),Node(9,4)])
# lines[3] = Line(nodes=[Node(20,4),Node(9,4)])
# lines[4] = Line(nodes=[Node(9,4),Node(11,6),Node(20,6)])
#
# # Junctions
# junctions[0] = Standard_Points(Node(5,0), start_line=lines[0], main_line=lines[1], branch_line=lines[2]) # First set of points
# junctions[1] = Standard_Points(Node(9,4), start_line=lines[7], main_line=lines[4], branch_line=lines[3]) # Second set of points on branch line
# junctions[2] = Standard_Points(Node(7,2), start_line=lines[2], main_line=lines[7], branch_line=lines[6])
# junctions[3] = Standard_Points(Node(15,0), start_line=lines[5], main_line=lines[1], branch_line=lines[6])

window = tk.Tk()
canvas = tk.Canvas(window, width=900, height=800)
canvas.grid()

scale = 40
offset = 20
dot_radius = 5

# Draw lines
for line in lines.values():
    for i in range(len(line.nodes)-1):
        start = line.nodes[i]
        end = line.nodes[i+1]
        x1, y1 = start.x*scale, start.y*scale
        x2, y2 = end.x*scale, end.y*scale
        canvas.create_line(x1+offset,y1+offset,x2+offset,y2+offset)


def switch_point_callback(event):
    junction_oval = event.widget.find_withtag('current')[0]
    junction = None
    for j in junctions.values():
        if j.oval == junction_oval:
            junction = j
            break
    print("Click from junction ",junction)
    colour = canvas.itemcget(junction_oval, "fill")
    newcolour = "blue"
    if colour == "blue":
        newcolour = "purple"
    canvas.itemconfig(junction_oval, fill=newcolour)
    junction.switch()

# Draw junctions
for junction in junctions.values():
    pos = junction.position
    x1, y1 = pos.x*scale, pos.y*scale
    junction.oval = canvas.create_oval(x1+offset-dot_radius,y1+offset-dot_radius,x1+offset+dot_radius,y1+offset+dot_radius,fill="blue")
    canvas.tag_bind(junction.oval, "<Button-1>", switch_point_callback)

def drawtrain_tmpfunction(train):
    for carriage in train.carriages:
        if hasattr(carriage.front, "oval"):
            canvas.delete(carriage.front.oval)
        if hasattr(carriage.back, "oval"):
            canvas.delete(carriage.back.oval)
        if hasattr(carriage, "line"):
            canvas.delete(carriage.line)

        position = carriage.front.get_position()
        x1, y1 = position.x*scale, position.y*scale
        carriage.front.oval = canvas.create_oval(x1+offset-3,y1+offset-3,x1+offset+3,y1+offset+3,fill="green")

        position = carriage.back.get_position()
        x2, y2 = position.x*scale, position.y*scale
        carriage.back.oval = canvas.create_oval(x2+offset-3,y2+offset-3,x2+offset+3,y2+offset+3,fill="red")

        dist_between_nodes = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        if dist_between_nodes > 40.01 or dist_between_nodes < 39.99:
            #print(f"DISTANCE BETWEEN NODES: {dist_between_nodes}")
            pass

        carriage.line = canvas.create_line(x1+offset,y1+offset,x2+offset,y2+offset, fill="red")

## Simulation ##
maintrain = Train.from_carriage_data(line=lines["Mainline-A"], fractional_position=0.1, carriage_data=[1,2,1])
train2 = Train.from_carriage_data(line=lines["Siding-3A"], fractional_position=0.9, carriage_data=[1,1,1])
maintrain.velocity = 0.05 # Velocity steps must be shorter than the shortest line segment
# Also, there must be no bends of more that 90 degrees within the length of the longest carriage (or carriage following will have unexpected behaviour)
# Also, trains should not be spawned within the length of its longest carriage of a junction (train still continues, but there is a graphics & position glitch while crossing the junction)


keys_down = {}
def keypress(event):
    keys_down[event.keycode] = True

def keyrelease(event):
    keys_down[event.keycode] = False

window.bind("<Key>", keypress)
window.bind("<KeyRelease>", keyrelease)
drawtrain_tmpfunction(maintrain)
drawtrain_tmpfunction(train2)
def simulate():
    v = 0
    if keys_down.get(113, False): # Left arrow pressed
        v -= 0.1
    if keys_down.get(114, False): # Right arrow pressed
        v += 0.1
    maintrain.velocity = v
    train2.velocity = v
    maintrain.step()
    train2.step()
    drawtrain_tmpfunction(maintrain)
    drawtrain_tmpfunction(train2)
    window.after(50, simulate)

simulate()

window.mainloop()
