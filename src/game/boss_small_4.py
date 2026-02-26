"""BossSmall4 – player‑chasing drone with laser attack.

Appears on level 4. Continuously moves toward the player and fires a laser
(sprite ``boss-attack2.png``) toward the player every ``attack_cooldown``
frames.
"""
import pygame
import math
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.game.miniboss_base import MiniBossBase

class Laser(pygame.sprite.Sprite):
    """Simple laser projectile aimed at the player."""
    def __init__(self, start_pos, target_pos, speed=6):
        super().__init__()
        img = pygame.image.load('assets/boss-attack2.png').convert_alpha()
        self.image = pygame.transform.scale(img, (20, 40))
        self.rect = self.image.get_rect(center=start_pos)
        # Compute normalized direction vector
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        dist = math.hypot(dx, dy) or 1
        self.vel_x = dx / dist * speed
        self.vel_y = dy / dist * speed
    def update(self, *args, **kwargs):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        # Remove if off‑screen
        if (self.rect.right < 0 or self.rect.left > kwargs.get('screen_width', 800) or
                self.rect.bottom < 0 or self.rect.top > kwargs.get('screen_height', 600)):
            self.kill()

class BossSmall4(MiniBossBase):
    def __init__(self, health=3, speed=2):
        super().__init__('assets/boss-small4.png', health, speed)
        # Start near top centre
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.centery = 100
        self.attack_cooldown = 120  # frames between laser shots (can be tweaked via config)
        self.attack_timer = self.attack_cooldown
        self.laser_group = pygame.sprite.Group()

    def update(self, player=None, *args, **kwargs):
        # Move toward player if provided
        if player:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy) or 1
            self.rect.x += (dx / dist) * self.speed
            self.rect.y += (dy / dist) * self.speed
        # Attack timer
        self.attack_timer -= 1
        if self.attack_timer <= 0 and player:
            laser = Laser(self.rect.center, player.rect.center)
            self.laser_group.add(laser)
            self.attack_timer = self.attack_cooldown
        # Update lasers
        self.laser_group.update(screen_width=kwargs.get('screen_width'), screen_height=kwargs.get('screen_height'))
        # Add lasers to provided groups if any
        if 'all_sprites' in kwargs:
            for l in self.laser_group:
                kwargs['all_sprites'].add(l)
        if 'enemy_bullets' in kwargs:
            for l in self.laser_group:
                kwargs['enemy_bullets'].add(l)
