import pygame
from src.game.bullet import Bullet
from src.utils.helpers import load_image
from src.config.config import PLAYER_SPEED

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image_idle = pygame.transform.scale(load_image("assets/player-idle.png").convert_alpha(), (32, 32))
        self.image_left = pygame.transform.scale(load_image("assets/player-left.png").convert_alpha(), (32, 32))
        self.image_right = pygame.transform.scale(load_image("assets/player-right.png").convert_alpha(), (32, 32))
        
        self.image = self.image_idle
        self.rect = self.image.get_rect(midbottom=(x, y))
        
        # Speed und Buffs
        self.base_speed = PLAYER_SPEED
        self.speed = self.base_speed
        self.speed_timer = 0
        
        self.weapon_type = "single"
        self.weapon_timer = 0
        
        self.last_shot_time = 0
        self.shot_cooldown = 300  # milliseconds
        self.lives = 3
    
    def update_buffs(self):
        # Speed Buff runterzählen
        if self.speed_timer > 0:
            self.speed_timer -= 1
            if self.speed_timer <= 0:
                self.speed = self.base_speed
                
        # Waffen Buff runterzählen
        if self.weapon_timer > 0:
            self.weapon_timer -= 1
            if self.weapon_timer <= 0:
                self.weapon_type = "single"

    def move(self, keys, screen_width):
        self.image = self.image_idle
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.image = self.image_left
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            self.image = self.image_right
            
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
    
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shot_cooldown:
            self.last_shot_time = current_time
            # Übergebe den Waffentyp an das Bullet
            return Bullet(self.rect.centerx, self.rect.top, direction=-1, bullet_type=self.weapon_type)
        return None

class PlayerBoost(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        
        # Lade die 3 Boost-Bilder und skaliere sie (z.B. auf 16 Pixel Breite und 24 Pixel Höhe)
        self.frames = [
            pygame.transform.scale(load_image("assets/player-boost-default.png").convert_alpha(), (16, 24)),
            pygame.transform.scale(load_image("assets/player-boost-left.png").convert_alpha(), (16, 24)),
            pygame.transform.scale(load_image("assets/player-boost-right.png").convert_alpha(), (16, 24))
        ]
        
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        
        # Animations-Timer
        self.animation_timer = 0
        self.animation_delay = 4  # Je kleiner die Zahl, desto schneller flackert der Boost
        
    def update(self):
        # Der Boost wird auf der X-Achse zentriert
        self.rect.centerx = self.player.rect.centerx
        
        # Setzt die Oberkante des Boosts etwas höher an (z. B. 10 Pixel in das Schiff hinein)
        self.rect.top = self.player.rect.bottom - 6
        
        # Frame der Animation weiterrücken
        self.animation_timer += 1
        if self.animation_timer >= self.animation_delay:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]