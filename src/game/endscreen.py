import pygame
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT

class EndScreen:
    def __init__(self, font):
        """
        Initialisiert den Endbildschirm mit allen Schriftarten und dem Keyboard-Layout.
        """
        self.font = font
        # Schriftarten laden
        self.title_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 50)
        self.key_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 20)
        
        # Virtuelles Tastatur-Layout
        # < = Backspace, OK = Bestätigen/Speichern
        self.keys = [
            ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
            ['H', 'I', 'J', 'K', 'L', 'M', 'N'],
            ['O', 'P', 'Q', 'R', 'S', 'T', 'U'],
            ['V', 'W', 'X', 'Y', 'Z', '<', 'OK']
        ]
        
        # Hintergrund-Overlay (Halbtransparent)
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 220))

    def draw(self, surface, state, score, player_name, selected_key_coords, is_victory=False):
        """
        Zeichnet den kompletten Endbildschirm inkl. asynchronem Blinken.
        """
        # 1. Hintergrund abdunkeln
        surface.blit(self.overlay, (0, 0))
        
        # --- ASYNCHRONE BLINK-LOGIK ---
        current_time = pygame.time.get_ticks()
        
        # Titel: Langsamer Takt (800ms)
        title_visible = (current_time // 800) % 2 == 0
        
        # Cursor: Schneller, ungerader Takt (250ms) für echtes asynchrones Feeling
        cursor_visible = (current_time // 250) % 2 == 0
        
        # 2. Titel zeichnen (Blinkt langsam bei Game Over)
        msg = "YOU WIN!" if is_victory else "GAME OVER"
        color = (0, 255, 0) if is_victory else (255, 50, 50)
        
        if is_victory or title_visible:
            title_surf = self.title_font.render(msg, True, color)
            title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 120))
            surface.blit(title_surf, title_rect)

        # 3. Score anzeigen (Immer sichtbar)
        score_surf = self.key_font.render(f"SCORE:{score}", True, (255, 215, 0))
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, 200))
        surface.blit(score_surf, score_rect)

        # 4. Name mit ASYNCHRON blinkendem Cursor (_)
        cursor = "_" if cursor_visible else " "
        name_text = f"NAME: {player_name}{cursor}"
        name_surf = self.key_font.render(name_text, True, (255, 255, 255))
        name_rect = name_surf.get_rect(center=(SCREEN_WIDTH // 2, 280))
        surface.blit(name_surf, name_rect)

        # 5. Virtuelle Tastatur (Zentriert unter Name/Score)
        start_y = 380
        key_spacing_x = 85
        key_spacing_y = 70
        sel_col, sel_row = selected_key_coords

        for row_idx, row in enumerate(self.keys):
            # Dynamische Zentrierung pro Zeile
            row_width = (len(row) - 1) * key_spacing_x
            row_start_x = (SCREEN_WIDTH // 2) - (row_width // 2)
            
            for col_idx, char in enumerate(row):
                x = row_start_x + (col_idx * key_spacing_x)
                y = start_y + (row_idx * key_spacing_y)
                
                is_selected = (col_idx == sel_col and row_idx == sel_row)
                
                # Farbe wählen: Grün wenn ausgewählt, sonst hellgrau
                t_color = (0, 255, 0) if is_selected else (180, 180, 180)
                char_surf = self.key_font.render(char, True, t_color)
                char_rect = char_surf.get_rect(center=(x, y))
                
                # Wenn ausgewählt: Grüner Rahmen und giftgrüne Schrift
                if is_selected:
                    pygame.draw.rect(surface, (0, 255, 0), char_rect.inflate(35, 35), 3)
                
                surface.blit(char_surf, char_rect)

        # 6. Fußzeile (R & Q Schnellwahl)
        footer_y = SCREEN_HEIGHT - 60
        r_surf = self.font.render("[R] RESTART", True, (120, 120, 120))
        q_surf = self.font.render("[Q] QUIT", True, (120, 120, 120))
        
        surface.blit(r_surf, (80, footer_y))
        surface.blit(q_surf, (SCREEN_WIDTH - 80 - q_surf.get_width(), footer_y))