"""Fist sprite used by the Level‑1 boss (BossSmall1).

The fist has three states:
    * **attached** – hovers above the boss, no visual effect.
    * **charging** – swings left‑up (for the left fist) or right‑up (for the right fist) while flashing a 2‑pixel outline that alternates white/red.
    * **launched** – homes toward the player and is removed only after it fully leaves the screen.
"""
import pygame
# NOTE: This file provides the **only active fist implementation** used by the game.
# The earlier `boss_fist.py` contained a visual‑only prototype that is no longer used.
# All boss‑level fist behavior (charging, launching, homing) is handled here.

import math
from src.config.config import (
    FIST_CHARGE_TIME,
    FIST_FLASH_COLORS,
    FIST_FLASH_INTERVAL,
)
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT  # for off‑screen checks

class Fist(pygame.sprite.Sprite):
    """State‑machine for a boss fist.

    Parameters
    ----------
    side: str
        "left" or "right" – determines swing direction.
    boss_rect: pygame.Rect
        Reference to the owning boss rectangle (updated each frame).
    player: Player or None
        Player reference – filled when the fist starts charging.
    speed: float
        Pixels per frame when the fist is launched.
    """
    def __init__(self, side: str, boss_rect, player, speed: float):
        super().__init__()
        img_path = f'assets/boss-fist-{side}.png'
        original = pygame.image.load(img_path).convert_alpha()
        self.base_image = pygame.transform.scale(original, (40, 40))
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()

        self.side = side
        self.boss_rect = boss_rect          # live reference to the boss sprite
        self.player = player                # may be None until charge begins
        self.speed = speed

        # Hover offset (above the boss so the fists are visible)
        horiz = -30 if side == "left" else 30
        self.hover_offset = pygame.math.Vector2(horiz, 40)   # 40 px up

        # Swing offset applied during the charging phase (left‑up / right‑up)
        self.swing_offset = pygame.math.Vector2(
            -10 if side == "left" else 10,   # X direction
            -15                                 # Y always up while charging
        )

        # State tracking
        self.state = "attached"          # attached | charging | launched
        self.charge_timer = 0
        self.flash_timer = 0
        self.flash_index = 0

        self._update_attached_position()

    # -----------------------------------------------------------------
    def _update_attached_position(self):
        """Position the fist while attached (or at the start of charging)."""
        self.rect.centerx = self.boss_rect.centerx + self.hover_offset.x
        self.rect.centery = self.boss_rect.centery + self.hover_offset.y

    # -----------------------------------------------------------------
    def start_charge(self, player):
        """Enter the charging (swing + flash) state.
        The player reference is stored so the fist knows where to head after charging.
        """
        self.state = "charging"
        self.charge_timer = FIST_CHARGE_TIME
        self.flash_timer = FIST_FLASH_INTERVAL
        self.flash_index = 0
        self.player = player
        # Slightly enlarge to emphasise the charge (optional)
        scale = 1.2
        w, h = self.base_image.get_size()
        self.image = pygame.transform.scale(self.base_image,
                                            (int(w * scale), int(h * scale)))
        self.rect = self.image.get_rect(center=self.rect.center)

    # -----------------------------------------------------------------
    def launch(self):
        """Transition to the homing phase."""
        self.state = "launched"
        self.image = self.base_image               # back to normal size, no outline
        self.rect = self.image.get_rect(center=self.rect.center)

    # -----------------------------------------------------------------
    def update(self, *args, **kwargs):
        # -----------------------------------------------------------------
        # ATTACHED – simply hover above the boss
        if self.state == "attached":
            self._update_attached_position()
            return

        # -----------------------------------------------------------------
        # CHARGING – swing up and flash
        if self.state == "charging":
            # Keep the base hover position
            self._update_attached_position()

            # Apply swing offset proportionally to the elapsed charge time
            progress = 1 - (self.charge_timer / FIST_CHARGE_TIME)  # 0 → 1
            swing_factor = math.sin(progress * math.pi)           # ease‑in‑out curve
            offset = self.swing_offset * swing_factor
            self.rect.centerx += offset.x
            self.rect.centery += offset.y

            # Flash colour handling – toggle every FIST_FLASH_INTERVAL frames
            self.flash_timer -= 1
            if self.flash_timer <= 0:
                self.flash_timer = FIST_FLASH_INTERVAL
                self.flash_index = (self.flash_index + 1) % len(FIST_FLASH_COLORS)
                colour = FIST_FLASH_COLORS[self.flash_index]
                # Draw a 2‑pixel outline around the current image
                img = self.base_image.copy()
                pygame.draw.rect(img, colour, img.get_rect(), 2)
                self.image = img
                self.rect = self.image.get_rect(center=self.rect.center)

            # Count down the charge timer
            self.charge_timer -= 1
            if self.charge_timer <= 0:
                self.launch()
            return

        # -----------------------------------------------------------------
        # LAUNCHED – homing toward the player
        if not self.player:
            return
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy) or 1
        self.rect.x += dx / dist * self.speed
        self.rect.y += dy / dist * self.speed

        # Remove only after the fist fully leaves the screen (prevents premature death)
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()
