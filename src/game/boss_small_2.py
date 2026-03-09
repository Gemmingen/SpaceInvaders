"""BossSmall2 – level 2 boss with a simplified laser attack.

State machine (high‑level):
- **MOVE**: Boss slides horizontally at the top for ``BOSS2_MOVE_DURATION`` seconds.
- **ATTACK**: Sequence of sub‑states:
  1. **FLASH** – boss flashes red for ``BOSS2_FLASH_DURATION`` seconds.
  2. **ORB_SPAWN** – two orbs arc into position (duration ``BOSS2_ORB_ARC_DURATION``).
  3. **LASER_CHARGE** – optional short pause (handled by ``LaserLine`` itself).
  4. **LASER_FIRED** – a single laser line is created and stays for ``BOSS2_CHARGE_FRAMES``
     (≈1 s) before moving downwards.
  5. **CLEANUP** – remove orbs and reset for next move phase.

The laser line is built instantly from ``laser-element.png`` (full width on each side),
dwells at the orb level for one second, then descends and is removed when it exits the
screen. This implementation removes the previous multi‑laser barrage logic and makes
the flow deterministic and easy to test.
"""

from datetime import time
import pygame
import random
from src.config.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    BOSS2_MOVE_DURATION,
    BOSS2_FLASH_DURATION,
    BOSS2_ORB_ARC_DURATION,
    BOSS2_ORB_Y_PERCENT,
    BOSS2_CHARGE_FRAMES,
    BOSS2_LASER_X_OFFSET,
    BOSS2_LASER_COUNT,
    BOSS2_LASER_SPAWN_INTERVAL,
)
from src.game.miniboss_base import MiniBossBase
from src.game.orb import Orb
from src.game.laser_line import LaserLine
from src.game.explosion import Explosion


