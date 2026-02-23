import random
import pygame
from src.config.config import UFO_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT

class UFO(pygame.sprite.Sprite):
    """Placeholder Mystery Ship (UFO) that moves horizontally across the top.
    It is drawn as a simple magenta rectangle (placeholder for future sprite).
    """

    def __init__(self):
        super().__init__()
        # Placeholder size – 32x16 (same width as player, half height)
        self.image = pygame.Surface((32, 16), pygame.SRCALPHA)
        self.image.fill((255, 0, 255))  # magenta placeholder
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
        """Move horizontally; self‑destruct when off‑screen."""
        self.rect.x += UFO_SPEED * self.direction
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
