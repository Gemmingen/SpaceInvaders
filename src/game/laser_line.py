"""LaserLine implementation using sprite‑based growth.

The laser consists of many ``LaserSegment`` sprites (the 25 × 5 px
``laser-element.png``). When a laser is created it starts with a tiny pause,
then segments are added on the left and right sides every
``BOSS2_LASER_BUILD_INTERVAL`` seconds (0.1 s by default). After all required
segments are in place the whole beam slides downward at ``BOSS2_LASER_SPEED``.

The gap in the middle is three times the player width (controlled via
``BOSS2_GAP_WIDTH_MULTIPLIER``). The implementation keeps the original public
API – ``LaserLine(y, left_center_x, right_center_x, player_x,
orb_half_width)`` – so ``BossSmall2`` does not need to change.
"""

import math
import pygame
import random
from src.config.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BOSS2_LASER_SPEED,
    BOSS2_GAP_WIDTH_MULTIPLIER,
    BOSS2_GAP_RANDOM_RANGE,
    BOSS2_LASER_ORB_MARGIN,
    BOSS2_LASER_SPRITE,
    BOSS2_LASER_SPRITE_WIDTH,
    BOSS2_CHARGE_FRAMES,
    FPS,
    # Side‑laser config
    BOSS2_SIDE_LASER_SPRITE,
    BOSS2_SIDE_LASER_PAUSE_FRAMES,
    BOSS2_SIDE_LASER_SPEED,
)

class LaserSegment(pygame.sprite.Sprite):
    """A single laser sprite for the left or right side.

    The image is loaded from ``BOSS2_LASER_SPRITE`` and scaled to the supplied
    width (default ``BOSS2_LASER_SPRITE_WIDTH``). The segment is static – movement
    is handled by the containing ``LaserLine``.
    """
    def __init__(self, x, y, width: int = BOSS2_LASER_SPRITE_WIDTH):
        super().__init__()
        sprite = pygame.image.load(BOSS2_LASER_SPRITE).convert_alpha()
        # Scale sprite horizontally to the required width while preserving height
        self.image = pygame.transform.scale(sprite, (width, sprite.get_height()))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)


class LaserLine(pygame.sprite.Sprite):
    # existing implementation unchanged
    """Container for a laser that grows segment‑by‑segment.

    Parameters
    ----------
    y_pos : int
        Vertical position where the laser should appear.
    left_center_x, right_center_x : int
        Center x‑coordinates of the left/right orb.
    player_x : int
        Current player x‑position (used for gap calculation).
    orb_half_width : int, optional
        Half the visual width of an orb sprite; used to offset the laser start
        from the orb edge.
    """

    def __init__(self, y_pos, left_center_x, right_center_x, player_x, orb_half_width=0):
        super().__init__()
        # Outer edges of the orbs, plus a visual margin
        self.left_edge = left_center_x + orb_half_width + BOSS2_LASER_ORB_MARGIN
        self.right_edge = right_center_x - orb_half_width - BOSS2_LASER_ORB_MARGIN
        self.y_pos = y_pos
        self.player_x = player_x

        # Gap width based on player width (32 px) and multiplier
        self.player_width = 32
        self.gap_width = int(self.player_width * BOSS2_GAP_WIDTH_MULTIPLIER)

        # Determine gap centre
        self.gap_x = self._calculate_gap_x()
        self._target_left_end = self.gap_x - self.gap_width // 2
        self._target_right_start = self.gap_x + self.gap_width // 2

        # Group holding the visible segments
        self.segments = pygame.sprite.Group()

        # Timing – hold the full laser for a short charge period before moving
        self._pause_counter = BOSS2_CHARGE_FRAMES   # frames to wait before moving (1 second at 60 FPS)
        self.speed = 0                # Downward speed (set after pause finishes)
        self.damage = 1  # LaserLine deals 1 damage to the player (consistent with other projectiles)
        
        # --- NEW: Allow speed to be overridden by the Boss ---
        self.speed_override = None
        # -----------------------------------------------------

        # Create full‑width left and right laser segments immediately
        left_width = max(0, self._target_left_end - self.left_edge)
        right_width = max(0, self.right_edge - self._target_right_start)
        if left_width > 0:
            left_seg = LaserSegment(self.left_edge, y_pos, width=int(left_width))
            self.segments.add(left_seg)
        if right_width > 0:
            right_seg = LaserSegment(self._target_right_start, y_pos, width=int(right_width))
            self.segments.add(right_seg)

        # Invisible placeholder sprite
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(self.left_edge, y_pos))

    # ------------------------------------------------------------------ #
    # Gap calculation – unchanged from the original implementation
    # ------------------------------------------------------------------ #
    def _calculate_gap_x(self):
        raw_gap = self.player_x + random.randint(
            -BOSS2_GAP_RANDOM_RANGE, BOSS2_GAP_RANDOM_RANGE
        )
        min_x = int(self.left_edge) + self.gap_width // 2
        max_x = int(self.right_edge) - self.gap_width // 2
        if min_x >= max_x:
            return (min_x + max_x) // 2
        return max(min_x, min(raw_gap, max_x))

    # ------------------------------------------------------------------ #
    # Update – handles initial pause, segment growth and normal descent
    # ------------------------------------------------------------------ #
    def update(self, *args, **kwargs):
        # -------------------------------------------------------------- #
        # 1️⃣ Initial pause (visual cue before the laser appears)
        # -------------------------------------------------------------- #
        if self._pause_counter > 0:
            self._pause_counter -= 1
            return

        # Pause finished – start moving the laser downward
        if self.speed == 0:
            # --- NEW: Use override if set, otherwise fallback to default ---
            if self.speed_override is not None:
                self.speed = self.speed_override
            else:
                self.speed = BOSS2_LASER_SPEED
            # ---------------------------------------------------------------

        # -------------------------------------------------------------- #
        # 3️⃣ Normal downward movement after the laser is fully built
        # -------------------------------------------------------------- #
        self.rect.y += self.speed
        for seg in self.segments:
            seg.rect.y += self.speed

        # Remove the laser when it leaves the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    # ------------------------------------------------------------------ #
    # Collision handling – return the rects of all live segments
    # ------------------------------------------------------------------ #
    def get_hitboxes(self):
        return [seg.rect.copy() for seg in self.segments]

    # ------------------------------------------------------------------ #
    # Ensure segments are cleaned up when the container is killed
    # ------------------------------------------------------------------ #
    def kill(self):
        # Ensure every segment sprite is killed so it is removed from any groups it was added to.
        for seg in self.segments:
            seg.kill()
        # Clear the internal group and then kill the container sprite.
        self.segments.empty()
        super().kill()


