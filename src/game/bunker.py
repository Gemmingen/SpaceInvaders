import pygame
import random
from src.utils.helpers import load_image

class Bunker(pygame.sprite.Sprite):
    def __init__(self, x, y, variant="satellite", angle=0):
        """Create a bunker (satellite) sprite.

        Parameters
        ----------
        x, y: int
            Position of the bunker centre.
        variant: str, optional
            Prefix of the asset files to use. Accepted values are
            ``"satellite"``, ``"satellit2"``, ``"satellit3"`` and ``"satellit4"``.
            The function will attempt to load ``assets/<variant>-default.png``
            and the corresponding ``dmg1``/``dmg2`` images. If a file is missing
            it gracefully falls back to the original ``satellite`` set.
        angle: int, optional
            Rotation angle in degrees (default 0). Used to orient the bunkers
            around the screen.
        """
        super().__init__()
        
        # 1. Determine which sprite set to load (default satellite or variants)
        prefix = variant  # e.g. "satellite", "satellit2", "satellit3", "satellit4"
        def load_variant_image(name):
            """Load a variant image, falling back to the default satellite set if missing."""
            try:
                return load_image(f"assets/{prefix}-{name}.png").convert_alpha()
            except Exception:
                # fallback to original satellite images (always present)
                return load_image(f"assets/satellite-{name}.png").convert_alpha()
        
        base_default = load_variant_image("default")
        base_dmg1 = load_variant_image("dmg1")
        base_dmg2 = load_variant_image("dmg2")
        
        # 2. Skaliere sie etwas größer (z. B. auf 64x64)
        size = (96, 96)
        base_default = pygame.transform.scale(base_default, size)
        base_dmg1 = pygame.transform.scale(base_dmg1, size)
        base_dmg2 = pygame.transform.scale(base_dmg2, size)
        
        # 3. Rotiere die Bilder basierend auf dem übergebenen Winkel
        self.img_default = pygame.transform.rotate(base_default, angle)
        self.img_dmg1 = pygame.transform.rotate(base_dmg1, angle)
        self.img_dmg2 = pygame.transform.rotate(base_dmg2, angle)
        
        # Start-Setup
        self.current_base_image = self.img_default
        self.image = self.current_base_image.copy()
        
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        
        # Originalposition speichern, damit der Satellit nach dem Wackeln zurückkehrt
        self.base_x = self.rect.centerx
        self.base_y = self.rect.centery
        
        # Health-System: 15 HP insgesamt
        self.max_health = 15
        self.health = self.max_health
        
        # Timer für die visuellen Effekte
        self.shake_timer = 0
        self.flash_timer = 0

    def take_damage(self):
        self.health -= 1
        
        # Nur beim exakt 5. und 10. Treffer (Health fällt auf 10 bzw. 5) 
        # wechseln wir den Frame und lösen das Wackeln/Leuchten aus
        if self.health == 10:
            self.current_base_image = self.img_dmg1
            self.shake_timer = 12
            self.flash_timer = 12
        elif self.health == 5:
            self.current_base_image = self.img_dmg2
            self.shake_timer = 12
            self.flash_timer = 12
            
        # Aktualisiere die Kollisionsmaske nur, wenn sich das Bild geändert hat
        if self.health in (10, 5):
            self.mask = pygame.mask.from_surface(self.current_base_image)
        
        # Satellit zerstören, wenn HP auf 0 fällt
        if self.health <= 0:
            self.kill()

    def update(self):
        # 1. Rotes Aufleuchten (Flash) anwenden, falls aktiv
        drawn_image = self.current_base_image.copy()
        
        if self.flash_timer > 0:
            self.flash_timer -= 1
            # Fügt dem Bild einen roten Tint hinzu
            drawn_image.fill((150, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
            
        self.image = drawn_image
        
        # 2. Wackeln (Shake) anwenden, falls aktiv
        if self.shake_timer > 0:
            self.shake_timer -= 1
            offset_x = random.randint(-4, 4)
            offset_y = random.randint(-4, 4)
            self.rect.centerx = self.base_x + offset_x
            self.rect.centery = self.base_y + offset_y
        else:
            self.rect.centerx = self.base_x
            self.rect.centery = self.base_y