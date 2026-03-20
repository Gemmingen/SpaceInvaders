"""BossSmall3 – horizontal sweeper that drops bombs.

Appears on level 3. Moves left‑right near the top of the screen and
periodically spawns a bomb sprite (using the boss‑attack1 image) that falls
straight down.
"""
import pygame
import random
import math
from src.config.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BOSS3_GLOB_SPLIT_ANGLE_DEGREES, 
    BOSS3_GLOB_SPLIT_HEIGHT, BOSS3_POISON_PUDDLE_FRAME_SKIP, 
    BOSS3_POISON_PUDDLE_ANIMATION_SPEED, BOSS3_POISON_PUDDLE_SIZE,
    MINIBOSS_SPAWN_FRAMES, MINIBOSS_SPAWNER_SIZE, MINIBOSS_SPAWNER_ROT_SPEED,
    BOSS3_POISON_PUDDLE_HITBOX_WIDTH, BOSS3_POISON_PUDDLE_HITBOX_HEIGHT # <-- ADDED
)
from src.game.miniboss_base import MiniBossBase
from src.utils.helpers import load_image

# Configurable constants
GLOB_SPEED = 8          # Pixels per frame – fast enough to reach the player
PUDDLE_OFFSET = 0    # No vertical offset; puddle sits on player's bottom
# Inaccuracy in pixels applied to the homing glob's trajectory
INACCURACY_PIXELS = 30  # +/- 30 px random offset for dx/dy

class PoisonGlob(pygame.sprite.Sprite):
    """Simple bomb that falls vertically."""
    def __init__(self, x, y, speed=GLOB_SPEED, puddle_group=None, effect_group=None, player=None, splits=False):
        super().__init__()
        img = pygame.image.load('assets/boss-attack1.png').convert_alpha()
        self.image = pygame.transform.scale(img, (30, 30))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        # Store exact floating‑point coordinates for precise movement
        self.exact_x = float(self.rect.x)
        self.exact_y = float(self.rect.y)
        # Reference to the group where puddles should be added
        self.puddle_group = puddle_group
        self.effect_group = effect_group
        self.has_spawned = False
        self.player = player
        self.damage = 1  # reduced damage for this weaker homing bullet
        self.splits = splits          # flag: this bullet should split at mid‑screen
        self.has_split = False        # ensures split happens only once

    def update(self, *args, **kwargs):
        """Move the glob using exact float coordinates and kill on floor contact.

        Puddle creation is handled in ``kill()`` to ensure it always spawns.
        """
        # --- Movement (targeted or straight) ---
        if hasattr(self, 'vel_x') and hasattr(self, 'vel_y'):
            self.exact_x += self.vel_x
            self.exact_y += self.vel_y
        else:
            self.exact_y += self.speed

        # Sync integer rect with float coordinates
        self.rect.x = int(self.exact_x)
        self.rect.y = int(self.exact_y)

        # ----- Split logic (mid‑screen) -----
        if getattr(self, 'splits', False) and not getattr(self, 'has_split', False) and self.rect.centery >= BOSS3_GLOB_SPLIT_HEIGHT:
            # Prevent the original puddle from spawning
            self.has_spawned = True
            self.has_split = True
            # Create three child globs with diverging angles
            for angle in (-BOSS3_GLOB_SPLIT_ANGLE_DEGREES, BOSS3_GLOB_SPLIT_ANGLE_DEGREES):
                rad = math.radians(angle)
                vx = math.sin(rad) * self.speed
                vy = math.cos(rad) * self.speed
                child = PoisonGlob(self.rect.centerx, self.rect.centery,
                                   speed=self.speed,
                                   puddle_group=self.puddle_group,
                                   effect_group=None,
                                   player=self.player,
                                   splits=False)
                child.image = pygame.transform.scale(child.image, (25, 25))
                child.vel_x = vx
                child.vel_y = vy
                # Add child to all groups the parent belonged to
                for grp in self.groups():
                    grp.add(child)
            # Kill the original bullet without spawning a puddle
            self.kill()
            return

        # Kill when reaching the bottom of the screen (puddle will be spawned in kill())
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.kill()

    def kill(self):
        """Guarantee a puddle spawns before the sprite is removed.

        If a player reference was supplied, the puddle appears at the player's
        foot level (using the player's current bottom coordinate). Otherwise it
        falls to the bottom of the screen as before.
        """
        if not self.has_spawned and self.puddle_group is not None:
            # Preserve the projectile's X coordinate
            puddle_x = self.rect.centerx
            # Use the player's foot level if available, otherwise fall back to the glob's current bottom
            #if self.player is not None:
            puddle_y = min(self.player.rect.bottom + PUDDLE_OFFSET, SCREEN_HEIGHT - 20)
            #else:
            #    puddle_y = min(self.rect.bottom + PUDDLE_OFFSET, SCREEN_HEIGHT - 20)
            self.puddle_group.add(PoisonPuddle(puddle_x, puddle_y, BOSS3_POISON_PUDDLE_FRAME_SKIP, BOSS3_POISON_PUDDLE_ANIMATION_SPEED, BOSS3_POISON_PUDDLE_SIZE, effect_group=self.effect_group))
            self.has_spawned = True
        super().kill()

