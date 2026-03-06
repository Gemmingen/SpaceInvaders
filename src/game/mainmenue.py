import pygame
import json
import os
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT

class MainMenu:
    def __init__(self, font, background_image):
        self.font = font
        self.background = background_image
        self.title_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 40)
        self.score_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 15)
        
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180)) 

    def load_top_scores(self):
        # EXAKT die gleiche Pfad-Logik wie in game.py verwenden!
        base_path = os.path.dirname(os.path.abspath(__file__))
        root_path = os.path.dirname(os.path.dirname(base_path))
        filename = os.path.join(root_path, "highsscores.json")
        
        if os.path.exists(filename):
            with open(filename, "r") as f:
                try:
                    data = json.load(f)
                    data.sort(key=lambda x: x["score"], reverse=True)
                    return data[:3] # Top 3 anzeigen
                except:
                    return []
        return []

    def draw(self, surface):
        surface.blit(self.background, (0, 0))
        surface.blit(self.overlay, (0, 0))

        # Titel
        title_surf = self.title_font.render("SPACE INVADERS", True, (0, 255, 0))
        surface.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 120)))
        
        # Start-Prompt
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            prompt_surf = self.font.render("PRESS ENTER TO START", True, (255, 255, 255))
            surface.blit(prompt_surf, prompt_rect := prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, 220)))

        # --- SCOREBOARD ZEICHNEN ---
        header_surf = self.score_font.render("--- TOP 3 STORY PILOTS ---", True, (255, 215, 0))
        surface.blit(header_surf, header_surf.get_rect(center=(SCREEN_WIDTH // 2, 350)))

        scores = self.load_top_scores()
        if not scores:
            no_score = self.score_font.render("NO RECORDS YET", True, (100, 100, 100))
            surface.blit(no_score, no_score.get_rect(center=(SCREEN_WIDTH // 2, 420)))
        else:
            for i, entry in enumerate(scores):
                color = (255, 255, 255)
                if i == 0: color = (255, 215, 0) # Gold für Platz 1
                
                txt = f"{i+1}. {entry['name']} - {entry['score']}"
                s_surf = self.score_font.render(txt, True, color)
                surface.blit(s_surf, s_surf.get_rect(center=(SCREEN_WIDTH // 2, 410 + (i * 45))))