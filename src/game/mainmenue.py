import pygame
import json
import os
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT

class MainMenu:
    def __init__(self, font):
        self.font = font
        self.title_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 40)
        self.score_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 15)
        
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180)) 

    def load_top_scores(self, mode="story"):
        # EXAKT die gleiche Pfad-Logik wie in game.py verwenden!
        base_path = os.path.dirname(os.path.abspath(__file__))
        root_path = os.path.dirname(os.path.dirname(base_path))
        filename = os.path.join(root_path, "highsscores.json")
        
        if os.path.exists(filename):
            with open(filename, "r") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict):
                        scores = data.get(mode, [])
                    else:
                        scores = []
                    scores.sort(key=lambda x: x["score"], reverse=True)
                    return scores[:3] # Top 3 anzeigen
                except:
                    return []
        return []

    def draw(self, surface):
        surface.blit(self.overlay, (0, 0))

        # Titel
        title_surf = self.title_font.render("SPACE INVADERS", True, (0, 255, 0))
        surface.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 120)))
        
        # Start-Prompt
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            prompt_surf = self.font.render("PRESS 1: STORY   2: ENDLESS", True, (255, 255, 255))
            surface.blit(prompt_surf, prompt_rect := prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, 220)))

        # --- SCOREBOARD ZEICHNEN ---
        # Story Mode Scores
        header_surf = self.score_font.render("--- TOP 3 STORY PILOTS ---", True, (255, 215, 0))
        surface.blit(header_surf, header_surf.get_rect(center=(SCREEN_WIDTH // 2, 300)))

        scores = self.load_top_scores("story")
        if not scores:
            no_score = self.score_font.render("NO RECORDS YET", True, (100, 100, 100))
            surface.blit(no_score, no_score.get_rect(center=(SCREEN_WIDTH // 2, 360)))
        else:
            for i, entry in enumerate(scores):
                color = (255, 255, 255)
                if i == 0: color = (255, 215, 0) # Gold für Platz 1
                
                txt = f"{i+1}. {entry['name']} - {entry['score']}"
                s_surf = self.score_font.render(txt, True, color)
                surface.blit(s_surf, s_surf.get_rect(center=(SCREEN_WIDTH // 2, 350 + (i * 35))))

        # Endless Mode Scores
        endless_header_surf = self.score_font.render("--- TOP 3 ENDLESS PILOTS ---", True, (0, 200, 255))
        surface.blit(endless_header_surf, endless_header_surf.get_rect(center=(SCREEN_WIDTH // 2, 520)))

        endless_scores = self.load_top_scores("endless")
        if not endless_scores:
            no_endless_score = self.score_font.render("NO RECORDS YET", True, (100, 100, 100))
            surface.blit(no_endless_score, no_endless_score.get_rect(center=(SCREEN_WIDTH // 2, 580)))
        else:
            for i, entry in enumerate(endless_scores):
                color = (255, 255, 255)
                if i == 0: color = (0, 200, 255) # Blau für Platz 1
                
                wave_info = f" W{entry.get('wave', 1)}" if 'wave' in entry else ""
                txt = f"{i+1}. {entry['name']} - {entry['score']}{wave_info}"
                s_surf = self.score_font.render(txt, True, color)
                surface.blit(s_surf, s_surf.get_rect(center=(SCREEN_WIDTH // 2, 570 + (i * 35))))