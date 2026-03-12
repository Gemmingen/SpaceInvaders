"""Orb - parabolic arc projectile used by BossSmall2.

Spawns at boss center and follows a parabolic arc to the screen edges.
"""
import pygame
import random
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT, BOSS2_ORB_Y_PERCENT


class Orb(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_x, side, arc_height=150):
        super().__init__()
        # Load side‑specific sprite
        if side == "left":
            img_path = "assets/orb-left.png"
        elif side == "right":
            img_path = "assets/orb-right.png"
        else:
            # Fallback to default orb image if side is unexpected
            print(f"[Orb] Warning: unknown side '{side}'. Using default orb image.")
            img_path = "assets/orb.png"
        img = pygame.image.load(img_path).convert_alpha()
        width = int(img.get_width() * 2)
        height = int(img.get_height() * 2)
        self.image = pygame.transform.scale(img, (width, height))
        self.rect = self.image.get_rect(center=start_pos)
        
        self.start_x = start_pos[0]
        self.start_y = start_pos[1]
        self.target_x = target_x
        self.target_y = SCREEN_HEIGHT * BOSS2_ORB_Y_PERCENT
        self.side = side
        self.arc_height = arc_height
        
        self.progress = 0.0
        self.speed = 1.0 / 60.0
        self.locked = False
        # Number of frames to keep shaking after locking (default 0)
        self.shake_timer = 0
        
    def start_shake(self, frames):
        """Activate shaking for *frames* frames (approx 1 second @ 60 FPS)."""
        self.shake_timer = frames
        
    def update(self, *args, **kwargs):
        if self.locked:
            # If shaking timer is active, apply a small random jitter each frame
            if getattr(self, "shake_timer", 0) > 0:
                # jitter up to 4 pixels in any direction
                jitter_x = random.randint(-4, 4)
                jitter_y = random.randint(-4, 4)
                self.rect.x += jitter_x
                self.rect.y += jitter_y
                self.shake_timer -= 1
            # No movement when locked; just return after optional shake
            return
            
        self.progress += self.speed
        if self.progress >= 1.0:
            self.progress = 1.0
            self.locked = True
            
        t = self.progress
        quad_t = t * t
        inv_t = 1 - t
        inv_t_squared = inv_t * inv_t
        
        new_x = inv_t_squared * self.start_x + 2 * inv_t * t * ((self.start_x + self.target_x) / 2) + quad_t * self.target_x
        
        base_y = inv_t_squared * self.start_y + 2 * inv_t * t * ((self.start_y + self.target_y) / 2 + self.arc_height) + quad_t * self.target_y
        
        arc_offset = -4 * self.arc_height * t * (t - 1)
        new_y = base_y + arc_offset
        
        self.rect.centerx = int(new_x)
        self.rect.centery = int(new_y)
        
    def get_final_position(self):
        return (self.target_x, self.target_y)
