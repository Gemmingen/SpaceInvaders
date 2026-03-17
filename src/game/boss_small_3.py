"""BossSmall3 – horizontal sweeper that drops bombs.

Appears on level 3. Moves left‑right near the top of the screen and
periodically spawns a bomb sprite (using the boss‑attack1 image) that falls
straight down.
"""
import pygame
import random
import math
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT, BOSS3_GLOB_SPLIT_ANGLE_DEGREES, BOSS3_GLOB_SPLIT_HEIGHT
from src.game.miniboss_base import MiniBossBase

# Configurable constants
GLOB_SPEED = 8          # Pixels per frame – fast enough to reach the player
PUDDLE_OFFSET = -40       # No vertical offset; puddle sits on player's bottom
# Inaccuracy in pixels applied to the homing glob's trajectory
INACCURACY_PIXELS = 30  # +/- 30 px random offset for dx/dy

class PoisonGlob(pygame.sprite.Sprite):
    """Simple bomb that falls vertically."""
    def __init__(self, x, y, speed=GLOB_SPEED, puddle_group=None, player=None, splits=False):
        super().__init__()
        img = pygame.image.load('assets/boss-attack1.png').convert_alpha()
        self.image = pygame.transform.scale(img, (30, 30))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        # Store exact floating‑point coordinates for precise movement
        self.exact_x = float(self.rect.x)
        self.exact_y = float(self.rect.y)
        # Reference to the group where puddles should be added
        self.puddle_group = puddle_group
        self.has_spawned = False
        self.player = player
        self.damage = 1  # reduced damage for this weaker homing bullet
        self.splits = splits          # flag: this bullet should split at mid‑screen
        self.has_split = False        # ensures split happens only once

    def update(self, *args, **kwargs):
        """Move the glob using exact float coordinates and kill on floor contact.

        Puddle creation is handled in ``kill()`` to ensure it always spawns.
        """
        # --- Movement (targeted or straight) ---
        if hasattr(self, 'vel_x') and hasattr(self, 'vel_y'):
            self.exact_x += self.vel_x
            self.exact_y += self.vel_y
        else:
            self.exact_y += self.speed

        # Sync integer rect with float coordinates
        self.rect.x = int(self.exact_x)
        self.rect.y = int(self.exact_y)

        # ----- Split logic (mid‑screen) -----
        if getattr(self, 'splits', False) and not getattr(self, 'has_split', False) and self.rect.centery >= BOSS3_GLOB_SPLIT_HEIGHT:
            # Prevent the original puddle from spawning
            self.has_spawned = True
            self.has_split = True
            # Create three child globs with diverging angles
            for angle in (-BOSS3_GLOB_SPLIT_ANGLE_DEGREES, 0, BOSS3_GLOB_SPLIT_ANGLE_DEGREES):
                rad = math.radians(angle)
                vx = math.sin(rad) * self.speed
                vy = math.cos(rad) * self.speed
                child = PoisonGlob(self.rect.centerx, self.rect.centery,
                                   speed=self.speed,
                                   puddle_group=self.puddle_group,
                                   player=self.player,
                                   splits=False)
                child.image = pygame.transform.scale(child.image, (15, 15))
                child.vel_x = vx
                child.vel_y = vy
                # Add child to all groups the parent belonged to
                for grp in self.groups():
                    grp.add(child)
            # Kill the original bullet without spawning a puddle
            self.kill()
            return

        # Kill when reaching the bottom of the screen (puddle will be spawned in kill())
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.kill()

    def kill(self):
        """Guarantee a puddle spawns before the sprite is removed.

        If a player reference was supplied, the puddle appears at the player's
        foot level (using the player's current bottom coordinate). Otherwise it
        falls to the bottom of the screen as before.
        """
        if not self.has_spawned and self.puddle_group is not None:
            # Preserve the projectile's X coordinate
            puddle_x = self.rect.centerx
            # Use the player's foot level if available, otherwise fall back to the glob's current bottom
            if self.player is not None:
                puddle_y = min(self.player.rect.bottom + PUDDLE_OFFSET, SCREEN_HEIGHT - 20)
            else:
                puddle_y = min(self.rect.bottom + PUDDLE_OFFSET, SCREEN_HEIGHT - 20)
            self.puddle_group.add(PoisonPuddle(puddle_x, puddle_y))
            self.has_spawned = True
        super().kill()

