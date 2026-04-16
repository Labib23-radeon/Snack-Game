import pygame
import random
from settings import BLOCK_SIZE, GRID_WIDTH, GRID_HEIGHT

class PowerUp:
    def __init__(self, type_name):
        self.type = type_name # "SLOW" or "DOUBLE"
        self.position = (0, 0)
        self.active = True
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 5000 # 5 seconds on board
        self.randomize_position()
        
        # Simple colors for now, could use images later
        if self.type == "SLOW":
            self.color = (0, 0, 255) # Blue
        else:
            self.color = (255, 215, 0) # Gold

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1) * BLOCK_SIZE, 
                         random.randint(0, GRID_HEIGHT - 1) * BLOCK_SIZE)

    def get_renderables(self):
        from graphics_3d import to_iso, draw_cube
        import math
        
        grid_x = int(self.position[0] // BLOCK_SIZE)
        grid_y = int(self.position[1] // BLOCK_SIZE)
        
        depth = grid_x + grid_y
        
        # Pulsing effect
        pulse = 1.0 + math.sin(pygame.time.get_ticks() / 150) * 0.15
        z = 1.3 + math.sin(pygame.time.get_ticks() / 200) * 0.2
        
        def draw_func(surface):
            pulsed_color = tuple(min(255, int(c * pulse)) for c in self.color)
            draw_cube(surface, (grid_x, grid_y), pulsed_color, BLOCK_SIZE, z_height=z, glow=True)
            
        return [(depth, draw_func)]
