import pygame
from src.game.bullet import Bullet
from src.utils.helpers import load_image
from src.config.config import PLAYER_SPEED

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Sprites laden und skalieren (z.B. auf 32x32 Pixel)
        self.image_idle = pygame.transform.scale(load_image("assets/player-idle.png").convert_alpha(), (32, 32))
        self.image_left = pygame.transform.scale(load_image("assets/player-left.png").convert_alpha(), (32, 32))
        self.image_right = pygame.transform.scale(load_image("assets/player-right.png").convert_alpha(), (32, 32))
        
        self.image = self.image_idle
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = PLAYER_SPEED
        
        self.last_shot_time = 0
        self.shot_cooldown = 300  # milliseconds
        self.lives = 3
    
    def move(self, keys, screen_width):
        # Standardmäßig Idle-Sprite
        self.image = self.image_idle
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.image = self.image_left
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            self.image = self.image_right
            
        # Keep within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
    
    def shoot(self):
        """Create a bullet if cooldown elapsed."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shot_cooldown:
            bullet = Bullet(self.rect.centerx, self.rect.top, direction=-1)
            self.last_shot_time = current_time
            return bullet
        return None