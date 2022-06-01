import tkinter as tk
import math

from train import Train
from NetworkConstructor import Construct_Network

lines, junctions = Construct_Network("unity/Assets/Resources/TrackLayouts/EastfieldDepot.json")

window = tk.Tk()
canvas = tk.Canvas(window, width=900, height=800)

def do_zoom(event):
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    factor = 1.001 ** event.delta
    canvas.scale(ALL, x, y, factor, factor)
canvas.bind("<MouseWheel>", do_zoom)
canvas.bind('<ButtonPress-1>', lambda event: canvas.scan_mark(event.x, event.y))
canvas.bind("<B1-Motion>", lambda event: canvas.scan_dragto(event.x, event.y, gain=1))

canvas.grid()

#scale = 40
scale = 10
offset = 20
dot_radius = 8

import random

# Draw lines
for name, line in lines.items():
    for i in range(len(line.nodes)-1):
        start = line.nodes[i]
        end = line.nodes[i+1]
        x1, y1 = start.x*scale, start.y*scale
        x2, y2 = end.x*scale, end.y*scale
        canvas.create_line(x1+offset,y1+offset,x2+offset,y2+offset)
        if i == 0 or i == len(line.nodes)-2:
            pass
            canvas.create_text((x1+offset+x2+offset)/2, (y1+offset+y2+offset+random.randint(0,20))/2-4, text=name[4:], fill="red", font=('Helvetica 8'))
selected_train = None

def switch_point_callback(event):
    junction_oval = event.widget.find_withtag('current')[0]
    junction = None
    for j in junctions.values():
        if j.oval == junction_oval:
            junction = j
            break
    print("Click from junction ",junction)
    if junction.switch():
        colour = canvas.itemcget(junction_oval, "fill")
        newcolour = "blue"
        if colour == "blue":
            newcolour = "purple"
        canvas.itemconfig(junction_oval, fill=newcolour)
    else:
        pass
        print("Can't switch! Occupied.")

def select_train_callback(event):
    global selected_train
    elem = event.widget.find_withtag('current')[0]
    clicked_train = None
    for train in trains:
        for carriage in train.carriages:
            if carriage.line == elem:
                clicked_train = train
                break
    if clicked_train == selected_train:
        # Deselect
        selected_train = None
        print("Deselected train")
    else:
        selected_train = clicked_train
        print("Selected train ", selected_train)

# Draw junctions
for junction in junctions.values():
    pos = junction.position
    x1, y1 = pos.x*scale, pos.y*scale
    junction.oval = canvas.create_oval(x1+offset-dot_radius,y1+offset-dot_radius,x1+offset+dot_radius,y1+offset+dot_radius,fill="blue")
    canvas.tag_bind(junction.oval, "<Button-1>", switch_point_callback)

for name, junction in junctions.items():
    pos = junction.position
    x1, y1 = pos.x*scale, pos.y*scale
    canvas.create_text(x1+offset, y1+offset+20, text=name[1:], fill="#f50", font=('Helvetica 12 bold'))

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

        colour = "grey"
        if train == selected_train:
            colour = "green"
        carriage.line = canvas.create_line(x1+offset,y1+offset,x2+offset,y2+offset, fill=colour,width=10)
        canvas.tag_bind(carriage.line, "<Button-1>", select_train_callback)


## Simulation ##
trains = []
trains.append(Train.from_carriage_data(line=lines["line5"], fractional_position=0.1, carriage_data=[2,2,2,2,2,2,2,2]))
trains.append(Train.from_carriage_data(line=lines["line11"], fractional_position=0.1, carriage_data=[2,2,2,2,2,2]))
trains.append(Train.from_carriage_data(line=lines["line16"], fractional_position=0.1, carriage_data=[2,2,2,2,2,2,2,2]))
#trains.append(Train.from_carriage_data(line=lines["Mainline-A"], fractional_position=0.1, carriage_data=[1,2,1]))
#trains.append(Train.from_carriage_data(line=lines["Siding-3A"], fractional_position=0.2, carriage_data=[1,1,1]))

# Velocity steps must be shorter than the shortest line segment
# Also, there must be no bends of more that 90 degrees within the length of the longest carriage (or carriage following will have unexpected behaviour)
# Also, trains should not be spawned within the length of its longest carriage of a junction (train still continues, but there is a graphics & position glitch while crossing the junction)

keys_down = {}
def keypress(event):
    keys_down[event.keycode] = True

def keyrelease(event):
    keys_down[event.keycode] = False

window.bind("<Key>", keypress)
window.bind("<KeyRelease>", keyrelease)

def simulate():
    v = 0
    if keys_down.get(37, False) or keys_down.get(113, False): # Left arrow pressed
        v -= 0.5
    if keys_down.get(39, False) or keys_down.get(114, False): # Right arrow pressed
        v += 0.5

    if selected_train:
        selected_train.velocity = v
        selected_train.step()

    for train in trains:
        drawtrain_tmpfunction(train)
    window.after(20, simulate)

simulate()

window.mainloop()
