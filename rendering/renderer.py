import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Define golden ratio (phi)
phi = (1 + np.sqrt(5)) / 2

# Define icosahedron vertices and faces
icosahedron_vertices = [
    (0, 1, phi), (0, -1, phi), (0, 1, -phi), (0, -1, -phi),
    (1, phi, 0), (-1, phi, 0), (1, -phi, 0), (-1, -phi, 0),
    (phi, 0, 1), (-phi, 0, 1), (phi, 0, -1), (-phi, 0, -1)
]

icosahedron_faces = [
    (0, 1, 4), (0, 4, 8), (0, 8, 9), (0, 9, 6), (0, 6, 1),
    (1, 6, 11), (1, 11, 7), (1, 7, 4), (2, 3, 5), (2, 5, 10),
    (2, 10, 8), (2, 8, 4), (2, 4, 7), (3, 7, 11), (3, 11, 9),
    (3, 9, 8), (3, 8, 10), (3, 10, 5), (2, 7, 3), (5, 10, 11)
]

def init_pygame_opengl():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def draw_icosahedron(scale_factor):
    glEnable(GL_BLEND)
    glEnable(GL_POLYGON_SMOOTH)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    glColor4f(1.0, 0.0, 0.0, 0.5)  # Red color with 50% transparency

    glBegin(GL_TRIANGLES)
    for face in icosahedron_faces:
        for vertex in face:
            glVertex3fv(icosahedron_vertices[vertex])
    glEnd()

def render_3d(scale_factor):
    init_pygame_opengl()

    # Main loop to render the scene
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glScalef(scale_factor, scale_factor, scale_factor)
        glRotatef(1, 0, 1, 0)  # Rotate for a dynamic view
        draw_icosahedron(scale_factor)
        glPopMatrix()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

    # Save the rendered image
    pygame.image.save(pygame.display.get_surface(), 'rendered_image.png')
    return 'rendered_image.png'
