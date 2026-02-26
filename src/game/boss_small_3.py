"""BossSmall3 – horizontal sweeper that drops bombs.

Appears on level 3. Moves left‑right near the top of the screen and
periodically spawns a bomb sprite (using the boss‑attack1 image) that falls
straight down.
"""
import pygame
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.game.miniboss_base import MiniBossBase

class Bomb(pygame.sprite.Sprite):
    """Simple bomb that falls vertically."""
    def __init__(self, x, y, speed=4):
        super().__init__()
        img = pygame.image.load('assets/boss-attack1.png').convert_alpha()
        self.image = pygame.transform.scale(img, (30, 30))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
    def update(self, *args, **kwargs):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class BossSmall3(MiniBossBase):
    def __init__(self, health=3, speed=2):
        super().__init__('assets/boss-small3.png', health, speed)
        # Start near top-left
        self.rect.centerx = self.rect.width // 2
        self.rect.centery = 120
        self.direction = 1  # 1 = right, -1 = left
        self.drop_interval = 180  # frames between bomb drops (adjust via config later)
        self.drop_timer = self.drop_interval
        # Group to hold bombs; will be added to game groups by the caller if needed
        self.bomb_group = pygame.sprite.Group()

    def update(self, *args, **kwargs):
        # Horizontal movement
        self.rect.x += self.direction * self.speed
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1
        # Bomb dropping timer
        self.drop_timer -= 1
        if self.drop_timer <= 0:
            bomb = Bomb(self.rect.centerx, self.rect.bottom)
            self.bomb_group.add(bomb)
            self.drop_timer = self.drop_interval
        # Update bombs
        self.bomb_group.update()
        # Add bombs to any sprite groups passed via kwargs (optional)
        if 'all_sprites' in kwargs:
            for b in self.bomb_group:
                kwargs['all_sprites'].add(b)
        if 'enemy_bullets' in kwargs:
            for b in self.bomb_group:
                kwargs['enemy_bullets'].add(b)
