import pygame
import json
import os
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT

class MainMenu:
    def __init__(self, font):
        self.font = font
        self.title_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 40)
        self.score_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 15)
        self.credits_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 25)
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180)) 

    def load_top_scores(self, filename="highscores_sp.json", mode="story"):
        """Loads the top 3 scores from the specified JSON file and mode."""
        base_path = os.path.dirname(os.path.abspath(__file__))
        root_path = os.path.dirname(os.path.dirname(base_path))
        filepath = os.path.join(root_path, filename)
        
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
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
        
        # Start-Prompt updated for SP and MP
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            prompt_surf1 = self.font.render("1:SP STORY    2:SP ENDLESS", True, (255, 255, 255))
            prompt_surf2 = self.font.render("3:MP STORY    4:MP ENDLESS", True, (255, 255, 255))
            surface.blit(prompt_surf1, prompt_surf1.get_rect(center=(SCREEN_WIDTH // 2, 200)))
            surface.blit(prompt_surf2, prompt_surf2.get_rect(center=(SCREEN_WIDTH // 2, 230)))

        # Helper function to draw leaderboards
        def render_leaderboard(title, filename, y_start, color, highlight_color):
            header = self.score_font.render(title, True, highlight_color)
            surface.blit(header, header.get_rect(center=(SCREEN_WIDTH // 2, y_start)))
            scores = self.load_top_scores(filename, "story")
            
            if not scores:
                no_score = self.score_font.render("NO RECORDS YET", True, (100, 100, 100))
                surface.blit(no_score, no_score.get_rect(center=(SCREEN_WIDTH // 2, y_start + 40)))
            else:
                for i, entry in enumerate(scores[:3]):
                    c = highlight_color if i == 0 else color
                    
                    # If endless mode was played, optionally show wave info (kept for compatibility)
                    wave_info = f" W{entry.get('wave', 1)}" if 'wave' in entry else ""
                    txt = f"{i+1}. {entry['name']} - {entry['score']}{wave_info}"
                    
                    s_surf = self.score_font.render(txt, True, c)
                    surface.blit(s_surf, s_surf.get_rect(center=(SCREEN_WIDTH // 2, y_start + 50 + (i * 35))))

        # Draw the leaderboards
        render_leaderboard("--- TOP SP PILOTS ---", "highscores_sp.json", 310, (255, 255, 255), (255, 215, 0))
        render_leaderboard("--- TOP MP SQUADS ---", "highscores_mp.json", 520, (255, 255, 255), (0, 200, 255))

        # Credits
        credits = self.credits_font.render("--- GAME MADE BY ---", True, (255, 215, 0))
        surface.blit(credits, credits.get_rect(center=(SCREEN_WIDTH // 2, 800)))
        credit_names = ["Macid Askar", "Santino Brauch", "Louis Edwell"]
        for i, name in enumerate(credit_names):
            name_surf = self.credits_font.render(name, True, (192, 192, 192))
            surface.blit(name_surf, name_surf.get_rect(center=(SCREEN_WIDTH // 2, 840 + (i * 30))))