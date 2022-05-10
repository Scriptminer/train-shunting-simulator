MAINLINE = True
BRANCHLINE = False

class Buffer:
    """ End of a line segment """
    def __init__(self, position, line=None, visible=False):
        self.position = position
        self.line = line # The line / points branch connected to this buffer
        self.visible = visible

    def __str__(self):
        return f"B{str(self.position)}"

class Standard_Points:
    direction = MAINLINE
    occupied = False
    
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
        if self.occupied == False:
            if direction:
                self.direction = direction
            else:
                self.direction = not self.direction
            return True
        else:
            return False
    
    def toggle_occupied(self):
        self.occupied = not self.occupied

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
            if self.direction == MAINLINE:
                return self.main_line
            else:
                return self.branch_line
        elif from_line == self.main_line:
            if self.direction == MAINLINE:
                return self.start_line
            else:
                return None # Train cannot go this way
        elif from_line == self.branch_line:
            if self.direction == MAINLINE:
                return None # Train cannot go this way
            else:
                return self.start_line
        else:
            raise ValueError(f"Cannot find next line at junction {str(self)}: line {str(from_line)} not a connection.")

    def __str__(self):
        return f"J{str(self.position)}"