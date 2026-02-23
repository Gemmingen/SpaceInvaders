import pygame
from src.config.config import BULLET_SPEED

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=-1):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill((255, 255, 0))  # yellow bullet
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = BULLET_SPEED * direction  # direction: -1 up, 1 down
        self.direction = direction
        pass
    
    def update(self):
        self.rect.y += self.speed
        # Remove bullet if it goes off-screen
        if self.rect.bottom < 0 or self.rect.top > pygame.display.get_surface().get_height():
            self.kill()
        pass