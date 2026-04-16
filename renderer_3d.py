"""
3D Renderer using PyOpenGL for Snake 3D TPP
"""
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

class Camera:
    def __init__(self):
        self.distance = 8.0  # Distance behind target
        self.height = 6.0    # Height above target
        self.target = [7.5, 7.5, 0]  # Look at center initially
        self.angle = 0       # Camera rotation angle
        
    def update(self, snake_head, snake_direction):
        """Update camera to follow snake from behind."""
        head_x = snake_head[0] / 20  # Convert from pixels to grid units
        head_y = snake_head[1] / 20
        
        self.target = [head_x, head_y, 0.5]
        
        # Calculate angle based on snake direction
        if snake_direction[0] == 1:  # Right
            self.angle = 90
        elif snake_direction[0] == -1:  # Left
            self.angle = 270
        elif snake_direction[1] == 1:  # Down
            self.angle = 180
        elif snake_direction[1] == -1:  # Up
            self.angle = 0
    
    def apply(self):
        """Apply camera transformation."""
        # Calculate camera position behind and above the target
        rad = math.radians(self.angle)
        cam_x = self.target[0] - math.sin(rad) * self.distance
        cam_y = self.target[1] - math.cos(rad) * self.distance
        cam_z = self.target[2] + self.height
        
        gluLookAt(
            cam_x, cam_y, cam_z,           # Camera position
            self.target[0], self.target[1], self.target[2],  # Look at
            0, 0, 1                         # Up vector
        )

def init_opengl(width, height):
    """Initialize OpenGL settings."""
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Set up perspective
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, width / height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    
    # Light position
    glLight(GL_LIGHT0, GL_POSITION, (10, 10, 20, 1))
    glLight(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.3, 1))
    glLight(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1))
    
    # Background color
    glClearColor(0.4, 0.6, 0.9, 1.0)

def draw_cube(x, y, z, size, color):
    """Draw a 3D cube at position (x, y, z)."""
    glPushMatrix()
    glTranslatef(x, y, z)
    
    r, g, b = color[0]/255, color[1]/255, color[2]/255
    glColor3f(r, g, b)
    
    half = size / 2
    
    # Front face
    glBegin(GL_QUADS)
    glNormal3f(0, 0, 1)
    glVertex3f(-half, -half, half)
    glVertex3f(half, -half, half)
    glVertex3f(half, half, half)
    glVertex3f(-half, half, half)
    glEnd()
    
    # Back face
    glBegin(GL_QUADS)
    glNormal3f(0, 0, -1)
    glVertex3f(-half, -half, -half)
    glVertex3f(-half, half, -half)
    glVertex3f(half, half, -half)
    glVertex3f(half, -half, -half)
    glEnd()
    
    # Top face
    glBegin(GL_QUADS)
    glNormal3f(0, 0, 1)
    glVertex3f(-half, -half, half)
    glVertex3f(-half, half, half)
    glVertex3f(-half, half, -half)
    glVertex3f(-half, -half, -half)
    glEnd()
    
    # Bottom face
    glBegin(GL_QUADS)
    glNormal3f(0, 0, -1)
    glVertex3f(half, -half, -half)
    glVertex3f(half, half, -half)
    glVertex3f(half, half, half)
    glVertex3f(half, -half, half)
    glEnd()
    
    # Right face
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-half, half, -half)
    glVertex3f(-half, half, half)
    glVertex3f(half, half, half)
    glVertex3f(half, half, -half)
    glEnd()
    
    # Left face
    glBegin(GL_QUADS)
    glNormal3f(0, -1, 0)
    glVertex3f(-half, -half, -half)
    glVertex3f(half, -half, -half)
    glVertex3f(half, -half, half)
    glVertex3f(-half, -half, half)
    glEnd()
    
    glPopMatrix()

def draw_ground(grid_width, grid_height, color):
    """Draw ground plane."""
    r, g, b = color[0]/255, color[1]/255, color[2]/255
    
    glBegin(GL_QUADS)
    glColor3f(r * 0.8, g * 0.8, b * 0.8)
    glNormal3f(0, 0, 1)
    glVertex3f(-1, -1, -0.1)
    glVertex3f(grid_width + 1, -1, -0.1)
    glVertex3f(grid_width + 1, grid_height + 1, -0.1)
    glVertex3f(-1, grid_height + 1, -0.1)
    glEnd()
    
    # Grid lines
    glDisable(GL_LIGHTING)
    glColor3f(r * 0.6, g * 0.6, b * 0.6)
    glBegin(GL_LINES)
    for i in range(grid_width + 1):
        glVertex3f(i, 0, 0)
        glVertex3f(i, grid_height, 0)
    for j in range(grid_height + 1):
        glVertex3f(0, j, 0)
        glVertex3f(grid_width, j, 0)
    glEnd()
    glEnable(GL_LIGHTING)

def draw_walls(grid_width, grid_height, color):
    """Draw walls around the arena."""
    wall_height = 0.5
    r, g, b = color[0]/255, color[1]/255, color[2]/255
    glColor3f(r, g, b)
    
    # Draw wall cubes
    for x in range(-1, grid_width + 1):
        draw_cube(x + 0.5, -0.5, wall_height/2, 1, color)
        draw_cube(x + 0.5, grid_height + 0.5, wall_height/2, 1, color)
    for y in range(grid_height):
        draw_cube(-0.5, y + 0.5, wall_height/2, 1, color)
        draw_cube(grid_width + 0.5, y + 0.5, wall_height/2, 1, color)
