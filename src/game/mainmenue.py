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

    def load_top_scores(self, filename, mode_key):
        base_path = os.path.dirname(os.path.abspath(__file__))
        root_path = os.path.dirname(os.path.dirname(base_path))
        filepath = os.path.join(root_path, filename)
        
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict):
                        scores = data.get(mode_key, [])
                    else:
                        scores = []
                    scores.sort(key=lambda x: x["score"], reverse=True)
                    return scores[:5]
                except:
                    return []
        return []

    def draw(self, surface, selected_index=0):
        surface.blit(self.overlay, (0, 0))

        title_surf = self.title_font.render("SPACE INVADERS", True, (0, 255, 0))
        surface.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100)))
        
        # --- Interactive Gamemode Selection Boxes ---
        options = ["SP STORY", "SP ENDLESS", "MP STORY", "MP ENDLESS", "MP VERSUS"]
        box_width = 180
        box_height = 35
        
        # Grid positions for the boxes
        positions = [
            (SCREEN_WIDTH // 2 - 110, 160), # 0: SP STORY
            (SCREEN_WIDTH // 2 + 110, 160), # 1: SP ENDLESS
            (SCREEN_WIDTH // 2 - 110, 210), # 2: MP STORY
            (SCREEN_WIDTH // 2 + 110, 210), # 3: MP ENDLESS
            (SCREEN_WIDTH // 2, 260)        # 4: MP VERSUS
        ]
        
        for i, text in enumerate(options):
            rect = pygame.Rect(0, 0, box_width, box_height)
            rect.center = positions[i]
            
            if i == selected_index:
                # Highlighted Box
                color = (0, 255, 0)
                border_thickness = 3
                fill_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
                fill_surf.fill((0, 255, 0, 40))  # Light green transparent fill
                surface.blit(fill_surf, rect.topleft)
            else:
                # Normal Box
                color = (255, 255, 255)
                border_thickness = 1
                
            pygame.draw.rect(surface, color, rect, border_thickness)
            text_surf = self.font.render(text, True, color)
            surface.blit(text_surf, text_surf.get_rect(center=rect.center))
        # --------------------------------------------

        def render_leaderboard(title, filename, mode_key, y_start, color, highlight_color, x_pos):
            header = self.score_font.render(title, True, highlight_color)
            surface.blit(header, header.get_rect(center=(x_pos, y_start)))
            scores = self.load_top_scores(filename, mode_key)
            
            if not scores:
                no_score = self.score_font.render("NO RECORDS YET", True, (100, 100, 100))
                surface.blit(no_score, no_score.get_rect(center=(x_pos, y_start + 40)))
            else:
                for i, entry in enumerate(scores[:5]):
                    c = highlight_color if i == 0 else color
                    
                    wave_info = f" W{entry.get('wave', 1)}" if 'wave' in entry else ""
                    txt = f"{i+1}. {entry.get('name', 'Unknown')} - {entry.get('score', 0)}{wave_info}"
                    
                    s_surf = self.font.render(txt, True, c)
                    surface.blit(s_surf, s_surf.get_rect(center=(x_pos, y_start + 45 + (i * 22))))

        render_leaderboard("SP STORY", "highscores_sp.json", "sp_story", 320, (255, 255, 255), (255, 215, 0), SCREEN_WIDTH // 4)
        render_leaderboard("SP ENDLESS", "highscores_sp.json", "sp_endless", 320, (255, 255, 255), (255, 215, 0), (SCREEN_WIDTH * 3) // 4)
        
        render_leaderboard("MP STORY", "highscores_mp.json", "mp_story", 480, (255, 255, 255), (0, 200, 255), SCREEN_WIDTH // 4)
        render_leaderboard("MP ENDLESS", "highscores_mp.json", "mp_endless", 480, (255, 255, 255), (0, 200, 255), (SCREEN_WIDTH * 3) // 4)
        
        render_leaderboard("MP VERSUS", "highscores_mp.json", "mp_versus", 640, (255, 255, 255), (255, 50, 50), SCREEN_WIDTH // 2)

        credits = self.credits_font.render("--- GAME MADE BY ---", True, (255, 215, 0))
        surface.blit(credits, credits.get_rect(center=(SCREEN_WIDTH // 2, 840)))
        credit_names = ["Macid Askar", "Santino Brauch", "Louis Edwell"]
        for i, name in enumerate(credit_names):
            name_surf = self.credits_font.render(name, True, (192, 192, 192))
            surface.blit(name_surf, name_surf.get_rect(center=(SCREEN_WIDTH // 2, 880 + (i * 30))))