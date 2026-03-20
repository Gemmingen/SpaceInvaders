import pygame
import os
from src.game.bullet import Bullet
from src.utils.helpers import load_image
from src.config.config import (
    PLAYER_SPEED, PLAYER_PATCH_COLOR, PLAYER_PATCH_RECT,
    PLAYER_BOOST_NORMAL_SIZE, PLAYER_HYPERBOOST_SIZE,
    PLAYER_HYPERBOOST_ANIMATION_DELAY, PLAYER_HYPERBOOST_PROGRESS_UP,
    PLAYER_HYPERBOOST_OVERLAP_BASE, PLAYER_HYPERBOOST_OVERLAP_MULT, 
    POWERUP_SPEED_MULTIPLIER, POISON_SPEED_MULTIPLIER, PLAYER_HYPERBOOST_PROGRESS_DOWN
)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, player_id=1):
        super().__init__()
        self.player_id = player_id
        
        # Determine prefix for assets based on player_id
        prefix = "player" if player_id == 1 else "player2"
        
        # Load base graphics
        raw_idle = pygame.transform.scale(load_image(f"assets/{prefix}-idle.png").convert_alpha(), (32, 32))
        raw_left = pygame.transform.scale(load_image(f"assets/{prefix}-left.png").convert_alpha(), (32, 32))
        raw_right = pygame.transform.scale(load_image(f"assets/{prefix}-right.png").convert_alpha(), (32, 32))
        
        # Patch missing pixels
        def patch_image(img):
            patched = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(patched, PLAYER_PATCH_COLOR, pygame.Rect(*PLAYER_PATCH_RECT))
            patched.blit(img, (0, 0))
            return patched
            
        self.base_image_idle = patch_image(raw_idle)
        self.base_image_left = patch_image(raw_left)
        self.base_image_right = patch_image(raw_right)
        
        self.current_scale = 1.0
        self.image = self.base_image_idle
        self.rect = self.image.get_rect(midbottom=(x, y))
        
        self.exact_x = float(self.rect.centerx)
        self.exact_y = float(self.rect.centery)
        
        self.base_speed = PLAYER_SPEED
        self.speed = self.base_speed
        self.speed_timer = 0
        self.poison_debuff_timer = 0
        
        self.weapon_type = "single"
        self.weapon_timer = 0
        self.last_shot_time = 0
        self.shot_cooldown = 300
    
    def update_buffs(self):
        # Keep your existing update_buffs implementation...
        if self.poison_debuff_timer > 0:
            self.poison_debuff_timer -= 1
            if self.poison_debuff_timer <= 0:
                self.speed = int(self.base_speed * POWERUP_SPEED_MULTIPLIER) if self.speed_timer > 0 else self.base_speed

        if self.speed_timer > 0:
            self.speed_timer -= 1
            if self.speed_timer <= 0:
                self.speed = int(self.base_speed * POISON_SPEED_MULTIPLIER) if self.poison_debuff_timer > 0 else self.base_speed
                
        if self.weapon_timer > 0:
            self.weapon_timer -= 1
            if self.weapon_timer <= 0:
                self.weapon_type = "single"

    def move(self, keys, screen_width):
        state = "idle"
        
        # Check controls based on player ID
        if self.player_id == 1:
            move_left = keys[pygame.K_a]
            move_right = keys[pygame.K_d]
        else:
            move_left = keys[pygame.K_LEFT]
            move_right = keys[pygame.K_RIGHT]
            
        if move_left:
            self.exact_x -= self.speed
            state = "left"
        if move_right:
            self.exact_x += self.speed
            state = "right"
            
        half_width = (32 * self.current_scale) / 2
        if self.exact_x - half_width < 0: self.exact_x = half_width
        if self.exact_x + half_width > screen_width: self.exact_x = screen_width - half_width

        if state == "idle": base_img = self.base_image_idle
        elif state == "left": base_img = self.base_image_left
        else: base_img = self.base_image_right
       
        new_size = (max(1, int(32 * self.current_scale)), max(1, int(32 * self.current_scale)))
        self.image = pygame.transform.scale(base_img, new_size)
        if self.poison_debuff_timer > 0:
            tint = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            tint.fill((100, 255, 100, 255)) 
            self.image.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
        self.rect = self.image.get_rect()
        self.rect.centerx = round(self.exact_x)
        self.rect.centery = round(self.exact_y)
    
    def shoot(self):
        # Keep existing shoot logic
        if getattr(self, 'poison_debuff_timer', 0) > 0: return None 
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shot_cooldown:
            self.last_shot_time = current_time
            return Bullet(self.rect.centerx, self.rect.top, direction=-1, bullet_type=self.weapon_type)
        return None

# Keep your existing PlayerBoost class here...

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
        
        overlap = int(PLAYER_HYPERBOOST_OVERLAP_BASE + PLAYER_HYPERBOOST_OVERLAP_MULT * self.hyper_progress) 
        overlap = int(overlap * self.player.current_scale)
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
        
        if getattr(self.player, 'poison_debuff_timer', 0) > 0:
            current_w = int(current_w * 0.5)
            current_h = int(current_h * 0.5)
            
        current_w = int(current_w * self.player.current_scale)
        current_h = int(current_h * self.player.current_scale)
        
        final_w = max(1, current_w)
        final_h = max(1, current_h)
        
        self.image = pygame.transform.scale(base_img, (final_w, final_h))
        pos = self.rect.topleft
        self.rect = self.image.get_rect()
        self.rect.topleft = pos