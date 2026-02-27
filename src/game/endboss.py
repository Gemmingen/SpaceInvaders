"""EndBoss – final level boss (level 5).

Uses the `endboss.png` sprite and fires `endboss-attack.png` projectiles
toward the player at a configurable interval.
"""
import pygame
import math
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.game.miniboss_base import MiniBossBase

class EndBossProjectile(pygame.sprite.Sprite):
    """Projectile fired by the EndBoss."""
    def __init__(self, start_pos, target_pos, speed=5):
        super().__init__()
        img = pygame.image.load('assets/endboss-attack.png').convert_alpha()
        self.image = pygame.transform.scale(img, (30, 60))
        self.rect = self.image.get_rect(center=start_pos)
        # compute velocity towards target
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        dist = math.hypot(dx, dy) or 1
        self.vel_x = dx / dist * speed
        self.vel_y = dy / dist * speed
    def update(self, *args, **kwargs):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        # remove when off-screen
        if self.rect.top > kwargs.get('screen_height', 600):
            self.kill()

class EndBoss(MiniBossBase):
    def __init__(self, health=5, speed=2):
        super().__init__('assets/endboss.png', health, speed)
        # start near top centre
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.centery = 80
        self.direction = 1  # horizontal movement direction
        self.attack_cooldown = 120  # frames between shots (can be tweaked via config later)
        self.attack_timer = self.attack_cooldown
        self.projectiles = pygame.sprite.Group()

    def update(self, player=None, *args, **kwargs):
        # horizontal back‑and‑forth movement along top
        self.rect.x += self.direction * self.speed
        if self.rect.right >= kwargs.get('screen_width', SCREEN_WIDTH) or self.rect.left <= 0:
            self.direction *= -1
        # attack handling
        self.attack_timer -= 1
        if self.attack_timer <= 0 and player:
            proj = EndBossProjectile(self.rect.center, player.rect.center)
            self.projectiles.add(proj)
            self.attack_timer = self.attack_cooldown
        # update projectiles
        self.projectiles.update(screen_height=kwargs.get('screen_height'))
        # add to groups if provided
        if 'all_sprites' in kwargs:
            for p in self.projectiles:
                kwargs['all_sprites'].add(p)
        if 'enemy_bullets' in kwargs:
            for p in self.projectiles:
                kwargs['enemy_bullets'].add(p)
