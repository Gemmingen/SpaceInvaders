"""BossSmall2 – sinusoidal horizontal glide.

Appears on level 2. Moves left‑right across the top of the screen while its
vertical position follows a sine wave. No projectile attack by default.
"""
import pygame
import math
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.game.miniboss_base import MiniBossBase

class BossSmall2(MiniBossBase):
    def __init__(self, health=3, speed=2):
        super().__init__('assets/boss-small2.png', health, speed)
        # Start near the top, centered horizontally
        self.base_y = 120
        self.amplitude = 60          # vertical sine amplitude
        self.frequency = 0.02        # controls wavelength
        self.x = 0
        self.direction = 1  # 1 = right, -1 = left
        # Initialise position
        self.rect.centerx = self.x
        self.rect.centery = self.base_y + self.amplitude * math.sin(self.x * self.frequency)

    def update(self, *args, **kwargs):
        # Move horizontally
        self.x += self.direction * self.speed
        if self.x > SCREEN_WIDTH - self.rect.width // 2:
            self.direction = -1
        elif self.x < self.rect.width // 2:
            self.direction = 1
        # Update position with sine wave
        self.rect.centerx = self.x
        self.rect.centery = self.base_y + self.amplitude * math.sin(self.x * self.frequency)
