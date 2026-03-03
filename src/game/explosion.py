import pygame
from src.utils.helpers import load_image

class Explosion(pygame.sprite.Sprite):
    """Animated explosion displayed when an enemy or boss is destroyed.

    By default the explosion is 32×32 (suitable for normal enemies). For larger
    entities (e.g., bosses) a custom ``size`` argument can be provided – the frames
    are scaled to ``size``×``size``. The same seven frame images are reused.
    """

    # Class‑level cache of original loaded images (unscaled). This avoids loading
    # the PNG files repeatedly. Each instance will scale them to the requested
    # size.
    _original_frames = None

    def __init__(self, x: int, y: int, size: int = 32, velocity: tuple[int, int] = (0, 0)):
        super().__init__()
        if Explosion._original_frames is None:
            # Load raw frames once (no scaling yet)
            frames = []
            for i in range(1, 8):
                img = load_image(f"assets/explosion{i}.png").convert_alpha()
                frames.append(img)
            Explosion._original_frames = frames
        # Scale each frame to the requested size for this instance
        self.frames = [pygame.transform.scale(img, (size, size)) for img in Explosion._original_frames]
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        # Position the explosion at the centre of the dead entity
        self.rect = self.image.get_rect(center=(x, y))
        # Velocity for a short drifting trail (default upward)
        self.velocity = velocity
        # Animation timing – advance every few ticks (adjustable)
        self.animation_timer = 0
        self.animation_delay = 2  # faster animation

    def update(self):
        # Apply drifting movement each tick
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # Increment timer and advance frame when delay is reached
        self.animation_timer += 1
        if self.animation_timer >= self.animation_delay:
            self.animation_timer = 0
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                # End of animation – remove sprite
                self.kill()
                return
            self.image = self.frames[self.current_frame]

class BunkerRespawnEffect(pygame.sprite.Sprite):
    """Spezielle Animation für das Respawnen der Bunker."""
    
    _frames = None

    def __init__(self, x: int, y: int, size: int = 128):
        super().__init__()
        if BunkerRespawnEffect._frames is None:
            frames = []
            for i in range(1, 9): # Lädt frame1 bis frame8
                img = load_image(f"assets/lightning_skill6_frame{i}.png").convert_alpha()
                frames.append(img)
            BunkerRespawnEffect._frames = frames
            
        # Skaliere die Animationsframes (z.B. auf 128x128, damit der Blitz den Bunker schön umschließt)
        self.frames = [pygame.transform.scale(img, (size, size)) for img in BunkerRespawnEffect._frames]
        
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        
        # Etwas langsamere Animation, damit man den Blitz gut sieht
        self.animation_timer = 0
        self.animation_delay = 3 

    def update(self):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_delay:
            self.animation_timer = 0
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.kill() # Animation beendet -> Sprite löschen
                return
            self.image = self.frames[self.current_frame]