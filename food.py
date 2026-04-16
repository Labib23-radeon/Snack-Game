import pygame
import random
from settings import BLOCK_SIZE, RED, SCREEN_WIDTH, SCREEN_HEIGHT

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.images = [
            pygame.transform.scale(pygame.image.load("assets/apple.png"), (BLOCK_SIZE, BLOCK_SIZE)),
            pygame.transform.scale(pygame.image.load("assets/banana.png"), (BLOCK_SIZE, BLOCK_SIZE)),
            pygame.transform.scale(pygame.image.load("assets/cherry.png"), (BLOCK_SIZE, BLOCK_SIZE)),
            pygame.transform.scale(pygame.image.load("assets/strawberry.png"), (BLOCK_SIZE, BLOCK_SIZE))
        ]
        self.image = self.images[0]
        self.randomize_position()

    def randomize_position(self):
        from settings import GRID_WIDTH, GRID_HEIGHT
        self.position = (random.randint(0, GRID_WIDTH - 1) * BLOCK_SIZE, 
                         random.randint(0, GRID_HEIGHT - 1) * BLOCK_SIZE)
        self.image = random.choice(self.images)

    def get_renderables(self, anim_timer=0):
        from graphics_3d import to_iso
        import math
        
        grid_x = int(self.position[0] // BLOCK_SIZE)
        grid_y = int(self.position[1] // BLOCK_SIZE)
        
        depth = grid_x + grid_y
        
        # Floating animation
        float_offset = math.sin(anim_timer * 3) * 4
        
        def draw_func(surface):
            # Project to 2D
            iso_x, iso_y = to_iso(grid_x, grid_y, z=1)
            
            # Apply floating offset
            iso_y += float_offset
            
            # Draw Shadow (at z=0.1) - shadow stays on ground
            shadow_iso_x, shadow_iso_y = to_iso(grid_x, grid_y, z=0.1)
            shadow_rect = pygame.Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE/2)
            shadow_rect.center = (shadow_iso_x, shadow_iso_y)
            # Smaller shadow when food is higher
            shadow_scale = 1.0 - abs(float_offset) / 20
            shadow_rect.width = int(BLOCK_SIZE * shadow_scale)
            shadow_rect.height = int(BLOCK_SIZE/2 * shadow_scale)
            shadow_rect.center = (shadow_iso_x, shadow_iso_y)
            pygame.draw.ellipse(surface, (0, 0, 0, 100), shadow_rect)
            
            # Draw glow behind food
            glow_surf = pygame.Surface((BLOCK_SIZE * 2, BLOCK_SIZE * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 255, 200, 50), (BLOCK_SIZE, BLOCK_SIZE), BLOCK_SIZE)
            surface.blit(glow_surf, (iso_x - BLOCK_SIZE, iso_y - BLOCK_SIZE - BLOCK_SIZE/2))
            
            # Draw image centered at iso coordinates
            img_rect = self.image.get_rect(center=(iso_x, iso_y - BLOCK_SIZE/2))
            surface.blit(self.image, img_rect)
            
        return [(depth, draw_func)]
