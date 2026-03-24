import pygame
import json
import os

class MainMenu:
    def __init__(self, font):
        self.font = font
        self.title_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 65)
        self.button_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 24)
        self.sub_title_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 35)
        
        self.credits_title_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 24)
        self.credits_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 18)
        
        self.COLOR_GOLD = (255, 215, 0)
        self.COLOR_SILVER = (192, 192, 192)
        
        self.state = "MAIN"
        self.selection = 0

        self.overlay = pygame.Surface((1920, 1080), pygame.SRCALPHA) 
        self.overlay_alpha = 150 

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
        sw = surface.get_width()
        sh = surface.get_height()

        # Overlay zeichnen
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.overlay_alpha)) 
        surface.blit(overlay, (0, 0))

        # --- HAUPTTITEL ---
        title_surf = self.title_font.render("SPACE INVADERS", True, (0, 255, 0))
        surface.blit(title_surf, title_surf.get_rect(center=(sw // 2, 120)))

        if self.state == "MAIN":
            self._draw_main_leaderboards(surface, sw)
            self._draw_pure_buttons(surface, ["SINGLEPLAYER", "MULTIPLAYER"], 400, sw, width=450, height=75)
            
        elif self.state == "SINGLEPLAYER":
            sub_title = self.sub_title_font.render("SINGLEPLAYER", True, (255, 255, 0))
            surface.blit(sub_title, sub_title.get_rect(center=(sw // 2, 220)))
            self._draw_pure_buttons(surface, ["STORY MODE", "ENDLESS MODE", "BACK"], 350, sw, width=450, height=65)
            self._draw_side_leaderboards(surface, "sp_story", "sp_endless", "STORY", "ENDLESS", "highscores_sp.json", (255, 255, 0), sw)

        elif self.state == "MULTIPLAYER":
            sub_title = self.sub_title_font.render("MULTIPLAYER", True, (0, 191, 255))
            surface.blit(sub_title, sub_title.get_rect(center=(sw // 2, 220)))
            self._draw_pure_buttons(surface, ["STORY (CO-OP)", "ENDLESS (CO-OP)", "VERSUS", "BACK"], 320, sw, width=500, height=65)
            self._draw_mp_leaderboards(surface, sw)

        self._draw_credits(surface, sw, sh)

    def _draw_main_leaderboards(self, surface, sw):
        small_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 16)
        
        # Fest definierte Säulen bei 20% und 80%
        left_x = sw // 5
        right_x = (sw * 4) // 5
        
        self._render_leaderboard(surface, "SP STORY", "highscores_sp.json", "sp_story", 280, left_x, small_font, (255, 255, 0))
        self._render_leaderboard(surface, "SP ENDLESS", "highscores_sp.json", "sp_endless", 560, left_x, small_font, (255, 255, 0))
        
        self._render_leaderboard(surface, "MP STORY", "highscores_mp.json", "mp_story", 280, right_x, small_font, (0, 191, 255))
        self._render_leaderboard(surface, "MP ENDLESS", "highscores_mp.json", "mp_endless", 560, right_x, small_font, (0, 191, 255))
        
        self._render_leaderboard(surface, "VERSUS", "highscores_mp.json", "mp_versus", 700, sw // 2, small_font, (255, 50, 50))

    def _draw_pure_buttons(self, surface, options, start_y, sw, width, height):
        for i, text in enumerate(options):
            is_selected = (i == self.selection)
            rect = pygame.Rect(0, 0, width, height)
            rect.center = (sw // 2, start_y + (i * (height + 30)))

            pygame.draw.rect(surface, (0, 0, 0), rect)

            if is_selected:
                pygame.draw.rect(surface, (0, 255, 0), rect, 6)
                display_text = f"> {text} <"
                txt_color = (0, 255, 0)
            else:
                pygame.draw.rect(surface, (100, 100, 100), rect, 2)
                display_text = text
                txt_color = (255, 255, 255)

            txt_surf = self.button_font.render(display_text, True, txt_color)
            txt_rect = txt_surf.get_rect(center=rect.center)
            surface.blit(txt_surf, txt_rect)

    def _draw_side_leaderboards(self, surface, key1, key2, label1, label2, file, color, sw):
        small_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 16)
        
        left_x = sw // 5
        right_x = (sw * 4) // 5
        
        # Auf Y=480 gesetzt, damit sie zentrierter und höher liegen
        self._render_leaderboard(surface, f"TOP 5 {label1}", file, key1, 480, left_x, small_font, color)
        self._render_leaderboard(surface, f"TOP 5 {label2}", file, key2, 480, right_x, small_font, color)

    def _draw_mp_leaderboards(self, surface, sw):
        small_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 16)
        
        left_x = sw // 5
        right_x = (sw * 4) // 5
        mid_x = sw // 2
        
        y_sides = 480  # Gleiche Höhe wie im Singleplayer
        y_bottom = 760 # Das Versus-Board sitzt tiefer unten in der Mitte
        
        self._render_leaderboard(surface, "TOP 5 STORY", "highscores_mp.json", "mp_story", 
                                 y_sides, left_x, small_font, (0, 191, 255))
        self._render_leaderboard(surface, "TOP 5 ENDLESS", "highscores_mp.json", "mp_endless", 
                                 y_sides, right_x, small_font, (0, 191, 255))
        self._render_leaderboard(surface, "TOP 5 VERSUS", "highscores_mp.json", "mp_versus", 
                                 y_bottom, mid_x, small_font, (255, 50, 50))

    def _render_leaderboard(self, surface, title, filename, mode_key, y_start, x_pos, font, color):
        header = font.render(title, True, color)
        surface.blit(header, header.get_rect(center=(x_pos, y_start)))
        scores = self.load_top_scores(filename, mode_key)
        
        if not scores:
            txt = font.render("EMPTY", True, (100, 100, 100))
            surface.blit(txt, txt.get_rect(center=(x_pos, y_start + 45)))
        else:
            for i, entry in enumerate(scores):
                name = entry.get('name', '???')[:8]
                points = entry.get('score', 0)
                txt = f"{i+1}.{name}-{points}"
                s_surf = font.render(txt, True, (255, 255, 255))
                surface.blit(s_surf, s_surf.get_rect(center=(x_pos, y_start + 45 + (i * 30))))

    def load_top_scores(self, filename, mode_key):
        data = self._get_raw_scores(filename)
        res = data.get(mode_key, [])
        return sorted(res, key=lambda x: x.get("score", 0), reverse=True)[:5]

    def _draw_credits(self, surface, sw, sh):
        y = sh - 90
        credits_title = self.credits_title_font.render("DEVELOPED BY SCHWARZ DIGITS", True, self.COLOR_GOLD)
        surface.blit(credits_title, credits_title.get_rect(center=(sw // 2, y)))
        
        names = "Macid Askar - Santino Brauch - Louis Edwell"
        name_surf = self.credits_font.render(names, True, self.COLOR_SILVER)
        surface.blit(name_surf, name_surf.get_rect(center=(sw // 2, y + 40)))