class PoisonPuddle(pygame.sprite.Sprite):
    """Lingers on the ground for a short time, damaging the player."""
    def __init__(self, x, y):
        super().__init__()
        try:
            img = pygame.image.load('assets/poison-puddle.png').convert_alpha()
        except Exception:
            img = pygame.Surface((64, 16), pygame.SRCALPHA)
            img.fill((0, 255, 0, 255))  # semi‑transparent green
        self.image = img
        self.rect = self.image.get_rect(midtop=(x, y))
        self.lifespan = 360  # 6 seconds @ 60 FPS

    def update(self, *args, **kwargs):
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.kill()


class BossSmall3(MiniBossBase):
    def __init__(self, health=3, speed=2):
        super().__init__('assets/boss-small3.png', health, speed)
        # Start near top‑left
        self.rect.centerx = self.rect.width // 2
        self.base_y = 120
        self.time_ticker = 0
        self.rect.centery = self.base_y
        self.direction = 1  # 1 = right, -1 = left
        self.drop_interval = 180
        self.drop_timer = self.drop_interval
        self.poison_group = pygame.sprite.Group()
        self.puddle_group = pygame.sprite.Group()

    def update(self, player=None, *args, **kwargs):  # Expected args: all_sprites, enemy_bullets, explosions, screen_width, screen_height, puddles_group
        """Update movement and drop PoisonGlob.

        Compatibility shim: accept positional arguments from Game.update.
        Expected positional order (if provided):
            0: all_sprites
            1: enemy_bullets
            2: explosions (currently unused)
            3: screen_width
            4: screen_height
            5: puddles (external puddle group)
        """
        # Populate kwargs from positional args if not already provided
        if len(args) >= 1 and 'all_sprites' not in kwargs:
            kwargs['all_sprites'] = args[0]
        if len(args) >= 2 and 'enemy_bullets' not in kwargs:
            kwargs['enemy_bullets'] = args[1]
        if len(args) >= 6 and 'puddles' not in kwargs:
            kwargs['puddles'] = args[5]

        # --- Sine wave vertical movement ---
        self.time_ticker += 0.05
        self.rect.centery = int(self.base_y + math.sin(self.time_ticker) * 50)

        # --- Horizontal movement (bounce) ---
        self.rect.x += self.direction * self.speed
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1

        # --- Poison glob dropping timer ---
        self.drop_timer -= 1
        if self.drop_timer <= 0:
            # Reduce the base speed (make the bullet slower) – 75 % of the original
            speed = int(GLOB_SPEED * 0.75)
            # Fire straight down without homing; enable split at mid‑screen
            glob = PoisonGlob(self.rect.centerx, self.rect.bottom,
                               speed=speed,
                               puddle_group=self.puddle_group,
                               player=player,
                               splits=True)
            # Straight‑down velocity
            glob.vel_x = 0
            glob.vel_y = speed
            self.poison_group.add(glob)
            self.drop_timer = self.drop_interval

        # --- Update poison globs (pass puddle group and player) ---
        self.poison_group.update()

        # --- Sync globs and puddles with external groups ---
        if 'all_sprites' in kwargs:
            for p in self.poison_group:
                kwargs['all_sprites'].add(p)
            for pd in self.puddle_group:
                kwargs['all_sprites'].add(pd)
        if 'enemy_bullets' in kwargs:
            for p in self.poison_group:
                kwargs['enemy_bullets'].add(p)
        if 'puddles' in kwargs:
            for pd in self.puddle_group:
                kwargs['puddles'].add(pd)