class BossSmall2(MiniBossBase):
    # Primary states
    STATE_MOVE = "move"
    STATE_ATTACK = "attack"

    # Attack sub‑states (order matters)
    ATTACK_FLASH = "flash"
    ATTACK_ORB_SPAWN = "orb_spawn"
    ATTACK_LASER_CHARGE = "laser_charge"  # placeholder – LaserLine does its own charge
    ATTACK_LASER_BARRAGE = "laser_barrage"
    ATTACK_ORB_SHAKE = "orb_shake"
    ATTACK_ORB_EXPLOSION = "orb_explosion"
    ATTACK_CLEANUP = "cleanup"

    def __init__(self, health=3, speed=2):
        super().__init__("assets/boss-small2.png", health, speed)
        # Position the boss near the top centre
        self.base_y = int(SCREEN_HEIGHT * 0.10)
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.centery = self.base_y

        self.direction = 1
        self.x = self.rect.centerx

        # Initialise state tracking variables
        self.state = self.STATE_MOVE
        self.attack_substate = None
        self.move_timer = BOSS2_MOVE_DURATION * FPS
        self.flash_timer = 0
        self.orb_spawn_timer = 0
        # laser handling
        self.laser_spawn_timer = 0
        self.laser_count = 0
        self.orb_shake_timer = 0
        self.explosion_timer = 0

        # Sprite groups for orbs and lasers
        self.orbs = pygame.sprite.Group()
        self.laser_lines = pygame.sprite.Group()

        self.original_image = self.image.copy()
        self.is_flashing = False

        # References set each frame by the Game loop
        self._player = None
        self._all_sprites = None
        self._enemy_bullets = None
        self._explosions = None

    # ------------------------------------------------------------------
    # Public helpers used by the Game loop
    # ------------------------------------------------------------------
    def start_attack(self):
        """Enter the ATTACK state and begin with the flash sub‑state."""
        self.state = self.STATE_ATTACK
        self.attack_substate = self.ATTACK_FLASH
        self.flash_timer = BOSS2_FLASH_DURATION * FPS
        self.is_flashing = True

    def spawn_orbs(self):
        """Create the left and right orbs and add them to the relevant groups."""
        start_pos = self.rect.center
        left_orb = Orb(start_pos, 30, "left", arc_height=150)
        right_orb = Orb(start_pos, SCREEN_WIDTH - 30, "right", arc_height=150)
        self.orbs.add(left_orb, right_orb)
        if self._all_sprites:
            self._all_sprites.add(left_orb, right_orb)
        if self._enemy_bullets:
            self._enemy_bullets.add(left_orb, right_orb)

    def spawn_laser_line(self):
        """Create a single LaserLine spanning between the two orbs.

        The line is built instantly (full width on each side) and will dwell for
        ``BOSS2_CHARGE_FRAMES`` frames before moving downwards.
        """
        if len(self.orbs) < 2:
            return
        left_orb = right_orb = None
        for orb in self.orbs:
            if orb.side == "left":
                left_orb = orb
            elif orb.side == "right":
                right_orb = orb
        if not left_orb or not right_orb:
            return

        # Player x is used for the gap calculation inside LaserLine
        player_x = self._player.rect.centerx if self._player else SCREEN_WIDTH // 2
        half_orb_width = left_orb.rect.width // 2
        laser_y = int(SCREEN_HEIGHT * BOSS2_ORB_Y_PERCENT)
        # Apply the optional horizontal offset for visual alignment
        # No horizontal offset – laser should start exactly at the orb edges
        laser = LaserLine(
            laser_y,
            left_orb.rect.centerx,
            right_orb.rect.centerx,
            player_x,
            orb_half_width=half_orb_width,
        )
        # Add laser to groups for drawing / collision. Segments are added globally in ``update``.
        self.laser_lines.add(laser)
        if self._all_sprites:
            self._all_sprites.add(laser)
            # Ensure orbs are drawn over the laser ends
            for orb in (left_orb, right_orb):
                self._all_sprites.remove(orb)
                self._all_sprites.add(orb)
        if self._enemy_bullets:
            self._enemy_bullets.add(laser)

    def cleanup_orbs(self, spawn_only=False):
        """Create an explosion at each orb position.
        If ``spawn_only`` is ``False`` (default) the orbs are also removed.
        """
        for orb in self.orbs:
            explosion = Explosion(orb.rect.centerx, orb.rect.centery, size=64)
            if self._all_sprites is not None:
                self._all_sprites.add(explosion)
            if self._explosions is not None:
                self._explosions.add(explosion)
        if not spawn_only:
            self.orbs.empty()

    # ------------------------------------------------------------------
    # Core update – called each frame by the Game loop
    # ------------------------------------------------------------------
    def update(self, player=None, all_sprites=None, enemy_bullets=None, explosions=None, *args, **kwargs):
        self._player = player
        self._all_sprites = all_sprites
        self._enemy_bullets = enemy_bullets
        self._explosions = explosions

        if self.state == self.STATE_MOVE:
            self._update_move_state()
        elif self.state == self.STATE_ATTACK:
            self._update_attack_state()

        # Update child sprite groups
        self.orbs.update()
        self.laser_lines.update()

        # Ensure laser segments are present in the global groups (draw / collision)
        if self._all_sprites:
            for laser in self.laser_lines:
                self._all_sprites.add(laser.segments)
        if self._enemy_bullets:
            for laser in self.laser_lines:
                self._enemy_bullets.add(laser.segments)

    # ------------------------------------------------------------------
    # State implementations
    # ------------------------------------------------------------------
    def _update_move_state(self):
        # Simple horizontal back‑and‑forth movement at the top
        self.x += self.direction * self.speed
        if self.x > SCREEN_WIDTH - self.rect.width // 2:
            self.direction = -1
        elif self.x < self.rect.width // 2:
            self.direction = 1
        self.rect.centerx = self.x
        self.rect.centery = self.base_y
        # Countdown to next attack
        self.move_timer -= 1
        if self.move_timer <= 0:
            self.start_attack()

    def _update_attack_state(self):
        # Dispatch based on the current sub‑state
        if self.attack_substate == self.ATTACK_FLASH:
            self._update_flash_state()
        elif self.attack_substate == self.ATTACK_ORB_SPAWN:
            self._update_orb_spawn_state()
        elif self.attack_substate == self.ATTACK_LASER_CHARGE:
            self._update_laser_charge_state()
        elif self.attack_substate == self.ATTACK_LASER_BARRAGE:
            self._update_laser_barrage_state()
        elif self.attack_substate == self.ATTACK_ORB_SHAKE:
            self._update_orb_shake_state()
        elif self.attack_substate == self.ATTACK_ORB_EXPLOSION:
            self._update_orb_explosion_state()
        elif self.attack_substate == self.ATTACK_CLEANUP:
            self._update_cleanup_state()

    # ------------------------------------------------------------------
    # Sub‑state helpers
    # ------------------------------------------------------------------
    def _update_flash_state(self):
        self.flash_timer -= 1
        # Simple red tint flash (alternating every few frames)
        if self.flash_timer % 6 < 3:
            tint = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            tint.fill((255, 0, 0, 100))
            self.image = self.original_image.copy()
            self.image.blit(tint, (0, 0))
        else:
            self.image = self.original_image.copy()
        if self.flash_timer <= 0:
            self.attack_substate = self.ATTACK_ORB_SPAWN
            self.orb_spawn_timer = BOSS2_ORB_ARC_DURATION * FPS
            self.spawn_orbs()

    def _update_orb_spawn_state(self):
        self.orb_spawn_timer -= 1
        # All orbs lock onto their target when the arc finishes
        all_locked = all(getattr(orb, "locked", False) for orb in self.orbs)
        if all_locked and self.orb_spawn_timer <= 0:
            # Transition to laser charge – LaserLine will handle the 1 s dwell
            self.attack_substate = self.ATTACK_LASER_CHARGE

    def _update_laser_charge_state(self):
        """Start the laser barrage.
        The first laser is spawned immediately; subsequent lasers will be spawned
        by ``_update_laser_barrage_state`` at regular intervals.
        """
        # Spawn the initial laser line
        self.spawn_laser_line()
        self.laser_count = 1
        # Set timer for the next laser
        self.laser_spawn_timer = BOSS2_LASER_SPAWN_INTERVAL * FPS
        # Move to barrage handling state
        self.attack_substate = self.ATTACK_LASER_BARRAGE

    def _update_laser_barrage_state(self):
        """Handle spawning of multiple lasers and wait for all to clear.
        Fires a new laser every ``BOSS2_LASER_SPAWN_INTERVAL`` seconds until
        ``BOSS2_LASER_COUNT`` lasers have been created. After the last laser is
        spawned, we wait until the ``laser_lines`` group is empty before moving
        on to the orb‑shake phase.
        """
        # Count down to the next laser spawn
        if self.laser_count < BOSS2_LASER_COUNT:
            self.laser_spawn_timer -= 1
            if self.laser_spawn_timer <= 0:
                self.spawn_laser_line()
                self.laser_count += 1
                # Reset timer for the next laser (if any left)
                self.laser_spawn_timer = BOSS2_LASER_SPAWN_INTERVAL * FPS
        # After the required number of lasers have been fired, wait for them to disappear
        if self.laser_count >= BOSS2_LASER_COUNT:
            if not self.laser_lines:  # all lasers cleared
                self.attack_substate = self.ATTACK_ORB_SHAKE
                self.orb_shake_timer = FPS  # 1‑second shake before explosion


    def _update_orb_shake_state(self):
        """Shake the orbs for a short duration before they explode.
        The shake effect itself is handled by the ``Orb`` class (via ``start_shake``).
        After the timer expires we move to the explosion sub‑state.
        """
        # On first entry, start shaking (if not already started)
        if not getattr(self, "orb_shake_started", False):
            for orb in self.orbs:
                orb.start_shake(FPS)
            self.orb_shake_started = True
        self.orb_shake_timer -= 1
        if self.orb_shake_timer <= 0:
            self.attack_substate = self.ATTACK_ORB_EXPLOSION

            # Explosion duration – roughly the length of the Explosion animation (14 frames at 60 FPS)
            self.explosion_timer = 30  # ~0.5 s (enough for the explosion animation)

    def _update_orb_explosion_state(self):

        """Spawn explosions, hide orbs, and wait for the animation to finish.
        The explosions are added to the global sprite groups. Orbs remain in
        ``self.orbs`` (so we can clear them later) but are removed from the
        rendering layer to avoid covering the explosion.
        """
        # First entry: spawn explosions and hide orbs
        if not getattr(self, "explosion_started", False):
            self.cleanup_orbs(spawn_only=True)
            # Debug: print explosion group size after spawning
            # Remove orbs from the global sprite group so they are not drawn
            if self._all_sprites:
                for orb in self.orbs:
                    if orb in self._all_sprites:
                        self._all_sprites.remove(orb)
            self.explosion_started = True
        # Countdown timer (set previously in shake state)
        self.explosion_timer -= 1
        if self.explosion_timer <= 0:
            # After explosion animation, finally remove orbs
            self.orbs.empty()
            self.attack_substate = self.ATTACK_CLEANUP
            # Reset flag for next attack cycle
            self.explosion_started = False

    # Laser barrage state handled in _update_laser_barrage_state (no separate fired state)
    def _update_cleanup_state(self):
        # Reset to MOVE state for the next cycle
        self.state = self.STATE_MOVE
        self.move_timer = BOSS2_MOVE_DURATION * FPS
        self.attack_substate = None
        self.is_flashing = False
        self.image = self.original_image.copy()
        # Reset laser counters for the next attack
        self.laser_spawn_timer = 0
        self.laser_count = 0
        self.orb_shake_started = False
        self.orb_shake_timer = 0
        self.explosion_timer = 0

    # ------------------------------------------------------------------
    # Utility methods used by collision detection in the main game loop
    # ------------------------------------------------------------------
    def get_laser_hitboxes(self):
        hitboxes = []
        for laser in self.laser_lines:
            hitboxes.extend(laser.get_hitboxes())
        return hitboxes

    def get_orb_hitboxes(self):
        return [orb.rect for orb in self.orbs]

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.orbs.empty()
            self.laser_lines.empty()
            self.kill()
