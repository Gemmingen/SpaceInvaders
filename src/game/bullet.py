import pygame
from src.config.config import BULLET_SPEED
from src.utils.helpers import load_image

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=-1):
        super().__init__()
        # Load the player attack sprite and scale to a suitable bullet size (8x8)
        self.image = pygame.transform.scale(
            load_image("assets/player-attack-single.png").convert_alpha(), (32, 32)
        )
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = BULLET_SPEED * direction  # direction: -1 up, 1 down
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
