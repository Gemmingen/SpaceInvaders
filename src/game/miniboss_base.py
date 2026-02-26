"""Base class for all minibosses.

Provides common health handling, sprite loading, and a placeholder for
`update`/`attack` methods that concrete subclasses should override.
"""
import pygame
import math
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT

class MiniBossBase(pygame.sprite.Sprite):
    """Common functionality for minibosses.

    Parameters
    ----------
    sprite_path: str
        Path to the image file relative to the project root.
    health: int, default 3
    speed: float, default 2 – meaning is defined by subclass (e.g., angular speed,
        pixels per frame, etc.)
    """
    def __init__(self, sprite_path: str, health: int = 3, speed: float = 2):
        super().__init__()
        original_image = pygame.image.load(sprite_path).convert_alpha()
        # Scale uniformly to 100x100 – can be overridden by subclass if needed
        self.image = pygame.transform.scale(original_image, (100, 100))
        self.rect = self.image.get_rect()
        self.health = health
        self.speed = speed
        # Subclass may set its own position variables

    def hit(self):
        """Called when a player bullet hits the boss."""
        self.health -= 1
        if self.health <= 0:
            self.kill()

    # Subclasses should implement `update` (movement) and optional `attack`
    def update(self, *args, **kwargs):
        raise NotImplementedError("MiniBoss subclasses must implement update method")
