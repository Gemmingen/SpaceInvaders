import random
import pygame
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT, UFO_SPAWN_HEIGHT_OPTIONS, UFO_SPEED_OPTIONS
from src.utils.helpers import load_image

class UFO(pygame.sprite.Sprite):
    """UFO (bonus ship) that flies horizontally across the screen.

    The vertical spawn position determines the horizontal speed:
        * Higher (smaller y) → slower speed
        * Lower (larger y)   → faster speed
    The mapping is defined in ``config.py`` via the two parallel lists
    ``UFO_SPAWN_HEIGHT_OPTIONS`` and ``UFO_SPEED_OPTIONS``.
    """

    def __init__(self):
        super().__init__()
        # Load the UFO sprite and scale it to the desired size
        img = load_image("assets/bonus-enemy.png").convert_alpha()
        self.image = pygame.transform.scale(img, (32, 16))
        self.rect = self.image.get_rect()

        # -----------------------------------------------------
        # 1) Choose an index that ties a spawn height to a speed
        self._speed_selector = random.choice(
            range(len(UFO_SPAWN_HEIGHT_OPTIONS))
        )  # 0, 1, or 2 (or more if config is extended)
        # 2) Derive speed and vertical position from that index
        self.speed = UFO_SPEED_OPTIONS[self._speed_selector]
        self.rect.top = UFO_SPAWN_HEIGHT_OPTIONS[self._speed_selector]
        # -----------------------------------------------------
        # 3) Randomly decide which side of the screen the UFO enters from
        if random.choice([True, False]):
            # Start just off the left edge, moving right
            self.rect.left = -self.rect.width
            self.direction = 1
        else:
            # Start just off the right edge, moving left
            self.rect.right = SCREEN_WIDTH + self.rect.width
            self.direction = -1

        # Apply an initial horizontal offset so the UFO is already moving
        self.rect.x += self.speed * self.direction

        # If the UFO somehow starts completely off‑screen, destroy it immediately
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

    def update(self):
        """Move horizontally according to its speed; destroy when off‑screen."""
        self.rect.x += self.speed * self.direction
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()