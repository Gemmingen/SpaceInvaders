import pygame
import os
from src.game.bullet import Bullet
from src.utils.helpers import load_image
from src.config.config import (
    PLAYER_SPEED, PLAYER_PATCH_COLOR, PLAYER_PATCH_RECT,
    PLAYER_BOOST_NORMAL_SIZE, PLAYER_HYPERBOOST_SIZE,
    PLAYER_HYPERBOOST_ANIMATION_DELAY, PLAYER_HYPERBOOST_PROGRESS_UP,
    PLAYER_HYPERBOOST_PROGRESS_DOWN, PLAYER_HYPERBOOST_OVERLAP_BASE,
    PLAYER_HYPERBOOST_OVERLAP_MULT
)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # 1. Lade Basis-Grafiken und skaliere sie erst einmal roh
        raw_idle = pygame.transform.scale(load_image("assets/player-idle.png").convert_alpha(), (32, 32))
        raw_left = pygame.transform.scale(load_image("assets/player-left.png").convert_alpha(), (32, 32))
        raw_right = pygame.transform.scale(load_image("assets/player-right.png").convert_alpha(), (32, 32))
        
        # --- PIXEL-PATCH FÜR FEHLENDE PIXEL ---
        def patch_image(img):
            # Erstelle eine komplett transparente Fläche in der Größe des Bildes
            patched = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            
            # Flicken-Farbe aus Config
            patch_color = PLAYER_PATCH_COLOR 
            
            # Flicken-Rect aus Config (X, Y, Breite, Höhe)
            patch_rect = pygame.Rect(*PLAYER_PATCH_RECT) 
            
            # Zeichne das Quadrat auf die leere Fläche
            pygame.draw.rect(patched, patch_color, patch_rect)
            # Lege das eigentliche Schiff darüber
            patched.blit(img, (0, 0))
            return patched
            
        # 2. Wende den Patch an und speichere sie als base_images
        self.base_image_idle = patch_image(raw_idle)
        self.base_image_left = patch_image(raw_left)
        self.base_image_right = patch_image(raw_right)
        
        self.current_scale = 1.0
        self.image = self.base_image_idle
        self.rect = self.image.get_rect(midbottom=(x, y))
        
        # Float-Positionen für Easing
        self.exact_x = float(self.rect.centerx)
        self.exact_y = float(self.rect.centery)
        
        # Speed und Buffs
        self.base_speed = PLAYER_SPEED
        self.speed = self.base_speed
        self.speed_timer = 0
        
        # Waffensystem
        self.weapon_type = "single"
        self.weapon_timer = 0
        self.last_shot_time = 0
        self.shot_cooldown = 300  # milliseconds
        
        # Leben
        self.lives = 3
    
    def update_buffs(self):
        """Zählt die Timer für PowerUps runter."""
        if self.speed_timer > 0:
            self.speed_timer -= 1
            if self.speed_timer <= 0:
                self.speed = self.base_speed
                
        if self.weapon_timer > 0:
            self.weapon_timer -= 1
            if self.weapon_timer <= 0:
                self.weapon_type = "single"

    def move(self, keys, screen_width):
        """Behandelt die Seitwärtsbewegung und wendet Zoom/Easing an."""
        state = "idle"
        
        # Horizontale Eingaben
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.exact_x -= self.speed
            state = "left"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.exact_x += self.speed
            state = "right"
            
        # Bildschirmgrenzen für exact_x einhalten
        half_width = (32 * self.current_scale) / 2
        if self.exact_x - half_width < 0:
            self.exact_x = half_width
        if self.exact_x + half_width > screen_width:
            self.exact_x = screen_width - half_width

        # Basis-Bild bestimmen
        if state == "idle":
            base_img = self.base_image_idle
        elif state == "left":
            base_img = self.base_image_left
        else:
            base_img = self.base_image_right
            
        # Skalierung anwenden (Zoom rein/raus)
        new_size = (max(1, int(32 * self.current_scale)), max(1, int(32 * self.current_scale)))
        self.image = pygame.transform.scale(base_img, new_size)
        
        # Position aktualisieren basierend auf Float-Werten (verhindert Ruckeln)
        self.rect = self.image.get_rect()
        self.rect.centerx = round(self.exact_x)
        self.rect.centery = round(self.exact_y)
    
    def shoot(self):
        """Erstellt ein Projektil, falls der Cooldown abgelaufen ist."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shot_cooldown:
            self.last_shot_time = current_time
            return Bullet(self.rect.centerx, self.rect.top, direction=-1, bullet_type=self.weapon_type)
        return None

class PlayerBoost(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        
        try:
            self.raw_normal_frames = [
                load_image("assets/player-boost-default.png").convert_alpha(),
                load_image("assets/player-boost-left.png").convert_alpha(),
                load_image("assets/player-boost-right.png").convert_alpha()
            ]
        except Exception:
            print("Warning: Normal boost images not found, using fallback.")
            img = pygame.Surface(PLAYER_BOOST_NORMAL_SIZE, pygame.SRCALPHA)
            img.fill((255, 100, 0, 200)) # Orange
            self.raw_normal_frames = [img, img, img]
        
        self.raw_hyper_frames = []
        for i in range(1, 5):
            filename = f"assets/hyperboost-{i}.png"
            try:
                if os.path.exists(filename):
                    img = load_image(filename).convert_alpha()
                    self.raw_hyper_frames.append(img)
                else:
                    raise FileNotFoundError(f"{filename} not found")
            except Exception as e:
                print(f"Warning: {filename} not found, using fallback. Error: {e}")
                img = pygame.Surface(PLAYER_BOOST_NORMAL_SIZE, pygame.SRCALPHA)
                img.fill((0, 255, 255, 180)) 
                self.raw_hyper_frames.append(img)
            
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_delay = PLAYER_HYPERBOOST_ANIMATION_DELAY 
        self.hyper_progress = 0.0 
        
        self.image = pygame.Surface((1,1)) 
        self.rect = self.image.get_rect()
        self.update_image()
        
    def update(self, is_hyperboosting=False, *args, **kwargs):
        if is_hyperboosting:
            self.hyper_progress = min(1.0, self.hyper_progress + PLAYER_HYPERBOOST_PROGRESS_UP) 
        else:
            self.hyper_progress = max(0.0, self.hyper_progress - PLAYER_HYPERBOOST_PROGRESS_DOWN) 
            
        self.animation_timer += 1
        if self.animation_timer >= self.animation_delay:
            self.animation_timer = 0
            self.current_frame += 1
            
        self.update_image()
        
        self.rect.centerx = self.player.rect.centerx
        
        # WICHTIG: Überlappung berechnen
        overlap = int(PLAYER_HYPERBOOST_OVERLAP_BASE + PLAYER_HYPERBOOST_OVERLAP_MULT * self.hyper_progress) 
        overlap = int(overlap * self.player.current_scale)
        
        # MINUS statt Plus! Zieht den Boost nach oben ins Schiff hinein
        self.rect.top = self.player.rect.bottom - overlap
        
    def update_image(self):
        if self.hyper_progress > 0.1:
            idx = self.current_frame % len(self.raw_hyper_frames)
            base_img = self.raw_hyper_frames[idx]
            target_w, target_h = PLAYER_HYPERBOOST_SIZE
        else:
            idx = self.current_frame % len(self.raw_normal_frames)
            base_img = self.raw_normal_frames[idx]
            target_w, target_h = PLAYER_BOOST_NORMAL_SIZE
            
        current_w = int(PLAYER_BOOST_NORMAL_SIZE[0] + (target_w - PLAYER_BOOST_NORMAL_SIZE[0]) * self.hyper_progress)
        current_h = int(PLAYER_BOOST_NORMAL_SIZE[1] + (target_h - PLAYER_BOOST_NORMAL_SIZE[1]) * self.hyper_progress)
        
        # Multipliziere Boost-Größe mit dem aktuellen Player Zoom-Faktor!
        current_w = int(current_w * self.player.current_scale)
        current_h = int(current_h * self.player.current_scale)
        
        final_w = max(1, current_w)
        final_h = max(1, current_h)
        
        self.image = pygame.transform.scale(base_img, (final_w, final_h))
        
        pos = self.rect.topleft
        self.rect = self.image.get_rect()
        self.rect.topleft = pos