class PoisonPuddle(pygame.sprite.Sprite):
    """Lingers on the ground, plays an animated poison explosion, and damages the player."""
    
    _frame_cache = None 

    def __init__(self, x, y, 
                 frame_skip=BOSS3_POISON_PUDDLE_FRAME_SKIP, 
                 animation_speed=BOSS3_POISON_PUDDLE_ANIMATION_SPEED, 
                 target_size=BOSS3_POISON_PUDDLE_SIZE,
                 effect_group=None):
        super().__init__()
        self.effect_group = effect_group
        # 1. Load and scale frames ONLY if the cache is empty
        if PoisonPuddle._frame_cache is None:
            PoisonPuddle._frame_cache = []
            total_frames = 278 
            
            for i in range(1, total_frames + 1, frame_skip):
                try:
                    img_path = f'assets/poison-explosion/poison-explosion{i:03d}.png'
                    img = pygame.image.load(img_path).convert_alpha()
                    
                    if target_size:
                        img = pygame.transform.scale(img, target_size)
                        
                    PoisonPuddle._frame_cache.append(img)
                except Exception:
                    pass
                    
            # Fallback if no images are found
            if not PoisonPuddle._frame_cache:
                img = pygame.Surface((64, 16), pygame.SRCALPHA)
                img.fill((0, 255, 0, 255))
                PoisonPuddle._frame_cache.append(img)

        self.frames = PoisonPuddle._frame_cache
        self.animation_speed = animation_speed
        
        self.current_frame = 0.0 
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        
        self.hitbox = pygame.Rect(0, 0, BOSS3_POISON_PUDDLE_HITBOX_WIDTH, BOSS3_POISON_PUDDLE_HITBOX_HEIGHT)
        # Center the hitbox exactly in the middle of the visual sprite
        self.hitbox.center = self.rect.center
        # --- NEW: Effect spawning variables ---
        self.effects_to_spawn = 5
        # Calculate roughly how many frames to wait between spawns
        self.effect_interval = max(1, len(self.frames) // (self.effects_to_spawn + 1))
        self.last_effect_frame = 0

    def update(self, *args, **kwargs):
        self.current_frame += self.animation_speed
        
        # Convert to an integer to get the actual list index
        frame_index = int(self.current_frame)
        
        if frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[frame_index]
            
            # --- NEW: Spawn poison effects ---
            if frame_index - self.last_effect_frame >= self.effect_interval and self.effects_to_spawn > 0:
                self.last_effect_frame = frame_index
                self.effects_to_spawn -= 1
                
                # Calculate a random position within the general width of the puddle
                offset_x = random.randint(-self.rect.width // 6, self.rect.width // 6)
                # Position it near the centre/bottom area
                offset_y = random.randint(0, self.rect.height // 5)
                
                effect = PoisonEffect(self.rect.centerx + offset_x, self.rect.centery + offset_y)
                
                # Automatically add the effect to the same sprite groups as the puddle
                if self.effect_group is not None:
                    self.effect_group.add(effect)

class PoisonEffect(pygame.sprite.Sprite):
    """Small poison effect particle that rises and fades."""
    _image_cache = None

    def __init__(self, x, y):
        super().__init__()
        # Load the image once and cache it
        if PoisonEffect._image_cache is None:
            try:
                PoisonEffect._image_cache = pygame.image.load('assets/poison-effect.png').convert_alpha()
                
            except Exception:
                # Fallback if image is missing
                surf = pygame.Surface((15, 15), pygame.SRCALPHA)
                surf.fill((0, 255, 0, 180))
                PoisonEffect._image_cache = surf
                
        self.original_image = pygame.transform.scale(PoisonEffect._image_cache, (75, 75))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.alpha = 255
        
        # Randomize fade and rise speeds slightly for a natural effect
        self.fade_speed = random.randint(3, 7) 
        self.rise_speed = random.uniform(0.5, 1.5)
        self.exact_y = float(self.rect.y)

    def update(self, *args, **kwargs):
        # Rise slowly upwards
        self.exact_y -= self.rise_speed
        self.rect.y = int(self.exact_y)
        
        # Fade out
        self.alpha -= self.fade_speed
        if self.alpha <= 0:
            self.kill()
        else:
            self.image = self.original_image.copy()
            self.image.set_alpha(self.alpha)

class BossSmall3(MiniBossBase):
    def __init__(self, health=3, speed=2):
        super().__init__('assets/boss-small3.png', health, speed)
        
        # --- Intro Setup ---
        self.boss_base = self.image.copy()
        self.spawner_base = load_image('assets/boss3-spawner.png').convert_alpha()
        
        self.base_y = 220
        # Start near top‑left (verschoben auf SCREEN_WIDTH // 2, wie gewünscht!)
        self.exact_x = float(SCREEN_WIDTH // 2)
        self.exact_y = float(self.base_y)
        
        # Unsichtbarer Start für den ersten Frame
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(round(self.exact_x), round(self.exact_y)))
        
        self.state = "intro"
        self.intro_timer = 0
        
        self.time_ticker = 0
        self.direction = 1  # 1 = right, -1 = left
        self.drop_interval = 180
        self.drop_timer = self.drop_interval
        self.poison_group = pygame.sprite.Group()
        self.puddle_group = pygame.sprite.Group()
        self.effect_group = pygame.sprite.Group()
    def update(self, player=None, *args, **kwargs):  # Expected args: all_sprites, enemy_bullets, explosions, screen_width, screen_height, puddles_group
        """Update movement and drop PoisonGlob.

        Compatibility shim: accept positional arguments from Game.update.
        Expected positional order (if provided):
            0: all_sprites
            1: enemy_bullets
            2: explosions (currently unused)
            3: screen_width
            4: screen_height
            5: puddles (external puddle group)
        """
        # Populate kwargs from positional args if not already provided
        if len(args) >= 1 and 'all_sprites' not in kwargs:
            kwargs['all_sprites'] = args[0]
        if len(args) >= 2 and 'enemy_bullets' not in kwargs:
            kwargs['enemy_bullets'] = args[1]
        if len(args) >= 6 and 'puddles' not in kwargs:
            kwargs['puddles'] = args[5]

        # ========================================================
        # 1. INTRO / SPAWN ANIMATION
        # ========================================================
        if getattr(self, 'state', None) == "intro":
            self.intro_timer += 1
            
            canvas_size = MINIBOSS_SPAWNER_SIZE + 100
            surf = pygame.Surface((canvas_size, canvas_size), pygame.SRCALPHA)
            center = (canvas_size // 2, canvas_size // 2)
            
            spawner_scale = min(1.0, self.intro_timer / float(MINIBOSS_SPAWN_FRAMES))
            if spawner_scale > 0:
                spawner_size = int(MINIBOSS_SPAWNER_SIZE * spawner_scale)
                if spawner_size > 0:
                    spawner_scaled = pygame.transform.scale(self.spawner_base, (spawner_size, spawner_size))
                    spawner_rot = pygame.transform.rotate(spawner_scaled, self.intro_timer * MINIBOSS_SPAWNER_ROT_SPEED)
                    sp_rect = spawner_rot.get_rect(center=center)
                    surf.blit(spawner_rot, sp_rect)
            
            if self.intro_timer > MINIBOSS_SPAWN_FRAMES:
                boss_scale = min(1.0, (self.intro_timer - MINIBOSS_SPAWN_FRAMES) / float(MINIBOSS_SPAWN_FRAMES))
                bw = int(self.boss_base.get_width() * boss_scale)
                bh = int(self.boss_base.get_height() * boss_scale)
                if bw > 0 and bh > 0:
                    boss_scaled = pygame.transform.scale(self.boss_base, (bw, bh))
                    b_rect = boss_scaled.get_rect(center=center)
                    surf.blit(boss_scaled, b_rect)
            
            self.image = surf
            self.rect = self.image.get_rect(center=(round(self.exact_x), round(self.exact_y)))
            
            if self.intro_timer >= MINIBOSS_SPAWN_FRAMES * 2:
                self.state = "orbiting"
                self.image = self.boss_base.copy()
                self.rect = self.image.get_rect(center=(round(self.exact_x), round(self.exact_y)))
                self.mask = pygame.mask.from_surface(self.image)
                
            return # Blockiert normale Updates bis das Intro durch ist!

        # ========================================================
        # 2. NORMAL GAMEPLAY UPDATE
        # ========================================================
        # --- Sine wave vertical movement ---
        self.time_ticker += 0.05
        self.rect.centery = int(self.base_y - abs(math.sin(self.time_ticker)) * 100)

        # --- Horizontal movement (bounce) ---
        self.rect.x += self.direction * self.speed
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1

        # --- Poison glob dropping timer ---
        self.drop_timer -= 1
        if self.drop_timer <= 0:
            # Reduce the base speed (make the bullet slower) – 75 % of the original
            speed = int(GLOB_SPEED * 0.75)
            # Fire straight down without homing; enable split at mid‑screen
            glob = PoisonGlob(self.rect.centerx, self.rect.bottom,
                               speed=speed,
                               puddle_group=self.puddle_group,
                               effect_group=self.effect_group,
                               player=player,
                               splits=True)
            # Straight‑down velocity
            glob.vel_x = 0
            glob.vel_y = speed
            self.poison_group.add(glob)
            self.drop_timer = self.drop_interval

        # --- Update poison globs (pass puddle group and player) ---
        self.poison_group.update()
        self.effect_group.update()
        # --- Sync globs and puddles with external groups ---
        if 'all_sprites' in kwargs:
            for p in self.poison_group:
                kwargs['all_sprites'].add(p)
            for pd in self.puddle_group:
                kwargs['all_sprites'].add(pd)
            for e in self.effect_group:          # <--- NEU: Effekte hinzufügen
                kwargs['all_sprites'].add(e)
        if 'enemy_bullets' in kwargs:
            for p in self.poison_group:
                kwargs['enemy_bullets'].add(p)
        if 'puddles' in kwargs:
            for pd in self.puddle_group:
                kwargs['puddles'].add(pd)
        

    def hit(self):
        # Im Intro unverwundbar
        if getattr(self, 'state', None) == "intro":
            return
            
        self.health -= 1
        if self.health <= 0:
            self.kill()