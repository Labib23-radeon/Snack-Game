"""
Snake 3D - Third Person Perspective Mode
Using PyOpenGL for proper 3D rendering
"""
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import random
import math

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, BLOCK_SIZE, GRID_WIDTH, GRID_HEIGHT
from renderer_3d import Camera, init_opengl, draw_cube, draw_ground, draw_walls

class Snake3D:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.length = 1
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)  # Start moving right
        self.score = 0
    
    def get_head_position(self):
        return self.positions[0]
    
    def turn(self, direction):
        # Prevent 180 degree turns
        if self.length > 1 and (direction[0] * -1, direction[1] * -1) == self.direction:
            return
        self.direction = direction
    
    def move(self):
        head = self.get_head_position()
        x, y = self.direction
        new_x = (head[0] + x) % GRID_WIDTH
        new_y = (head[1] + y) % GRID_HEIGHT
        new_head = (new_x, new_y)
        
        # Check collision with self
        if len(self.positions) > 2 and new_head in self.positions[2:]:
            return False
        
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()
        
        return True

class Food3D:
    def __init__(self):
        self.position = (0, 0)
        self.randomize()
    
    def randomize(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), 
                         random.randint(0, GRID_HEIGHT - 1))

def draw_text_2d(screen, text, x, y, color=(255, 255, 255)):
    """Draw 2D text overlay."""
    font = pygame.font.SysFont("monospace", 20, bold=True)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def main():
    pygame.init()
    pygame.mixer.init()
    
    # Load sounds
    try:
        eat_sound = pygame.mixer.Sound("assets/eat.wav")
        game_over_sound = pygame.mixer.Sound("assets/game_over.wav")
    except:
        class MockSound:
            def play(self): pass
        eat_sound = game_over_sound = MockSound()
    
    # Create OpenGL window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("🐍 Snake 3D - TPP Mode")
    
    # Initialize OpenGL
    init_opengl(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Create game objects
    snake = Snake3D()
    food = Food3D()
    camera = Camera()
    
    # Game settings
    clock = pygame.time.Clock()
    game_speed = 8  # Moves per second
    move_timer = 0
    
    # Theme colors
    SNAKE_COLOR = (255, 100, 50)
    FOOD_COLOR = (255, 50, 50)
    GROUND_COLOR = (100, 180, 100)
    WALL_COLOR = (80, 60, 40)
    
    running = True
    paused = False
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    paused = not paused
                if not paused:
                    if event.key == K_UP or event.key == K_w:
                        snake.turn((0, -1))
                    elif event.key == K_DOWN or event.key == K_s:
                        snake.turn((0, 1))
                    elif event.key == K_LEFT or event.key == K_a:
                        snake.turn((-1, 0))
                    elif event.key == K_RIGHT or event.key == K_d:
                        snake.turn((1, 0))
                else:
                    if event.key == K_r:
                        paused = False
                    elif event.key == K_q:
                        running = False
        
        if not paused:
            # Game logic
            move_timer += dt
            if move_timer >= 1.0 / game_speed:
                move_timer = 0
                
                if not snake.move():
                    # Game Over
                    game_over_sound.play()
                    # Reset game
                    snake.reset()
                    food.randomize()
                
                # Check food collision
                if snake.get_head_position() == food.position:
                    eat_sound.play()
                    snake.length += 1
                    snake.score += 1
                    food.randomize()
            
            # Update camera to follow snake
            head = snake.get_head_position()
            camera.update((head[0] * BLOCK_SIZE, head[1] * BLOCK_SIZE), snake.direction)
        
        # Clear screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Apply camera
        camera.apply()
        
        # Draw ground and walls
        draw_ground(GRID_WIDTH, GRID_HEIGHT, GROUND_COLOR)
        draw_walls(GRID_WIDTH, GRID_HEIGHT, WALL_COLOR)
        
        # Draw snake
        for i, pos in enumerate(snake.positions):
            x, y = pos
            # Head is taller
            height = 0.8 if i == 0 else 0.5
            # Gradient color
            fade = 1.0 - (i / max(len(snake.positions), 1)) * 0.4
            color = (int(SNAKE_COLOR[0] * fade), 
                     int(SNAKE_COLOR[1] * fade), 
                     int(SNAKE_COLOR[2] * fade))
            draw_cube(x + 0.5, y + 0.5, height / 2, 0.9, color)
        
        # Draw food (floating and bobbing)
        food_x, food_y = food.position
        bob = math.sin(pygame.time.get_ticks() / 200) * 0.1 + 0.6
        draw_cube(food_x + 0.5, food_y + 0.5, bob, 0.7, FOOD_COLOR)
        
        pygame.display.flip()
        
        # Draw 2D HUD overlay
        # Note: For proper 2D overlay with OpenGL, we'd need to switch projection
        # For now, the 3D view is the main focus
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
