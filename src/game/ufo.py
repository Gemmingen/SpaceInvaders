import random
import pygame
from src.config.config import UFO_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT
from src.utils.helpers import load_image

class UFO(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # Lade das Bonus Enemy Sprite und skaliere es passend
        img = load_image("assets/bonus-enemy.png").convert_alpha()
        self.image = pygame.transform.scale(img, (32, 16))
        self.rect = self.image.get_rect()
        
        # Random start side
        if random.choice([True, False]):
            self.rect.left = -self.rect.width
            self.direction = 1  # move right
        else:
            self.rect.right = SCREEN_WIDTH + self.rect.width
            self.direction = -1  # move left
        self.rect.top = 20  # near top of screen

    def update(self):
        """Move horizontally; self-destruct when off-screen."""
        self.rect.x += UFO_SPEED * self.direction
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()