import pygame

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# 3D Theme Colors
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (124, 252, 0)
SNAKE_COLOR = (65, 105, 225) # Royal Blue like the image


# Game settings
BLOCK_SIZE = 20
# Difficulty FPS (Made easier)
FPS_EASY = 5
FPS_MEDIUM = 8
FPS_HARD = 12

# Grid settings (Larger grid for easier navigation)
GRID_WIDTH = 15
GRID_HEIGHT = 15

# Themes (Improved contrast)
THEMES = {
    "Classic": {
        "BG": (70, 130, 180), # Steel Blue
        "GRID": (144, 238, 144), # Light Green
        "WALL": (34, 100, 34), # Dark Green
        "SNAKE": (255, 69, 0) # Orange Red (more visible)
    },
    "Desert": {
        "BG": (255, 222, 173), # Navajo White
        "GRID": (244, 164, 96), # Sandy Brown
        "WALL": (139, 90, 43), # Saddle Brown
        "SNAKE": (0, 100, 0) # Dark Green (contrast)
    },
    "Night": {
        "BG": (15, 15, 45), # Very Dark Blue
        "GRID": (30, 30, 80), # Dark Indigo
        "WALL": (60, 0, 100), # Dark Purple
        "SNAKE": (0, 255, 100) # Bright Neon Green
    }
}
