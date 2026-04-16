import pygame
from settings import BLOCK_SIZE, GREEN, SCREEN_WIDTH, SCREEN_HEIGHT

class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        from settings import GRID_WIDTH, GRID_HEIGHT
        self.length = 1
        self.positions = [((GRID_WIDTH // 2) * BLOCK_SIZE, (GRID_HEIGHT // 2) * BLOCK_SIZE)]
        self.prev_positions = list(self.positions) # Copy for interpolation
        self.direction = (0, 0) # Initially stationary
        self.score = 0
        
        # Load images
        self.head_img = pygame.transform.scale(pygame.image.load("assets/snake_head.png"), (BLOCK_SIZE, BLOCK_SIZE))
        self.body_img = pygame.transform.scale(pygame.image.load("assets/snake_body.png"), (BLOCK_SIZE, BLOCK_SIZE))
        self.tail_img = pygame.transform.scale(pygame.image.load("assets/snake_tail.png"), (BLOCK_SIZE, BLOCK_SIZE))

    def get_head_position(self):
        return self.positions[0]

    def turn(self, point):
        if self.length > 1 and (point[0] * -1, point[1] * -1) == self.direction:
            return
        else:
            self.direction = point

    def move(self):
        from settings import GRID_WIDTH, GRID_HEIGHT
        
        # Store previous positions before moving
        self.prev_positions = list(self.positions)
        
        cur = self.get_head_position()
        x, y = self.direction
        new_x = cur[0] + (x * BLOCK_SIZE)
        new_y = cur[1] + (y * BLOCK_SIZE)
        
        # Infinite Mode: Wrap around grid
        max_x = GRID_WIDTH * BLOCK_SIZE
        max_y = GRID_HEIGHT * BLOCK_SIZE
        
        new_x = new_x % max_x
        new_y = new_y % max_y
            
        new = (new_x, new_y)

        if len(self.positions) > 2 and new in self.positions[2:]:
            return False
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()
            
            # Handle prev_positions length to match positions (for growing)
            if len(self.prev_positions) < len(self.positions):
                self.prev_positions.append(self.prev_positions[-1])
            elif len(self.prev_positions) > len(self.positions):
                self.prev_positions.pop()
                
            return True

    def get_renderables(self, alpha):
        from graphics_3d import draw_cube
        from settings import SNAKE_COLOR, BLOCK_SIZE, GRID_WIDTH, GRID_HEIGHT
        
        renderables = []
        
        for index, (curr_pos, prev_pos) in enumerate(zip(self.positions, self.prev_positions)):
            # Interpolate
            dx = curr_pos[0] - prev_pos[0]
            dy = curr_pos[1] - prev_pos[1]
            
            if abs(dx) > BLOCK_SIZE * 2 or abs(dy) > BLOCK_SIZE * 2:
                interp_x = curr_pos[0]
                interp_y = curr_pos[1]
            else:
                interp_x = prev_pos[0] + (curr_pos[0] - prev_pos[0]) * alpha
                interp_y = prev_pos[1] + (curr_pos[1] - prev_pos[1]) * alpha
            
            grid_x = interp_x / BLOCK_SIZE
            grid_y = interp_y / BLOCK_SIZE
            
            depth = grid_x + grid_y
            
            # Color gradient: head is bright, tail fades
            fade_factor = 1.0 - (index / max(len(self.positions), 1)) * 0.4
            segment_color = (
                int(SNAKE_COLOR[0] * fade_factor),
                int(SNAKE_COLOR[1] * fade_factor),
                int(SNAKE_COLOR[2] * fade_factor)
            )
            
            # Head is taller and glows more
            is_head = (index == 0)
            z_height = 1.2 if is_head else 1.0
            
            def draw_func(surface, gx=grid_x, gy=grid_y, color=segment_color, zh=z_height, glow=is_head):
                draw_cube(surface, (gx, gy), color, BLOCK_SIZE, z_height=zh, glow=glow)
            
            renderables.append((depth, draw_func))
            
        return renderables
