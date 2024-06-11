import json
import sys

filename = sys.argv[1]

layout_dict = {}

with open(filename,"r") as file:
    layout_dict = json.load(file)
    for junction_name in sys.argv[2:]:
        junction = layout_dict["junctions"][junction_name]
        startline, mainline = junction["startline"], junction["mainline"]
        layout_dict["junctions"][junction_name]["startline"] = mainline
        layout_dict["junctions"][junction_name]["mainline"] = startline

with open(filename[:-5]+".fixed.json","w") as file:
    json.dump(layout_dict, file, sort_keys=False, indent=4)
