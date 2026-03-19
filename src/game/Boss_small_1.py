"""BossSmall1 – level‑1 miniboss (the *fist* boss).

Features:
- Orbits around the centre of the screen.
- Carries two fist sprites that are attached to its body.
- On a cooldown the fists launch, home toward the player and are removed when off‑screen.
- When both fists have been destroyed they re‑attach to the boss.
"""
import pygame
import math
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT, FIST_SETTINGS

from src.game.miniboss_base import MiniBossBase
from src.game.fist import Fist

class BossSmall1(MiniBossBase):
    def __init__(self, health=3, speed=2):
        super().__init__('assets/boss-small1.png', health, speed)
        # --- orbit parameters -------------------------------------------------
        self.orbit_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.radius = 150                     # distance from centre (pixels)
        self.angular_speed = self.speed * 0.015
        self.angle = -math.pi / 2             # start at top of the circle
        self._update_position()

        # ----- fist management -----
        self._player = None
        self.fists = pygame.sprite.Group()
        self.fist_group = self.fists          # Alias für game.py
        
        # Create two attached fists
        self.left_fist = Fist('left', self.rect, None, FIST_SETTINGS['speed'])
        self.right_fist = Fist('right', self.rect, None, FIST_SETTINGS['speed'])
        self.fists.add(self.left_fist, self.right_fist)
        self.fist_cooldown = FIST_SETTINGS.get('cooldown', 120)
        self.fist_timer = self.fist_cooldown
        self.fists_launched = 0  # how many fists currently in flight

    def _update_position(self):
        cx, cy = self.orbit_center
        self.rect.centerx = cx + self.radius * math.cos(self.angle)
        self.rect.centery = cy + self.radius * math.sin(self.angle)

    def update(self, player=None, *args, **kwargs):
        # --- Map positional arguments to kwargs ---
        if len(args) >= 1 and 'all_sprites' not in kwargs:
            kwargs['all_sprites'] = args[0]
        if len(args) >= 2 and 'enemy_bullets' not in kwargs:
            kwargs['enemy_bullets'] = args[1]
        if len(args) >= 3 and 'explosions' not in kwargs:
            kwargs['explosions'] = args[2]
        if len(args) >= 4 and 'screen_width' not in kwargs:
            kwargs['screen_width'] = args[3]
        if len(args) >= 5 and 'screen_height' not in kwargs:
            kwargs['screen_height'] = args[4]

        # --- orbit movement ---
        self.angle += self.angular_speed
        if self.angle >= 2 * math.pi:
            self.angle -= 2 * math.pi
        self._update_position()

        # store player reference for fists
        self._player = player

        # --- fist launch logic ---
        self.fist_timer -= 1
        if self.fist_timer <= 0 and self.fists_launched < 2:
            # start charging one attached fist (prefer left then right)
            for f in self.fists:
                if f.state == "attached":
                    f.start_charge(self._player)    
                    self.fists_launched += 1
                    break
            self.fist_timer = self.fist_cooldown

        # update all fists (they manage attached vs launched internally)
        self.fists.update(
            screen_width=kwargs.get('screen_width', SCREEN_WIDTH),
            screen_height=kwargs.get('screen_height', SCREEN_HEIGHT),
            explosions=kwargs.get('explosions'),
            all_sprites=kwargs.get('all_sprites')
        )

        # add fists to the groups supplied by the caller so they participate in collisions
        if 'all_sprites' in kwargs:
            for f in self.fists:
                kwargs['all_sprites'].add(f)
        if 'enemy_bullets' in kwargs:
            for f in self.fists:
                if f.state == "launched":
                    kwargs['enemy_bullets'].add(f)

        # --- respawn fists when all have been destroyed ---
        if len(self.fists) == 0:
            # recreate fists attached to the current boss rect
            self.left_fist = Fist('left', self.rect, self._player, FIST_SETTINGS['speed'])
            self.right_fist = Fist('right', self.rect, self._player, FIST_SETTINGS['speed'])
            self.fists.add(self.left_fist, self.right_fist)
            self.fists_launched = 0

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.left_fist.kill() 
            self.right_fist.kill()
            self.kill()