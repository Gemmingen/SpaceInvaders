import pygame
from src.config.config import FPS, SCREEN_WIDTH, SCREEN_HEIGHT

class MainMenu:
    def __init__(self, font, background_image):
        self.font = font
        self.background = background_image
        self.title_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 40)
        
    def draw(self, surface):
        self.clock(FPS)
        surface.blit(self.background, (0, 0))
        
        # Ein halbtransparentes Overlay, damit der Text besser lesbar ist
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) # Schwarz mit 150 Alpha
        surface.blit(overlay, (0, 0))

        # Titel rendern
        title_surf = self.title_font.render("SPACE INVADERS", True, (0, 255, 0))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        
        # Blink-Effekt für den "Press Enter"-Text
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            prompt_surf = self.font.render("PRESS ENTER TO START", True, (255, 255, 255))
            prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            surface.blit(prompt_surf, prompt_rect)

        surface.blit(title_surf, title_rect)