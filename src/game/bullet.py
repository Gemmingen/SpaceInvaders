import pygame
from src.config.config import BULLET_SPEED
from src.utils.helpers import load_image

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=-1, bullet_type="single"):
        super().__init__()
        self.pierce = 1  # Wie viele Gegner getroffen werden können (default)
        # Enemy bullets should be able to pass through at least one bunker before being destroyed
        if direction == 1:
            self.pierce = 1
        
        if direction == 1:
            img_path = "assets/enemy-attack-small1.png"
            size = (12, 12)
        else:
            if bullet_type == "double":
                img_path = "assets/player-attack-double.png"
                size = (32, 32) 
                self.pierce = 2
            elif bullet_type == "triple":
                img_path = "assets/player-attack-tripple.png"
                size = (32, 32) 
                self.pierce = 3
            else:
                img_path = "assets/player-attack-single.png"
                size = (32, 32)
                
        self.image = pygame.transform.scale(load_image(img_path).convert_alpha(), size)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = BULLET_SPEED * direction
        self.direction = direction
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.y += self.speed
        # Remove bullet if it goes off-screen
        if (
            self.rect.bottom < 0
            or self.rect.top > pygame.display.get_surface().get_height()
        ):
            self.kill()
