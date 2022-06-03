from carriage import Carriage

class Train:
    all_trains = []

    def __init__(self, carriages):
        Train.all_trains.append(self)
        self.carriages = carriages
        self.velocity = 0

        carriages[0].front.is_ends_node = True
        carriages[-1].back.is_ends_node = True

        # Fully expand train
        print(f"Expanding train {self}...")
        self.velocity = 0.1
        while True:
            # Loop while at least one following node can't move
            code = self.step()
            if code == 2:
                continue
            elif code == 0:
                break
            else: # Case 1 or 3
                raise SystemError("Cannot fully expand train!")
        self.velocity = 0

    @classmethod
    def from_carriage_data(cls, line, fractional_position, carriage_data):
        carriages = []
        for carriage in carriage_data:
            carriages.append( Carriage(line, fractional_position, length=carriage) )
        return cls(carriages)


    def step(self):
        # Error Codes: 0 - success, 1 - lead node cannot move, 2 - at least one following node cannot move, 3 - collision with other train, so can't move
        if self.velocity == 0:
            return 0

        def check_collisions(carriage_node):
            carriage_old_position = carriage_node.get_previous_state()
            carriage_position = carriage_node.get_state()
            if carriage_old_position["line_occupied"] != carriage_position["line_occupied"]:
                carriage_old_position["line_occupied"] = carriage_position["line_occupied"]
                carriage_old_position["fractional_position"] = -0.1 if carriage_position["direction"]*self.velocity > 0 else 1.1

            for train in Train.all_trains:
                if train == self:
                    continue
                # Check for collision with front of train
                if train.carriages[0].front.line_occupied == carriage_position["line_occupied"]:
                    #print(f"Train of length {len(self.carriages)} shares line: OldPos: {carriage_old_position['fractional_position']}, NewPos: {carriage_position['fractional_position']}, OtherTrain: {train.carriages[0].front.fractional_position}")
                    begins_before = carriage_old_position["fractional_position"] < train.carriages[0].front.fractional_position
                    ends_after    = carriage_position["fractional_position"] >= train.carriages[0].front.fractional_position
                    if (begins_before and ends_after) or ((not begins_before) and (not ends_after)):
                        return 1

                # Check for collision with rear of train
                if train.carriages[-1].back.line_occupied == carriage_position["line_occupied"]:
                    #print(f"Train of length {len(self.carriages)} shares line: OldPos: {carriage_old_position['fractional_position']}, NewPos: {carriage_position['fractional_position']}, OtherTrain: {train.carriages[0].front.fractional_position}")
                    begins_before = carriage_old_position["fractional_position"] < train.carriages[-1].back.fractional_position
                    ends_after    = carriage_position["fractional_position"] >= train.carriages[-1].back.fractional_position
                    if (begins_before and ends_after) or ((not begins_before) and (not ends_after)):
                        return 1
            return 0

        if self.velocity > 0:
            ordered_carriages = self.carriages[:]
        else:
            ordered_carriages = self.carriages[::-1]

        # Move lead node
        carriage = ordered_carriages[0]
        leader, follower = carriage.get_leader(self.velocity), carriage.get_follower(self.velocity)
        if leader.step(self.velocity, save=True) != 0:
            return 1 # If moving lead node fails, return

        if check_collisions(leader) != 0: # Collision has occurred
            print("REVERTING! Back on train of length",len(self.carriages))
            leader.undo_step()
            return 3

        # Move all remaining nodes of the train
        if follower.follow(leader, carriage.length, self.velocity) != 0:
            return 2 # If a following node fails, return

        previous_carriage_back = follower
        for carriage in ordered_carriages[1:]:
            leader, follower = carriage.get_leader(self.velocity), carriage.get_follower(self.velocity)
            leader.move_to(previous_carriage_back)
            if follower.follow(leader, carriage.length, self.velocity) != 0:
                return 2
            previous_carriage_back = follower

        return 0 # Success
        # success = self.front.step(self.velocity) # May not be the way it is done in the end
        # self.a_temporary_second_node.follow(self.front,1,self.velocity)
        # return success
