import pygame
import sys
import random
import math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, BLOCK_SIZE, GREEN, RED, SKY_BLUE, GRASS_GREEN
from snake import Snake
from food import Food
from graphics_3d import get_grid_renderables, get_wall_renderables

def draw_gradient_background(surface, color1, color2):
    """Draw a vertical gradient from color1 to color2."""
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))

def draw_text_centered(surface, text, size, color, y_offset=0):
    font = pygame.font.SysFont("monospace", size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (SCREEN_WIDTH/2 - label.get_width()/2, SCREEN_HEIGHT/2 + y_offset))

def start_screen(screen):
    from settings import THEMES, FPS_EASY, FPS_MEDIUM, FPS_HARD
    
    selected_theme_idx = 0
    theme_names = list(THEMES.keys())
    
    # Animation
    anim_offset = 0
    clock = pygame.time.Clock()
    
    while True:
        current_theme_name = theme_names[selected_theme_idx]
        theme = THEMES[current_theme_name]
        
        # Animated background
        bg_color1 = theme["BG"]
        bg_color2 = tuple(max(0, c - 50) for c in bg_color1)
        gradient_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        draw_gradient_background(gradient_surf, bg_color1, bg_color2)
        screen.blit(gradient_surf, (0, 0))
        
        # Bouncing title
        anim_offset = math.sin(pygame.time.get_ticks() / 300) * 5
        
        # Title with shadow
        title_font = pygame.font.SysFont("monospace", 60, bold=True)
        shadow_label = title_font.render("SNAKE 3D", 1, (0, 0, 0))
        screen.blit(shadow_label, (SCREEN_WIDTH/2 - shadow_label.get_width()/2 + 3, SCREEN_HEIGHT/2 - 117 + anim_offset))
        title_label = title_font.render("SNAKE 3D", 1, theme["SNAKE"])
        screen.blit(title_label, (SCREEN_WIDTH/2 - title_label.get_width()/2, SCREEN_HEIGHT/2 - 120 + anim_offset))
        
        draw_text_centered(screen, f"< Map: {current_theme_name} >", 28, WHITE, -40)
        draw_text_centered(screen, "Select Difficulty:", 22, (200, 200, 200), 20)
        draw_text_centered(screen, "[1] Easy (Relaxed)", 18, (100, 255, 100), 55)
        draw_text_centered(screen, "[2] Medium", 18, (255, 255, 100), 85)
        draw_text_centered(screen, "[3] Hard (Fast)", 18, (255, 100, 100), 115)
        draw_text_centered(screen, "Arrow Keys to Move | ESC = Pause", 14, (150, 150, 150), 170)
        
        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_theme_idx = (selected_theme_idx - 1) % len(theme_names)
                elif event.key == pygame.K_RIGHT:
                    selected_theme_idx = (selected_theme_idx + 1) % len(theme_names)
                elif event.key == pygame.K_1:
                    return FPS_EASY, theme
                elif event.key == pygame.K_2:
                    return FPS_MEDIUM, theme
                elif event.key == pygame.K_3:
                    return FPS_HARD, theme

