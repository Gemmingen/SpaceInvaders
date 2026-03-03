import pygame
import random
import math
from src.utils.helpers import load_image

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, powerup_type):
        super().__init__()
        self.type = powerup_type
        
        # Weist jedem Typen sein passendes Bild zu
        images = {
            "comet": "assets/powerup-comet.png",
            "bunker": "assets/powerup-bunker.png",
            "hp": "assets/powerup-hp.png",
            "speed": "assets/powerup-speed.png",
            "doubleshot": "assets/powerup-doubleshot.png",
            "trippleshot": "assets/powerup-trippleshot.png"
        }
        
        img = load_image(images[self.type]).convert_alpha()
        self.image = pygame.transform.scale(img, (96, 96))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self, screen_height, *args, **kwargs):
        self.rect.y += self.speed
        if self.rect.top > screen_height:
            self.kill()


class Comet(pygame.sprite.Sprite):
    def __init__(self, screen_width, normal_speed, normal_rotation_speed, tie_speed, tie_rotation_speed, tie_size):
        super().__init__()
        
        # 1 zu 10 Chance für das Easter Egg (10%)
        is_tie_fighter = random.randint(1, 20) == 1
        
        if is_tie_fighter:
            # Easter Egg: Tie-Fighter laden und spezielle Werte setzen
            img = load_image("assets/comet-tie-fighter.png").convert_alpha()
            self.speed = tie_speed
            self.rotation_speed = tie_rotation_speed
            size = (tie_size, tie_size)
        else:
            # Normaler Komet
            comet_images = ["assets/comet-big.png", "assets/comet-big2.png"]
            img = load_image(random.choice(comet_images)).convert_alpha()
            self.speed = normal_speed
            self.rotation_speed = normal_rotation_speed
            size = (80, 80)
            
        # Originalbild mit der ausgewählten Größe speichern
        self.original_image = pygame.transform.scale(img, size)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        
        self.angle = 0

        # Zufällig entscheiden: Kommt er von Links-Oben oder Rechts-Oben?
        if random.choice([True, False]):
            # Start: Links oben -> Flugrichtung: Rechts unten
            self.rect.bottomright = (0, 0)
            self.dir_x = 1
            self.dir_y = 1
        else:
            # Start: Rechts oben -> Flugrichtung: Links unten
            self.rect.bottomleft = (screen_width, 0)
            self.dir_x = -1
            self.dir_y = 1

        # Vektor normalisieren, damit die Geschwindigkeit diagonal exakt stimmt
        length = math.hypot(self.dir_x, self.dir_y)
        self.vel_x = (self.dir_x / length) * self.speed
        self.vel_y = (self.dir_y / length) * self.speed

        # Zentrum als Float speichern (gegen das Wackeln beim Rotieren)
        self.exact_center_x = float(self.rect.centerx)
        self.exact_center_y = float(self.rect.centery)

    def update(self, screen_width, screen_height, *args, **kwargs):
        # 1. Leichte Eigendrehung berechnen
        self.angle = (self.angle + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)

        # 2. Exaktes Zentrum bewegen
        self.exact_center_x += self.vel_x
        self.exact_center_y += self.vel_y

        # 3. Das Rect neu holen und das ZENTRUM auf unsere Float-Werte setzen
        self.rect = self.image.get_rect(center=(int(self.exact_center_x), int(self.exact_center_y)))

        # 4. Despawn, wenn der Komet den Bildschirm komplett verlassen hat
        if self.rect.top > screen_height or self.rect.left > screen_width or self.rect.right < 0:
            self.kill()