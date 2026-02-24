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
        self.score = 0
        self.lives = 0
        # Render initial text
        self._render_text()

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
        # Compute vertical center for text within the bar's height
        text_y = (self.rect.height - self.font.get_height()) // 2

        # Left – Level (10 px margin from bar's left edge)
        level_surf = self.font.render(f"Level: {self.level}", True, (255, 255, 255))
        self.image.blit(level_surf, (10, text_y))

        # Center – Score (centered within the bar's width)
        score_surf = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        score_x = self.rect.width // 2 - score_surf.get_width() // 2
        self.image.blit(score_surf, (score_x, text_y))

        # Right – Lives (10 px margin from bar's right edge)
        lives_surf = self.font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        lives_x = self.rect.width - lives_surf.get_width() - 10
        self.image.blit(lives_surf, (lives_x, text_y))

    def update(self, score, lives):  # Later can be extended for LEVEL
        """Update internal score/lives and redraw the header image."""
        self.score = score
        self.lives = lives
        self._render_text()

    # The SpriteGroup's draw method handles blitting, so no explicit draw needed
    def draw(self, *args, **kwargs):
        pass