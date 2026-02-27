from logging import warning

import pygame
from src.config.config import SCREEN_WIDTH

class HeaderBar(pygame.sprite.Sprite):
    def __init__(self, screen, font):
        super().__init__()
        # Store reference to screen and font for later drawing
        self.screen = screen
        self.font = font
        # Fixed level (always 1 per specification)
        self.level = 1
        # Load original PNG (126×22)
        raw_image = pygame.image.load("assets/header-bar.png").convert_alpha()
        orig_w, orig_h = raw_image.get_size()
        # Desired width = 50% of the screen width (centered)
        target_w = int(SCREEN_WIDTH * 0.5)
        # Compute uniform scale factor to preserve aspect ratio
        scale_factor = target_w / orig_w
        target_h = int(orig_h * scale_factor)
        # Uniformly scale the image to the target size
        self.base_image = pygame.transform.scale(raw_image, (target_w, target_h))
        self.image = self.base_image.copy()
        # Position the bar centered horizontally at the top edge
        self.rect = self.image.get_rect()
        self.rect.topleft = ((SCREEN_WIDTH - target_w) // 2, 0)
        # Initialize score/lives values
        self.health_icon = pygame.image.load("assets/HP.png").convert_alpha()
        h_icon_h = int(self.rect.height * 0.4)
        h_icon_w = h_icon_h
        self.health_icon = pygame.transform.scale(self.health_icon, (h_icon_h, h_icon_w))
        self.score = 0
        self.lives = 0
        # Render initial text
        self._render_text()
        raw_warning_img = pygame.image.load("assets/warning.png").convert_alpha()
        new_width = 180
        new_height = 30
        self.warning_icon = pygame.transform.scale(raw_warning_img, (new_width, new_height))

    def _render_text(self):
        """Render Level, Score and Lives onto the header image.
        
        Layout (inside the smaller, centered bar):
        - Left side  : "Level: 1"
        - Center     : "Score: X"
        - Right side : "Lives: Y"
        All text is vertically centered within the header bar.
        """
        # Start from a fresh copy of the scaled base image
        self.image = self.base_image.copy()
        retro_green = (0, 228, 54)
        # Compute vertical center for text within the bar's height
        text_y = (self.rect.height - self.font.get_height()) // 2

        w = self.rect.width

        h = self.rect.height

        # Left – Level (10 px margin from bar's left edge)
        level_surf = self.font.render(f"LvL: {self.level}", True, retro_green)
        level_x = (w // 6) - (level_surf .get_width() // 2 )
        self.image.blit(level_surf, (level_x, text_y))

        # Center – Score (centered within the bar's width)
        score_surf = self.font.render(f"Score: {self.score}", True, retro_green)
        score_x = self.rect.width // 2 - score_surf.get_width() // 2
        self.image.blit(score_surf, (score_x, text_y))

        # Right – Lives (10 px margin from bar's right edge)
        lives_num_surf = self.font.render(f"{self.lives}", True, retro_green)
        total_width = self.health_icon.get_width() + 5 + lives_num_surf.get_width()
        start_x = (5 * w // 6) - (total_width // 2)
        icon_y = (h - self.health_icon.get_height()) // 2
        self.image.blit(self.health_icon, (start_x, icon_y))
        self.image.blit(lives_num_surf, (start_x + self.health_icon.get_width() + 5, text_y))
    

    def update(self, score, lives):  # Later can be extended for LEVEL
        """Update internal score/lives and redraw the header image."""
        self.score = score
        self.lives = lives
        self._render_text()

    def set_level(self, level: int):
        """Set the current level displayed in the header bar and redraw.

        Args:
            level: The new level number to display.
        """
        self.level = level
        self._render_text()


    # The SpriteGroup's draw method handles blitting, so no explicit draw needed
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        warning_x = self.rect.right + 15
        warning_y = self.rect.centery - (self.warning_icon.get_height()// 2)
        screen.blit(self.warning_icon,(warning_x, warning_y))