class SideLaser(pygame.sprite.Sprite):
    """Stationary vertical laser that appears at a given x‑coordinate.

    It uses the same initial pause as ``LaserLine`` but does **not** move
    afterwards. It has no gap – the whole sprite is a solid beam.
    """
    def __init__(self, x_center, y_pos, orb=None):
        super().__init__()
        sprite = pygame.image.load(BOSS2_SIDE_LASER_SPRITE).convert_alpha()
        self.image = sprite
        self.rect = self.image.get_rect(midtop=(x_center, y_pos))
        self.mask = pygame.mask.from_surface(self.image)
        self._pause_counter = BOSS2_SIDE_LASER_PAUSE_FRAMES
        # No speed – laser stays stationary after the pause
        self.speed = 0
        # Expose a ``segments`` group so the boss update logic can treat it like a regular LaserLine
        self.segments = pygame.sprite.Group(self)
        # Store reference to the orb (if any) and compute the horizontal offset used at spawn
        self.orb = orb
        self.offset = x_center - (orb.rect.centerx if orb else 0)

    def update(self, *args, **kwargs):
        # Initial pause – after this the laser remains stationary
        if self._pause_counter > 0:
            self._pause_counter -= 1
            return
        # Follow the orb’s position (including shake jitter) if attached
        if self.orb:
            self.rect.midtop = (self.orb.rect.centerx + self.offset, self.orb.rect.centery)
        # Keep the segment rects in sync (they already match ``self.rect``)
        for seg in self.segments:
            seg.rect.topleft = self.rect.topleft
        # No auto‑kill; cleanup handled by boss.
        pass

    def kill(self):
        # Ensure the segment sprite is also removed from any groups.
        # ``self.segments`` contains ``self`` for SideLaser, so we must not
        # iterate over it (that would cause infinite recursion).  Simply
        # clear the group and then call the superclass ``kill``.
        self.segments.empty()
        super().kill()

    def get_hitboxes(self):
        """Return a list containing the rectangle of this side laser.

        The boss collision code expects every laser sprite to implement a
        ``get_hitboxes`` method that returns an iterable of ``pygame.Rect``
        objects.  ``SideLaser`` is a single‑segment sprite, so we simply
        return a copy of its own rect.
        """
        return [self.rect.copy()]
