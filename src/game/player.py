import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        spritesheet = pygame.image.load("assets/pico8_invaders_sprites_LARGE.png").convert_alpha()

        rect_idle = pygame.Rect(0, 0, 32, 32)
        rect_left = pygame.Rect(32, 0, 32, 32)
        rect_right = pygame.Rect(64, 0, 32, 32)
        
        self.image_idle = spritesheet.subsurface(rect_idle)
        self.image_left = spritesheet.subsurface(rect_left)
        self.image_right = spritesheet.subsurface(rect_right)
        
        self.image = self.image_idle
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        self.image = self.image_idle
        
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.image = self.image_left
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.image = self.image_right
            
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        elif keys[pygame.K_DOWN]:
            self.rect.y += self.speed