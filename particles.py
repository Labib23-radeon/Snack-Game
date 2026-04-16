import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color, velocity=None):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 8)
        self.lifespan = 60  # frames
        self.age = 0
        
        if velocity:
            self.vx, self.vy = velocity
        else:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed - 2  # Slight upward bias
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Gravity
        self.age += 1
        self.size = max(1, self.size - 0.1)
        
    def is_alive(self):
        return self.age < self.lifespan
    
    def draw(self, surface):
        alpha = int(255 * (1 - self.age / self.lifespan))
        if alpha <= 0:
            return
            
        # Create a temp surface for alpha
        s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def spawn(self, x, y, color, count=10):
        import random
        for _ in range(count):
            # Add color variation for sparkle effect
            r = min(255, color[0] + random.randint(-30, 30))
            g = min(255, color[1] + random.randint(-30, 30))
            b = min(255, color[2] + random.randint(-30, 30))
            varied_color = (max(0, r), max(0, g), max(0, b))
            self.particles.append(Particle(x, y, varied_color))
    
    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.is_alive()]
    
    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
