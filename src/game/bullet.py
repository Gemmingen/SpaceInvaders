import pygame
from src.config.config import BULLET_SPEED
from src.utils.helpers import load_image

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=-1):
        super().__init__()
        # Load the player attack sprite and scale to a suitable bullet size (8x8)
# Choose bullet sprite based on direction (player vs enemy)
        if direction == 1:
            # Enemy bullet – use enemy attack graphic
            img_path = "assets/enemy-attack-small1.png"
        else:
            # Player bullet – original graphic
            img_path = "assets/player-attack-single.png"
        # Choose appropriate size: player bullets (32x32), enemy bullets smaller (12x12)
        if direction == 1:
            size = (12, 12)  # enemy bullet size
        else:
            size = (32, 32)  # player bullet size (original)
        self.image = pygame.transform.scale(
            load_image(img_path).convert_alpha(), size
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
