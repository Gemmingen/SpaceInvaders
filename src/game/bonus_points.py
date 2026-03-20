import pygame
from src.utils.helpers import load_image

class BonusPointItem(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, points):
        super().__init__()
        self.points = points
        self.speed = speed
        
        try:
            # Bild laden basierend auf den Punkten
            raw_image = load_image(f'assets/bonus-points{self.points}.png').convert_alpha()
            # Proportionale Skalierung auf 94x94
            self.image = pygame.transform.scale(raw_image, (94, 94)) 
        except Exception:
            # Fallback
            self.image = pygame.Surface((94, 94), pygame.SRCALPHA)
            self.image.fill((255, 255, 0))
            
        self.rect = self.image.get_rect(center=(x, y))
        self.exact_y = float(self.rect.y)

    def update(self, *args, **kwargs):
        # Fällt konstant nach unten
        self.exact_y += self.speed
        self.rect.y = int(self.exact_y)
        
        if self.rect.top > 1500:
            self.kill()


# --- NEU: Der visuelle Effekt beim Einsammeln ---
class CollectEffect(pygame.sprite.Sprite):
    _frames = None # Wir cachen die Bilder, damit die Festplatte geschont wird

    def __init__(self, x, y, size=(94, 94), animation_speed=0.4):
        super().__init__()
        
        if CollectEffect._frames is None:
            CollectEffect._frames = []
            for i in range(1, 6): # collect1.png bis collect5.png
                try:
                    img = load_image(f'assets/collect{i}.png').convert_alpha()
                    img = pygame.transform.scale(img, size)
                    CollectEffect._frames.append(img)
                except Exception:
                    pass
            
            # Notfall-Fallback falls Bilder fehlen
            if not CollectEffect._frames:
                surf = pygame.Surface(size, pygame.SRCALPHA)
                CollectEffect._frames.append(surf)

        self.frames = CollectEffect._frames
        self.current_frame = 0.0
        self.animation_speed = animation_speed
        
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, *args, **kwargs):
        self.current_frame += self.animation_speed
        
        frame_index = int(self.current_frame)
        if frame_index >= len(self.frames):
            self.kill() # Animation fertig -> Löschen
        else:
            self.image = self.frames[frame_index]