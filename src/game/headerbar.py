import pygame
from src.config.config import SCREEN_WIDTH

class HeaderBar(pygame.sprite.Sprite):
    def __init__(self, screen, font):
        super().__init__()
        self.screen = screen
        
        # --- SCHRIFTGRÖßE ANPASSEN ---
        # Wir ignorieren die kleine Schrift aus der game.py und laden sie hier größer
        self.font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 16)
        
        self.level = 1
        self.wave = 1
        self.is_wave_mode = False
        
        raw_image = pygame.image.load("assets/header-bar.png").convert_alpha()
        orig_w, orig_h = raw_image.get_size()
        
        target_w = int(SCREEN_WIDTH * 0.5)
        scale_factor = target_w / orig_w
        target_h = int(orig_h * scale_factor)
        
       # --- SCHWARZER HINTERGRUND FÜR DIE PNG-GRAFIK ---
        # 1. Erstelle eine TRANSPARENTE Fläche in der Zielgröße
        self.base_image = pygame.Surface((target_w, target_h), pygame.SRCALPHA)
        
        # 2. Zeichne einen schwarzen Block, der an allen Seiten 6 Pixel kleiner ist
        offset_x = 6
        offset_y = 6
        inner_rect = pygame.Rect(offset_x, offset_y, target_w - (2 * offset_x), target_h - (2 * offset_y))
        pygame.draw.rect(self.base_image, (0, 0, 0), inner_rect)
        
        # 3. Skaliere das PNG und blitte es drüber
        scaled_raw = pygame.transform.scale(raw_image, (target_w, target_h))
        self.base_image.blit(scaled_raw, (0, 0))

        self.image = self.base_image.copy()
        
        # Zentriere die Bar oben am Bildschirm
        self.rect = self.image.get_rect()
        self.rect.topleft = ((SCREEN_WIDTH - target_w) // 2, 0)
        
        # HP Icon
        self.health_icon = pygame.image.load("assets/HP.png").convert_alpha()
        h_icon_h = int(self.rect.height * 0.4)
        h_icon_w = h_icon_h
        self.health_icon = pygame.transform.scale(self.health_icon, (h_icon_h, h_icon_w))
        
        self.score = 0
        self.lives = 0
        
        self._render_text()
        
        # Warn-Icon
        raw_warning_img = pygame.image.load("assets/warning.png").convert_alpha()
        new_width = 180
        new_height = 30
        self.warning_icon = pygame.transform.scale(raw_warning_img, (new_width, new_height))

    def _render_text(self):
        """Rendert Level/Wave, Score und Lives in die Header-Grafik."""
        self.image = self.base_image.copy()
        retro_green = (0, 228, 54)
        
        # Zentriere den Text vertikal
        text_y = (self.rect.height - self.font.get_height()) // 2

        w = self.rect.width
        h = self.rect.height

        # Links – Level oder Wave
        if self.is_wave_mode:
            display_text = f"Wave:{self.wave}"
        else:
            display_text = f"LvL:{self.level}"

        level_surf = self.font.render(display_text, True, retro_green)
        level_x = (w // 6) - (level_surf.get_width() // 2)
        self.image.blit(level_surf, (level_x, text_y))

        # Mitte – Score 
        score_surf = self.font.render(f"Score: {self.score}", True, retro_green)
        score_x = self.rect.width // 2 - score_surf.get_width() // 2
        self.image.blit(score_surf, (score_x, text_y))

        # Rechts – Lives 
        lives_num_surf = self.font.render(f"{self.lives}", True, retro_green)
        total_width = self.health_icon.get_width() + 5 + lives_num_surf.get_width()
        start_x = (5 * w // 6) - (total_width // 2)
        icon_y = (h - self.health_icon.get_height()) // 2
        
        self.image.blit(self.health_icon, (start_x, icon_y))
        self.image.blit(lives_num_surf, (start_x + self.health_icon.get_width() + 5, text_y))
    
    def update(self, score, lives):  
        """Aktualisiert die Werte und zeichnet sie neu."""
        self.score = score
        self.lives = lives
        self._render_text()

    def set_wave(self, wave_number):
        """Aktiviert den Endless/Versus Modus und setzt die Wave."""
        self.wave = wave_number
        self.is_wave_mode = True
        self._render_text()

    def set_level(self, level_number):
        """Aktiviert den Story Modus und setzt das Level."""
        self.level = level_number
        self.is_wave_mode = False
        self._render_text()

    def draw(self, screen):
        # --- DURCHGEHENDER SCHWARZER BALKEN ---
        # Verhindert, dass Gegner oder Sterne links/rechts neben der UI durchscheinen
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, SCREEN_WIDTH, self.rect.height))
        
        # Zeichne die Grafik mittig drüber
        screen.blit(self.image, self.rect)
        
        # Hinweis: Das tatsächliche Zeichnen des Warn-Icons (Blinken) 
        # passiert wahrscheinlich in deiner game.py. Die Methode hier 
        # zeichnet es dauerhaft, weshalb sie in manchen Konfigurationen
        # ignoriert oder in der game.py überschrieben wird.