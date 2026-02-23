import pygame
from src.config.config import ENEMY_SPEED
from src.game.bullet import Bullet

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill((255, 0, 0))  # red enemy
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = ENEMY_SPEED
        pass
    
    def move(self, direction):
        self.rect.x += direction * self.speed
        pass
    
    def shoot(self):
        # Enemy bullet shoots downward
        bullet = Bullet(self.rect.centerx, self.rect.bottom, direction=1)
        return bullet
        pass