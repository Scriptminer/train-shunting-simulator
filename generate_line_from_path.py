# example_inkscape_path = "111.28724,100.00364 6.95545,8.97478 2.01932,14.35964 v 10.9941 l -0.44874,15.4815 0.44874,14.13527 -1.79495,11.89158 -0.44874,5.60923"

import sys

inkscape_path = sys.argv[1]
print("Generating sequence from path: ", inkscape_path)
nodes = []

for coords in inkscape_path.split(" "):
    parts = coords.split(",")
    if len(parts) != 2:
        continue
    x, y = parts[0], parts[1]
    nodes.append([float(x),float(y)])

print("****** OUTPUT ******")
print(nodes)