def main():
    from settings import FPS_EASY, FPS_MEDIUM, FPS_HARD
    from powerup import PowerUp
    from particles import ParticleSystem
    
    pygame.init()
    pygame.mixer.init()
    
    # Load Sounds
    try:
        eat_sound = pygame.mixer.Sound("assets/eat.wav")
        powerup_sound = pygame.mixer.Sound("assets/powerup.wav")
        game_over_sound = pygame.mixer.Sound("assets/game_over.wav")
        click_sound = pygame.mixer.Sound("assets/click.wav")
    except:
        print("Warning: Sound files not found. Run sound_generator.py")
        class MockSound:
            def play(self): pass
        eat_sound = powerup_sound = game_over_sound = click_sound = MockSound()

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    pygame.display.set_caption("🐍 Snake 3D - Isometric Adventure")
    surface = pygame.Surface(screen.get_size())
    surface = surface.convert()
    
    # Load high score
    high_score = 0
    try:
        with open("highscore.txt", "r") as f:
            high_score = int(f.read().strip())
    except:
        pass
    
    # Level Selection
    current_fps, current_theme = start_screen(screen)
    
    snake = Snake()
    food = Food()
    powerups = []
    particles = ParticleSystem()
    
    myfont = pygame.font.SysFont("monospace", 16)
    
    # Colors from Theme
    BG_COLOR = current_theme["BG"]
    BG_COLOR2 = tuple(max(0, c - 40) for c in BG_COLOR)  # Darker version for gradient
    GRID_COLOR = current_theme["GRID"]
    WALL_COLOR = current_theme["WALL"]
    
    # Pre-render gradient background for performance
    gradient_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    draw_gradient_background(gradient_bg, BG_COLOR, BG_COLOR2)
    
    # Animation timer for floating effects
    anim_timer = 0
    
    # Game Loop Variables
    dt = 0
    accumulator = 0
    GAME_STEP = 1000 / current_fps # ms per game step
    RENDER_FPS = 60
    
    last_powerup_spawn = pygame.time.get_ticks()
    powerup_spawn_interval = 10000 # 10 seconds
    
    # Active effects
    score_multiplier = 1
    score_multiplier_end = 0
    
    paused = False
    
    # Screen shake effect
    screen_shake = 0
    
    # Combo system
    combo = 0
    last_eat_time = 0
    combo_timeout = 3000 # 3 seconds
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # Decouple Render FPS from Game Logic FPS
        dt = clock.tick(RENDER_FPS)
        accumulator += dt
        
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                    click_sound.play()
                
                if not paused:
                    if event.key == pygame.K_UP:
                        snake.turn((0, -1))
                    elif event.key == pygame.K_DOWN:
                        snake.turn((0, 1))
                    elif event.key == pygame.K_LEFT:
                        snake.turn((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        snake.turn((1, 0))
                else:
                    # Pause Menu Controls
                    if event.key == pygame.K_r: # Resume
                        paused = False
                        click_sound.play()
                    elif event.key == pygame.K_q: # Quit to Menu
                        return # Returns to __main__ which calls main() again
                    elif event.key == pygame.K_e: # Exit Game
                        running = False

        if paused:
            # Draw Pause Menu
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            draw_text_centered(screen, "PAUSED", 50, WHITE, -50)
            draw_text_centered(screen, "Press R to Resume", 20, WHITE, 10)
            draw_text_centered(screen, "Press Q to Quit to Menu", 20, WHITE, 40)
            draw_text_centered(screen, "Press E to Exit Desktop", 20, WHITE, 70)
            pygame.display.update()
            continue
        
        # Powerup Spawning
        if current_time - last_powerup_spawn > powerup_spawn_interval:
            if len(powerups) < 3:
                type_name = random.choice(["SLOW", "DOUBLE"])
                powerups.append(PowerUp(type_name))
            last_powerup_spawn = current_time
            
        # Check Powerup Expiry (on board)
        powerups = [p for p in powerups if current_time - p.spawn_time < p.duration]
        
        # Check Effect Expiry
        if current_time > score_multiplier_end:
            score_multiplier = 1
        
        # Update Particles
        particles.update()
        
        # Game Logic (Fixed Timestep)
        # Update GAME_STEP based on current_fps (difficulty)
        GAME_STEP = 1000 / current_fps
        
        while accumulator >= GAME_STEP:
            if not snake.move():
                # Game Over Logic
                game_over_sound.play()
                while True:
                    screen.fill(BLACK)
                    draw_text_centered(screen, "GAME OVER", 50, RED, -50)
                    draw_text_centered(screen, f"Score: {snake.score}", 30, WHITE, 10)
                    draw_text_centered(screen, "Press R to Restart or Q to Quit", 20, WHITE, 60)
                    pygame.display.update()
                    
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_q:
                                pygame.quit()
                                sys.exit()
                            if event.key == pygame.K_r:
                                snake.reset()
                                food.randomize_position()
                                break
                    else:
                        continue
                    break
            
            # Check Food Collision (grid coords)
            head_x, head_y = snake.get_head_position()
            food_x, food_y = food.position
            
            # Both are in pixel coords, check if on same grid cell
            head_grid = (head_x // BLOCK_SIZE, head_y // BLOCK_SIZE)
            food_grid = (food_x // BLOCK_SIZE, food_y // BLOCK_SIZE)
            
            if head_grid == food_grid:
                eat_sound.play()
                
                # Combo logic
                if current_time - last_eat_time < combo_timeout:
                    combo += 1
                else:
                    combo = 1
                last_eat_time = current_time
                
                # Score with combo bonus
                base_score = 1 * score_multiplier
                combo_bonus = min(combo - 1, 5) # Max +5 from combo
                snake.length += 1
                snake.score += base_score + combo_bonus
                
                # Screen shake on combo
                if combo > 1:
                    screen_shake = 5 + combo
                
                # Spawn particles
                from graphics_3d import to_iso
                food_grid_x = int(food.position[0] // BLOCK_SIZE)
                food_grid_y = int(food.position[1] // BLOCK_SIZE)
                iso_x, iso_y = to_iso(food_grid_x, food_grid_y, z=1)
                # More particles for combo
                particles.spawn(iso_x, iso_y, (255, 200, 50), count=10 + combo * 3)
                food.randomize_position()
                
            # Check Powerup Collision (grid coords)
            head_grid = (head_x // BLOCK_SIZE, head_y // BLOCK_SIZE)
            for p in powerups[:]:
                p_grid = (p.position[0] // BLOCK_SIZE, p.position[1] // BLOCK_SIZE)
                if head_grid == p_grid:
                    powerup_sound.play()
                    screen_shake = 8
                    # Spawn particles
                    from graphics_3d import to_iso
                    p_grid_x = int(p.position[0] // BLOCK_SIZE)
                    p_grid_y = int(p.position[1] // BLOCK_SIZE)
                    iso_x, iso_y = to_iso(p_grid_x, p_grid_y, z=1)
                    particles.spawn(iso_x, iso_y, p.color, count=25)
                    powerups.remove(p)
                    if p.type == "DOUBLE":
                        score_multiplier = 2
                        score_multiplier_end = current_time + 5000
                    elif p.type == "SLOW":
                        snake.score += 5
            
            accumulator -= GAME_STEP
            
        # Interpolation Alpha
        alpha = accumulator / GAME_STEP
        
        # Update animation timer
        anim_timer += dt / 1000.0
            
        # Drawing - Use gradient background
        surface.blit(gradient_bg, (0, 0))
        
        # Collect Renderables
        render_list = []
        
        # Grid
        render_list.extend(get_grid_renderables(GRID_COLOR))
        
        # Walls
        render_list.extend(get_wall_renderables(WALL_COLOR))
        
        # Snake
        render_list.extend(snake.get_renderables(alpha))
        
        # Food (with animation)
        render_list.extend(food.get_renderables(anim_timer))
        
        # Powerups
        for p in powerups:
            render_list.extend(p.get_renderables())
        
        # Sort by depth (Painter's Algorithm)
        render_list.sort(key=lambda x: x[0])
        
        # Draw
        for depth, draw_func in render_list:
            draw_func(surface)
        
        # Apply screen shake
        shake_offset_x = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
        shake_offset_y = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
        screen_shake = max(0, screen_shake - 1)
        
        screen.blit(surface, (shake_offset_x, shake_offset_y))
        
        # Draw particles on top
        particles.draw(screen)
        
        # HUD Background
        hud_surf = pygame.Surface((220, 95), pygame.SRCALPHA)
        hud_surf.fill((0, 0, 0, 150))
        screen.blit(hud_surf, (0, 0))
        
        text = myfont.render("Score: {0}".format(snake.score), 1, WHITE)
        screen.blit(text, (5, 10))
        
        # High score
        hs_text = myfont.render(f"Best: {high_score}", 1, (180, 180, 180))
        screen.blit(hs_text, (120, 10))
        
        # Combo display
        if combo > 1 and current_time - last_eat_time < combo_timeout:
            combo_color = (255, min(255, 100 + combo * 30), 0)
            combo_text = myfont.render(f"COMBO x{combo}!", 1, combo_color)
            screen.blit(combo_text, (5, 30))
        elif score_multiplier > 1:
            mult_text = myfont.render("2X SCORE!", 1, (255, 215, 0))
            screen.blit(mult_text, (5, 30))
        else:
            hint_text = myfont.render("ESC = Pause", 1, (150, 150, 150))
            screen.blit(hint_text, (5, 30))
        
        # Length display
        len_text = myfont.render(f"Length: {snake.length}", 1, (200, 200, 200))
        screen.blit(len_text, (5, 50))
        
        # FPS display (debug)
        fps_text = myfont.render(f"FPS: {int(clock.get_fps())}", 1, (100, 100, 100))
        screen.blit(fps_text, (5, 70))
            
        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    while True:
        try:
            main()
        except SystemExit:
            break
        except Exception as e:
            print(f"Error: {e}")
            break
