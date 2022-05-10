import json
from node import Node
from line import Line
from junctions import Standard_Points, Buffer


def Construct_Network(filename):
    lines = {}
    junctions = {}

    with open(filename) as file:
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

    return lines, junctions
