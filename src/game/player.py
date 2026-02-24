import pygame
from src.game.bullet import Bullet

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill((0, 255, 0))  # green player
        self.rect = self.image.get_rect(midbottom=(x, y))
        from src.config.config import PLAYER_SPEED
        self.speed = PLAYER_SPEED
        
        self.last_shot_time = 0
        self.shot_cooldown = 300  # milliseconds
        self.lives = 3
        pass
    
    def move(self, keys, screen_width):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            
        # Keep within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        pass
    
    def shoot(self):
        """Create a bullet if cooldown elapsed.
        Returns the ``Bullet`` instance or ``None`` if still on cooldown.
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shot_cooldown:
            bullet = Bullet(self.rect.centerx, self.rect.top, direction=-1)
            self.last_shot_time = current_time
            return bullet
        return None