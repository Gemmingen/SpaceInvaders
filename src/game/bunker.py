import pygame

class Bunker(pygame.sprite.Sprite):
    def __init__(self, x, y, size=3):
        super().__init__()
        # 1. Create a Surface with per-pixel alpha transparency (SRCALPHA)
        # Width/Height can be adjusted; 50x40 is a good starting block size
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        
        # 2. Fill it with the classic bunker green (RGB: 8, 136, 23)
        self.image.fill((8, 136, 23))
        
        # Optional: To get the specific notch shape of the original bunkers,
        # you can manually clear parts of the surface here:
        # pygame.draw.rect(self.image, (0, 0, 0, 0), ) # Notch example
        
        # 3. Set the position Rect
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # 4. Generate the bitmask for pixel-perfect collision detection
        # This must be done AFTER drawing the initial shape
        self.mask = pygame.mask.from_surface(self.image)
    
    