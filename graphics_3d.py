import pygame
import math
from settings import BLOCK_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT

# Isometric projection constants
ISO_ANGLE = 30
SCALE_X = math.cos(math.radians(ISO_ANGLE))
SCALE_Y = math.sin(math.radians(ISO_ANGLE))

def to_iso(x, y, z=0):
    """Convert 3D coordinates to 2D isometric screen coordinates."""
    from settings import GRID_WIDTH, GRID_HEIGHT
    
    # Center the grid on screen
    # Calculate total width/height of the grid in iso view
    # This is a bit rough, but centering based on the center tile (GRID_WIDTH/2, GRID_HEIGHT/2) works best.
    
    center_x = GRID_WIDTH / 2
    center_y = GRID_HEIGHT / 2
    
    # Offset to center of screen
    screen_center_x = SCREEN_WIDTH / 2
    screen_center_y = SCREEN_HEIGHT / 2
    
    # Calculate iso pos of the center tile (at z=0)
    iso_center_x = (center_x - center_y) * BLOCK_SIZE * SCALE_X
    iso_center_y = (center_x + center_y) * BLOCK_SIZE * SCALE_Y
    
    # Calculate offset needed to bring iso_center to screen_center
    offset_x = screen_center_x - iso_center_x
    offset_y = screen_center_y - iso_center_y
    
    iso_x = (x - y) * BLOCK_SIZE * SCALE_X + offset_x
    iso_y = (x + y) * BLOCK_SIZE * SCALE_Y - (z * BLOCK_SIZE) + offset_y
    return int(iso_x), int(iso_y)

def draw_cube(surface, pos, color, size, z_height=1, glow=False):
    """Draw a 3D cube at grid position (x, y)."""
    x, y = pos
    
    # Vertices
    # Top face
    t1 = to_iso(x, y, z_height)
    t2 = to_iso(x + 1, y, z_height)
    t3 = to_iso(x + 1, y + 1, z_height)
    t4 = to_iso(x, y + 1, z_height)
    
    # Bottom face (only needed for sides)
    b2 = to_iso(x + 1, y, 0)
    b3 = to_iso(x + 1, y + 1, 0)
    b4 = to_iso(x, y + 1, 0)
    
    # Glow Effect
    if glow:
        glow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(3, 0, -1):
            alpha = int(30 / i)
            glow_color = (*color[:3], alpha)
            # Expand the top face for glow
            offset = i * 3
            gt1 = (t1[0], t1[1] - offset)
            gt2 = (t2[0] + offset, t2[1])
            gt3 = (t3[0], t3[1] + offset)
            gt4 = (t4[0] - offset, t4[1])
            pygame.draw.polygon(glow_surface, glow_color, [gt1, gt2, gt3, gt4])
        surface.blit(glow_surface, (0, 0))
    
    # Colors (Shading)
    c_top = color
    c_right = (max(0, color[0] - 50), max(0, color[1] - 50), max(0, color[2] - 50))
    c_left = (max(0, color[0] - 30), max(0, color[1] - 30), max(0, color[2] - 30))
    
    # Draw faces
    # Right Face
    pygame.draw.polygon(surface, c_right, [t2, t3, b3, b2])
    
    # Left Face
    pygame.draw.polygon(surface, c_left, [t4, t3, b3, b4])
    
    # Top Face
    pygame.draw.polygon(surface, c_top, [t1, t2, t3, t4])

def get_grid_renderables(color):
    """Return a list of renderables for the grid."""
    from settings import GRID_WIDTH, GRID_HEIGHT
    
    renderables = []
    
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            # Checkerboard pattern
            if (x + y) % 2 == 0:
                c = color
            else:
                c = (max(0, color[0] - 20), max(0, color[1] - 20), max(0, color[2] - 20))
            
            depth = x + y - 1 # Grid is below everything
            
            def draw_func(surface, gx=x, gy=y, col=c):
                draw_cube(surface, (gx, gy), col, BLOCK_SIZE, z_height=0.2)
                
            renderables.append((depth, draw_func))
            
    return renderables

def get_wall_renderables(color):
    """Return renderables for the arena walls."""
    from settings import GRID_WIDTH, GRID_HEIGHT
    
    renderables = []
    wall_height = 1.5
    
    # Draw walls around the perimeter
    for x in range(-1, GRID_WIDTH + 1):
        for y in range(-1, GRID_HEIGHT + 1):
            if x == -1 or x == GRID_WIDTH or y == -1 or y == GRID_HEIGHT:
                depth = x + y
                
                def draw_func(surface, gx=x, gy=y):
                    # Darker color for walls based on theme color passed in
                    wall_col = (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40))
                    draw_cube(surface, (gx, gy), wall_col, BLOCK_SIZE, z_height=wall_height)
                
                renderables.append((depth, draw_func))
                
    return renderables
