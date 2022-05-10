import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from NetworkConstructor import Construct_Network

import math

lines, junctions = Construct_Network("nofilenameyet.json")

dot_radius = 5

def draw_lines():
    glBegin(GL_LINES)
    for line in lines:
        for i in range(len(line.nodes)-1):
            start = line.nodes[i]
            end = line.nodes[i+1]
            x1, y1 = start.x, start.y
            x2, y2 = end.x, end.y
            #dx,dy = x2-x1, y2-y1
            glVertex3fv( (x1,y1,0) )
            glVertex3fv( (x2,y2,0) )
            
            #glVertex3fv( (x1+dx,y1+dy,0) )
            #glVertex3fv( (x2+dx,y2+dy,0) )
    glEnd()


def main():
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 100.0)

    glTranslatef(-10,10, -30)
    glRotatef(180, 180, 0, 0)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        #Cube()
        draw_lines()
        pygame.display.flip()
        pygame.time.wait(10)


main()