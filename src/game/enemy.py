import pygame
from src.config.config import ENEMY_SPEED
from src.game.bullet import Bullet
from src.utils.helpers import load_image

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, row):
        super().__init__()
        
        # Bestimme den Sprite anhand der Reihe (1 bis 7)
        enemy_type = (row % 7) + 1
        sheet = load_image(f"assets/enemy{enemy_type}.png").convert_alpha()
        
        # Frame 1 (obere 8x8 Pixel)
        frame1 = pygame.Surface((8, 8), pygame.SRCALPHA)
        frame1.blit(sheet, (0, 0), (0, 0, 8, 8))
        
        # Frame 2 (untere 8x8 Pixel)
        frame2 = pygame.Surface((8, 8), pygame.SRCALPHA)
        frame2.blit(sheet, (0, 0), (0, 8, 8, 8))
        
        # Frames skalieren auf 32x32
        self.frames = [
            pygame.transform.scale(frame1, (32, 32)),
            pygame.transform.scale(frame2, (32, 32))
        ]
        
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = ENEMY_SPEED
        
        # Animationstimer
        self.animation_timer = 0
        self.animation_delay = 30  # Alle 30 Ticks wird der Frame gewechselt
    
    def move(self, direction):
        self.rect.x += direction * self.speed
        
    def update(self):
        # Wechsle das Animations-Frame basierend auf dem Timer
        self.animation_timer += 1
        if self.animation_timer >= self.animation_delay:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
    
    def shoot(self):
        # Enemy bullet shoots downward
        bullet = Bullet(self.rect.centerx, self.rect.bottom, direction=1)
        return bullet