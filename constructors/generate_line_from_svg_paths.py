import sys
import svg.path
import xmltodict
import json

filename = sys.argv[1]

with open(filename) as f:
    file = xmltodict.parse(f.read())

lines = []
nodes_list = []

raw_paths = file["svg"]["g"]["path"]

for idx, raw_path in enumerate(raw_paths):
    path = svg.path.parse_path(raw_path["@d"])
    line = [[round(node.start.real,2), round(node.start.imag,2)] for node in path[1:]] + [[round(path[-1].end.real,2), round(path[-1].end.imag,2)]]
    nodes_list += line
    lines.append(line)

# Split lines on junctions
newlines = []
for line in lines:
    line_part = []
    for node in line:
        line_part.append(node)
        if nodes_list.count(node) > 1:
            if len(line_part) > 1:
                newlines.append(line_part)
            line_part = [node]
    if len(line_part) > 1:
        newlines.append(line_part)
lines = newlines

print("\n".join([f"{idx}:{str(line)}" for idx,line in enumerate(lines)]))

nodes = {} # Maps node tuples to arrays of all line numbers in which they occur
for idx, line in enumerate(lines):
    for node in line:
        if nodes.get(tuple(node)):
            nodes[tuple(node)].append(idx)
        else:
            nodes[tuple(node)] = [idx]

layout_dict = {"lines":{},"junctions":{}}
junctions = {key: value for key, value in nodes.items() if len(value) > 1} # Only points where multiple lines meet
print("Identified junctions:")
print(junctions)

for idx, kv in enumerate(junctions.items()):
    junction, connecting_lines = kv

    layout_dict["junctions"][f"J{idx}"] = {
      "type": "StandardPoints",
      "position": list(junction),
      "startline":  f"line{connecting_lines[0]}",
      "mainline":   f"line{connecting_lines[1]}",
      "branchline": f"line{connecting_lines[2]}"
    }

for idx, line in enumerate(lines):
    line_dict = {"nodes":line}
    layout_dict["lines"][f"line{idx}"] = line_dict

with open(f"{filename.split('.')[0]}.json", "w") as f:
    json.dump(layout_dict, f, sort_keys=False, indent=4)
