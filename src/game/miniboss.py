import pygame
import math
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT

class MiniBoss(pygame.sprite.Sprite):
    """Mini‑boss that orbits around the centre of the screen.

    The boss uses the existing UFO sprite image.  Its motion is a smooth
    circular orbit whose radius and angular speed can be tweaked via the
    ``MINIBOSS_SETTINGS`` configuration (the defaults are set in the class).
    """
    def __init__(self):
        super().__init__()
        # Re‑use the UFO image – path relative to project root
        self.image = pygame.image.load('assets/bonus-enemy.png').convert_alpha()
        self.rect = self.image.get_rect()
        # --- orbit parameters -------------------------------------------------
        self.orbit_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.radius = 150                     # distance from centre (pixels)
        self.angular_speed = 0.03             # radians per frame
        self.angle = -math.pi / 2             # start at top of the circle
        # Initialise position on the orbit
        self._update_position()
        # Health – will be overwritten by Game._spawn_miniboss() according to settings
        self.health = 3

    def _update_position(self):
        cx, cy = self.orbit_center
        self.rect.centerx = cx + self.radius * math.cos(self.angle)
        self.rect.centery = cy + self.radius * math.sin(self.angle)

    def update(self):
        # Advance along the circular path
        self.angle += self.angular_speed
        # Keep angle bounded (optional but tidy)
        if self.angle >= 2 * math.pi:
            self.angle -= 2 * math.pi
        self._update_position()

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()
