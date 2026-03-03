import pygame
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT

class MainMenu:
    def __init__(self, font, background_image):
        self.font = font
        self.background = background_image
        self.title_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 40)
        
        # Performance: Overlay einmalig erstellen statt in jedem Frame
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 150)) 
        
    def draw(self, surface):
        # 1. Hintergrund zeichnen
        surface.blit(self.background, (0, 0))
        surface.blit(self.overlay, (0, 0))

        # 2. Titel rendern
        title_surf = self.title_font.render("SPACE INVADERS", True, (0, 255, 0))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        surface.blit(title_surf, title_rect)
        
        # 3. Blink-Logik (Automatisch basierend auf der Zeit)
        # get_ticks() zählt Millisekunden seit Programmstart. 
        # // 500 bedeutet: Alle 0.5 Sekunden wechselt der Wert zwischen gerade/ungerade
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            prompt_surf = self.font.render("PRESS ENTER TO START", True, (255, 255, 255))
            prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            surface.blit(prompt_surf, prompt_rect)