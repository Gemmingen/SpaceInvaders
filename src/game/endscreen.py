import pygame
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT

class EndScreen:
    def __init__(self, font):
        self.font = font
        self.title_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 50)
        self.key_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 20)
        self.keys = [
            ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
            ['H', 'I', 'J', 'K', 'L', 'M', 'N'],
            ['O', 'P', 'Q', 'R', 'S', 'T', 'U'],
            ['V', 'W', 'X', 'Y', 'Z', '<', 'OK']
        ]
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 220))

    def draw(self, surface, state, score, p1_name, p2_name, sel_p1, sel_p2, p1_done, p2_done, num_players=1, is_victory=False, game_mode="story", wave_number=1, score_p2=0, wave_p2=1):
        surface.blit(self.overlay, (0, 0))
        current_time = pygame.time.get_ticks()
        title_visible = (current_time // 800) % 2 == 0
        cursor_visible = (current_time // 250) % 2 == 0
        
        msg = "YOU WIN!" if is_victory else "GAME OVER"
        color = (0, 255, 0) if is_victory else (255, 50, 50)
        
        if is_victory or title_visible:
            title_surf = self.title_font.render(msg, True, color)
            surface.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 120)))

        if game_mode == "versus":
            score_txt = f"P1 W:{wave_number} S:{score} | P2 W:{wave_p2} S:{score_p2}"
        elif game_mode == "endless":
            score_txt = f"WAVE:{wave_number}  SCORE:{score}"
        else:
            score_txt = f"SCORE:{score}"
            
        score_surf = self.key_font.render(score_txt, True, (255, 215, 0))
        surface.blit(score_surf, score_surf.get_rect(center=(SCREEN_WIDTH // 2, 200)))

        # Draw virtual keyboards
        cursor = "_" if cursor_visible else " "
        
        if num_players == 1:
            self._draw_keyboard(surface, p1_name + (cursor if not p1_done else ""), sel_p1, p1_done, SCREEN_WIDTH // 2, "P1 (WASD/SPACE)")
        else:
            self._draw_keyboard(surface, p1_name + (cursor if not p1_done else ""), sel_p1, p1_done, SCREEN_WIDTH // 4, "P1 (WASD/SPACE)")
            self._draw_keyboard(surface, p2_name + (cursor if not p2_done else ""), sel_p2, p2_done, (SCREEN_WIDTH * 3) // 4, "P2 (ARROWS/NUM0)")

        footer_y = SCREEN_HEIGHT - 60
        r_surf = self.font.render("[R] RESTART", True, (120, 120, 120))
        q_surf = self.font.render("[Q] QUIT", True, (120, 120, 120))
        surface.blit(r_surf, (80, footer_y))
        surface.blit(q_surf, (SCREEN_WIDTH - 80 - q_surf.get_width(), footer_y))

    def _draw_keyboard(self, surface, name_str, sel_coords, is_done, center_x, label):
        name_surf = self.key_font.render(name_str, True, (255, 255, 255) if not is_done else (0, 255, 0))
        surface.blit(name_surf, name_surf.get_rect(center=(center_x, 260)))
        
        label_surf = self.font.render(label, True, (150, 150, 150))
        surface.blit(label_surf, label_surf.get_rect(center=(center_x, 290)))

        if is_done:
            return

        start_y = 350
        key_spacing_x = 55
        key_spacing_y = 60
        sel_col, sel_row = sel_coords
        row_width = (len(self.keys[0]) - 1) * key_spacing_x
        row_start_x = center_x - (row_width // 2)

        for row_idx, row in enumerate(self.keys):
            for col_idx, char in enumerate(row):
                x = row_start_x + (col_idx * key_spacing_x)
                y = start_y + (row_idx * key_spacing_y)
                is_selected = (col_idx == sel_col and row_idx == sel_row)
                
                t_color = (0, 255, 0) if is_selected else (180, 180, 180)
                char_surf = self.key_font.render(char, True, t_color)
                char_rect = char_surf.get_rect(center=(x, y))
                
                if is_selected:
                    pygame.draw.rect(surface, (0, 255, 0), char_rect.inflate(25, 25), 3)
                surface.blit(char_surf, char_rect)