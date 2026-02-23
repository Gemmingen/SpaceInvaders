import pygame

# Hilfsfunktion einfügen
def get_image(sheet, x, y, width, height):
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    image.blit(sheet, (0, 0), (x, y, width, height))
    return image

class Game:
    def __init__(self):
        # Bildschirm einrichten
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Space Invaders")
        
        self.clock = pygame.time.Clock()
        self.running = True

        # --- ASSETS LADEN ---
        # 1. Das komplette Spritesheet laden
        self.spritesheet = pygame.image.load("assets/pico8_invaders_sprites_LARGE.png").convert_alpha()
        
        # 2. Das 8x8 Raumschiff aus dem Sheet herausschneiden
        self.player_image = get_image(self.spritesheet, 0, 0, 8, 8)
        
        # 3. Das Sprite vergrößern (auf 32x32)
        self.player_image = pygame.transform.scale(self.player_image, (32, 32))
        # --------------------

        # Variablen für die Spielerposition
        self.player_x = self.width // 2 - 16
        self.player_y = self.height - 100

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()

    def handle_events(self):
        # A. Ereignisse abfragen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        # B. Spiellogik updaten (Bewegung des Spielers)
        keys = pygame.key.get_pressed()
        speed = 5
        
        if keys[pygame.K_LEFT]:
            self.player_x -= speed
        if keys[pygame.K_RIGHT]:
            self.player_x += speed
            
        # Verhindern, dass das Raumschiff aus dem Bildschrim fliegt
        if self.player_x < 0:
            self.player_x = 0
        elif self.player_x > self.width - 32: # 32 ist die Breite des Raumschiffs
            self.player_x = self.width - 32

    def draw(self):
        # C. Zeichnen
        self.screen.fill((0, 0, 0)) # Hintergrund schwarz malen
        
        # --- ASSETS ZEICHNEN ---
        self.screen.blit(self.player_image, (self.player_x, self.player_y))
        # -----------------------

        # D. Das gezeichnete Bild auf dem Bildschirm anzeigen
        pygame.display.flip()