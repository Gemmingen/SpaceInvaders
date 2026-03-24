import pygame
import json
import os
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT

class MainMenu:
    def __init__(self, font):
        self.font = font
        self.title_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 45)
        self.score_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 18)
        self.sub_title_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 25)
        self.credits_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 12)
        
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 210)) 
        
        self.state = "MAIN"
        self.selection = 0
        
        # --- Nahtlose Wasserfall Logik ---
        self.scroll_y = 0
        self.scroll_speed = 1.2
        self.line_height = 50 
        
        # Kategorien mit vollen Namen und Farben
        self.categories = [
            {"label": "TOP 5 - SINGLEPLAYER STORY", "file": "highscores_sp.json", "key": "sp_story", "color": (255, 255, 0)}, # Gelb
            {"label": "TOP 5 - SINGLEPLAYER ENDLESS", "file": "highscores_sp.json", "key": "sp_endless", "color": (255, 255, 0)}, # Gelb
            {"label": "TOP 5 - MULTIPLAYER STORY", "file": "highscores_mp.json", "key": "mp_story", "color": (0, 191, 255)}, # Blau
            {"label": "TOP 5 - MULTIPLAYER ENDLESS", "file": "highscores_mp.json", "key": "mp_endless", "color": (0, 191, 255)}, # Blau
            {"label": "TOP 5 - MULTIPLAYER VERSUS", "file": "highscores_mp.json", "key": "mp_versus", "color": (255, 0, 0)} # Rot
        ]
        
        self.all_category_data = []
        self.refresh_all_scores()

    def refresh_all_scores(self):
        self.all_category_data = []
        for cat in self.categories:
            data = self._get_raw_scores(cat["file"])
            entries = sorted(data.get(cat["key"], []), key=lambda x: x.get("score", 0), reverse=True)[:5]
            
            lines = [(f"--- {cat['label']} ---", cat["color"])]
            if not entries:
                lines.append(("NO RECORDS YET", (150, 150, 150)))
            else:
                for i, e in enumerate(entries):
                    lines.append((f"{i+1}. {e.get('name', '???').upper()} - {e.get('score', 0)}", (255, 255, 255)))
            lines.append(("", (0, 0, 0))) 
            self.all_category_data.append(lines)

    def _get_raw_scores(self, filename):
        base_path = os.path.dirname(os.path.abspath(__file__))
        root_path = os.path.dirname(os.path.dirname(base_path))
        filepath = os.path.join(root_path, filename)
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                try: return json.load(f)
                except: return {}
        return {}

    def draw(self, surface, selected_index=0):
        self.selection = selected_index
        surface.blit(self.overlay, (0, 0))

        title_surf = self.title_font.render("SPACE INVADERS", True, (0, 255, 0))
        surface.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80)))

        if self.state == "MAIN":
            self._draw_seamless_waterfall(surface, 480, view_height=350) 
            self._draw_pure_buttons(surface, ["SINGLEPLAYER", "MULTIPLAYER"], 280, width=650, height=90)
            
        elif self.state == "SINGLEPLAYER":
            sub_title = self.sub_title_font.render("SINGLEPLAYER", True, (255, 255, 0))
            surface.blit(sub_title, sub_title.get_rect(center=(SCREEN_WIDTH // 2, 180)))
            self._draw_pure_buttons(surface, ["STORY MODE", "ENDLESS MODE", "BACK"], 280, width=500, height=65)
            self._draw_side_leaderboards(surface, "sp_story", "sp_endless", "STORY", "ENDLESS", "highscores_sp.json", (255, 255, 0))

        elif self.state == "MULTIPLAYER":
            sub_title = self.sub_title_font.render("MULTIPLAYER", True, (0, 191, 255))
            surface.blit(sub_title, sub_title.get_rect(center=(SCREEN_WIDTH // 2, 180)))
            self._draw_pure_buttons(surface, ["STORY (CO-OP)", "ENDLESS (CO-OP)", "VERSUS", "BACK"], 260, width=550, height=65)
            self._draw_mp_leaderboards(surface)

        self._draw_credits(surface)

    def _draw_seamless_waterfall(self, surface, start_y, view_height):
        waterfall_surf = pygame.Surface((SCREEN_WIDTH, view_height), pygame.SRCALPHA)
        flat_list = [line for cat in self.all_category_data for line in cat]
        total_height = len(flat_list) * self.line_height
        
        self.scroll_y -= self.scroll_speed
        if self.scroll_y <= -total_height:
            self.scroll_y = 0

        for offset in [0, total_height]:
            for i, (text, color) in enumerate(flat_list):
                y_pos = self.scroll_y + (i * self.line_height) + offset
                if -50 < y_pos < view_height + 50:
                    if text:
                        txt_surf = self.score_font.render(text, True, color)
                        rect = txt_surf.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
                        waterfall_surf.blit(txt_surf, rect)
        
        surface.blit(waterfall_surf, (0, start_y))

    def _draw_pure_buttons(self, surface, options, start_y, width, height):
        for i, text in enumerate(options):
            is_selected = (i == self.selection)
            rect = pygame.Rect(0, 0, width, height)
            rect.center = (SCREEN_WIDTH // 2, start_y + (i * (height + 30)))

            pygame.draw.rect(surface, (0, 0, 0), rect)

            if is_selected:
                pygame.draw.rect(surface, (0, 255, 0), rect, 4)

            txt_color = (0, 255, 0) if is_selected else (255, 255, 255)
            txt_surf = self.font.render(text, True, txt_color)
            txt_rect = txt_surf.get_rect(center=rect.center)
            surface.blit(txt_surf, txt_rect)

    def _draw_side_leaderboards(self, surface, key1, key2, label1, label2, file, color):
        small_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 14)
        self._render_leaderboard(surface, f"TOP 5 {label1}", file, key1, 580, SCREEN_WIDTH // 4, small_font, color)
        self._render_leaderboard(surface, f"TOP 5 {label2}", file, key2, 580, (SCREEN_WIDTH * 3) // 4, small_font, color)

    def _draw_mp_leaderboards(self, surface):
        """Zeigt drei Scoreboards nebeneinander für den Multiplayer-Screen."""
        small_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 12)
        y_pos = 620
        
        # Story Co-Op (Blau)
        self._render_leaderboard(surface, "TOP 5 STORY", "highscores_mp.json", "mp_story", 
                                 y_pos, SCREEN_WIDTH // 6, small_font, (0, 191, 255))
        
        # Endless Co-Op (Blau)
        self._render_leaderboard(surface, "TOP 5 ENDLESS", "highscores_mp.json", "mp_endless", 
                                 y_pos, SCREEN_WIDTH // 2, small_font, (0, 191, 255))
        
        # Versus (Rot)
        self._render_leaderboard(surface, "TOP 5 VERSUS", "highscores_mp.json", "mp_versus", 
                                 y_pos, (SCREEN_WIDTH // 6) * 5, small_font, (255, 0, 0))

    def _render_leaderboard(self, surface, title, filename, mode_key, y_start, x_pos, font, color):
        header = font.render(title, True, color)
        surface.blit(header, header.get_rect(center=(x_pos, y_start)))
        scores = self.load_top_scores(filename, mode_key)
        
        if not scores:
            txt = font.render("EMPTY", True, (100, 100, 100))
            surface.blit(txt, txt.get_rect(center=(x_pos, y_start + 40)))
        else:
            for i, entry in enumerate(scores):
                name = entry.get('name', '???')[:8]
                points = entry.get('score', 0)
                txt = f"{i+1}.{name}-{points}"
                s_surf = font.render(txt, True, (255, 255, 255))
                surface.blit(s_surf, s_surf.get_rect(center=(x_pos, y_start + 40 + (i * 25))))

    def load_top_scores(self, filename, mode_key):
        data = self._get_raw_scores(filename)
        res = data.get(mode_key, [])
        return sorted(res, key=lambda x: x.get("score", 0), reverse=True)[:5]

    def _draw_credits(self, surface):
        y = SCREEN_HEIGHT - 40
        credits_title = self.credits_font.render("DEVELOPED BY", True, (150, 150, 150))
        surface.blit(credits_title, credits_title.get_rect(center=(SCREEN_WIDTH // 2, y)))
        names = "Macid Askar  •  Santino Brauch  •  Louis Edwell"
        name_surf = self.credits_font.render(names, True, (100, 100, 100))
        surface.blit(name_surf, name_surf.get_rect(center=(SCREEN_WIDTH // 2, y + 20)))
