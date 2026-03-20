import pygame
import random
import sys
import json
import os
from src.config.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, PLAYER_SPEED,
    ENEMY_SPEED, BULLET_SPEED, TEST_START_LEVEL, UFO_SPAWN_TIME,
    UFO_SCORE_OPTIONS, UFO_SHOT_THRESHOLD,
    BASE_SCROLL_SPEED, INITIAL_SCROLL, PARALLAX_LAYERS, PARALLAX_SPEED_FACTORS,
    LEVEL_BACKGROUND_PATTERN, TRANSITION_BACKGROUND_PATTERN,
    ENEMY_SHOOT_CHANCE,
    ENEMY_WAVE_SETTINGS, MINIBOSS_SETTINGS,
    POWERUP_DROP_CHANCES, POWERUP_FALL_SPEED, COMET_SPEED, COMET_ROTATION_SPEED,
    POWERUP_SPEED_DURATION, POWERUP_DOUBLESHOT_DURATION, POWERUP_TRIPLESHOT_DURATION,
    POWERUP_SPEED_MULTIPLIER, TIE_FIGHTER_SPEED, TIE_FIGHTER_SIZE, TIE_FIGHTER_ROTATION_SPEED,
    AMPLIFY_STEP, DECEL_STEP, AMPLIFY_MAX_FACTOR, THRESHOLD_FACTOR, TRANSITION_HOLD_FRAMES,
    PLANET_SCROLL_FACTOR,
    TRANSITION_PLAYER_SCALE_MAX, TRANSITION_PLAYER_SCALE_NORMAL,
    TRANSITION_PLAYER_SCALE_EASING, TRANSITION_BUNKER_Y_DOWN,
    TRANSITION_BUNKER_Y_UP, TRANSITION_BUNKER_EASING,
    TRANSITION_PLAYER_Y_AMPLIFY_PCT, TRANSITION_PLAYER_Y_HOLD_PCT,
    TRANSITION_PLAYER_Y_NORMAL_OFFSET, TRANSITION_PLAYER_EASING_UP,
    TRANSITION_PLAYER_EASING_DOWN, TRANSITION_PLAYER_EASING_RETURN,
    TRANSITION_PLAYER_EASING_PLAYING, TRANSITION_WARP_OUT_ACCEL,
    FIST_EXPLOSION_OFFSET_LARGE, FIST_EXPLOSION_OFFSET_SMALL,
    FIST_EXPLOSION_SIZE_LARGE, FIST_EXPLOSION_SIZE_SMALL,
    POISON_DAMAGE_DELAY, POISON_DEBUFF_DURATION, POISON_SPEED_MULTIPLIER,
    BONUS_ITEM_SPEED, BONUS_ITEM_PROBABILITIES
)
from src.game.player import Player, PlayerBoost
from src.game.enemy import Enemy
from src.game.explosion import Explosion, BunkerRespawnEffect
from src.game.ufo import UFO
from src.game.Boss_small_1 import BossSmall1
from src.game.boss_small_2 import BossSmall2
from src.game.boss_small_3 import BossSmall3, PoisonGlob
from src.game.boss_small_4 import BossSmall4
from src.game.fist import Fist
from src.game.endboss import EndBoss
from src.game.bullet import Bullet
from src.game.laser_line import LaserLine, LaserSegment
from src.game.bunker import Bunker
from src.game.headerbar import HeaderBar
from src.game.powerup import PowerUp, Comet
from src.game.mainmenue import MainMenu
from src.game.endscreen import EndScreen
from src.game.led_controller import LedController
from src.game.explosion import Explosion
from src.game.boss_healthbar import BossHealthBar
from src.game.bonus_points import BonusPointItem, CollectEffect

def get_image(sheet, x, y, width, height):
    """
    Helper function to extract a single sprite from a spritesheet.
    Creates a new surface with alpha channel and blits the specified region onto it.
    """
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    image.blit(sheet, (0, 0), (x, y, width, height))
    return image.convert_alpha()

class Game:
    """
    Main Game class handling the core game loop, states, rendering, and logic updates.
    """
    # Define possible game states
    STATE_MENU = "menu"
    STATE_PLAYING = "playing"
    STATE_GAME_OVER = "game_over"
    STATE_VICTORY = "victory"
    STATE_LEVEL_CLEARED = "level_cleared"

    def __init__(self):
        """Initializes the game window, audio, states, backgrounds, and required game assets."""
        pygame.init()
        pygame.mixer.init()

        # External LED controller setup for physical cabinet effects
        self.leds = LedController("ws://localhost:8765")
        self.leds.attract_pause()
        self.warning_led_active = False
        
        # Hide mouse cursor for arcade/fullscreen experience
        pygame.mouse.set_visible(False)

        # Leaderboard and highscore variables
        self.player_name = ""
        self.selected_key_coords = [0, 0]
        
        # Music tracks setup
        self.music_intro = ("assets/music/intro.mp3")
        self.music_level = ("assets/music/02 Pluto.mp3")
        self.music_boss = ("assets/music/03 Pluto Boss.mp3")
        
        # Sound effects setup
        self.laser_sound = pygame.mixer.Sound("assets/music/lasershot.mp3")
        self.enemy_explosion = pygame.mixer.Sound("assets/music/enemyexplosion.mp3")
        self.ufo_damage = pygame.mixer.Sound("assets/music/ufodamage.mp3")
        self.warning_sound = pygame.mixer.Sound("assets/music/warning.mp3")
        self.game_over = pygame.mixer.Sound("assets/music/gameover.mp3")
        self.warning_sound.set_volume(0.4)
        
        # Audio state tracking
        self.current_track = None
        self.music_playing = False
        self.warning_played = False 
        
        # Base game variables
        self.game_mode = "story"
        self.wave_number = 1
        
        # Display initialization: Get desktop resolution and set up full-screen
        info = pygame.display.Info()
        self.full_w, self.full_h = info.current_w, info.current_h
        self.display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.full_w, self.full_h = self.display.get_width(), self.display.get_height()
        
        # Internal drawing surface that scales up to the full screen
        self.game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen = self.game_surface
        pygame.display.set_caption("Space Invaders")
        
        self.level = 1
        self.planet_index = 0  
        
        # Parallax background initialization for all 5 levels
        self.level_backgrounds = {}
        for lvl in range(1, 6):
            layers = []
            for layer in range(PARALLAX_LAYERS):
                path = LEVEL_BACKGROUND_PATTERN.format(level=lvl, layer=layer)
                try:
                    img = pygame.image.load(path).convert()
                except Exception:
                    # Fallback to black if image is missing
                    img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    img.fill((0, 0, 0))
                layers.append(img)
            self.level_backgrounds[lvl] = layers
            
        # Background layer initialization for cinematic warp transitions
        self.transition_background = []
        for layer in range(PARALLAX_LAYERS):
            path = TRANSITION_BACKGROUND_PATTERN.format(layer=layer)
            try:
                img = pygame.image.load(path).convert()
            except Exception:
                img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                img.fill((0, 0, 0))
            self.transition_background.append(img)
            
        # Set current background info
        self.current_background_layers = self.level_backgrounds[self.level]
        self.layer_offsets = [INITIAL_SCROLL] * PARALLAX_LAYERS
        
        # Font and timer initialization
        self.font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 10)
        self.clock = pygame.time.Clock()
        
        # UI menus
        self.main_menu = MainMenu(self.font)
        self.end_screen = EndScreen(self.font)

        # Start game in menu state
        self.state = self.STATE_MENU
        self.running = True
        self.SCROLL = INITIAL_SCROLL
        self.MAX_LEVEL = 5
        
        # Load sliding background planet sprites
        from src.config.config import PLANET_PATTERN, PLANET_SCALE
        self.planets = {}
        self.planet_index = 0
        self.planet_y = 0
        self.planet_sliding = False
        
        for idx in range(self.MAX_LEVEL): 
            path = PLANET_PATTERN.format(idx=idx)
            try:
                img = pygame.image.load(path).convert_alpha()
            except Exception:
                img = pygame.Surface((200, 200), pygame.SRCALPHA)
            if PLANET_SCALE != 1.0:
                width = int(img.get_width() * PLANET_SCALE)
                height = int(img.get_height() * PLANET_SCALE)
                img = pygame.transform.scale(img, (width, height))
            self.planets[idx] = img

        # Initialize the first planet position (just above the screen)
        if 0 in self.planets:
            self.planet_y = -self.planets[0].get_height()
        else:
            self.planet_y = 0
            
        # Transition/Planet slide trackers
        self.planet_sliding = True
        self.next_planet_index = None
        self.next_planet_y = 0
        self.next_planet_sliding = False
        self.decel_normal_frames = 0
        self.bunker_transition_y = 0.0
        
        # Boss state and timers
        self.mini_boss_spawned = False
        self.level_cleared_timer = 0
        
        # Initialisiere Sprite-Groups
        self.miniboss_group = pygame.sprite.Group()
        self.boss_healthbar = None 
        self.bonus_items = pygame.sprite.Group() 
        
        # Cinematic transition state
        self.is_transition_active = False
        self.transition_state = None
        self.transition_timer = 0
        self.current_speed_factors = list(PARALLAX_SPEED_FACTORS)

    def _is_laser_line(self, obj):
        """Utility check to identify laser beam objects via the presence of hitboxes."""
        return hasattr(obj, "get_hitboxes")

    def handle_bunker_collision(self, bullet, bunker_group):
        """
        Handles physical collisions between projectiles and protective bunkers.
        Differentiates between normal bullets, large physical objects (fists/globs), and lasers.
        """
        # 1. Laser beam collision (Lasers instantly wipe out entire bunker structures)
        if self._is_laser_line(bullet) or isinstance(bullet, LaserSegment):
            hitboxes = bullet.get_hitboxes() if self._is_laser_line(bullet) else [bullet.rect]
            hit_any = False
            for b in list(bunker_group):
                # If any hitbox of the laser touches the bunker, destroy it
                if any(laser_rect.colliderect(b.rect) for laser_rect in hitboxes):
                    exp = Explosion(b.rect.centerx, b.rect.centery, size=96)
                    self.explosions.add(exp)
                    self.all_sprites.add(exp)
                    b.kill()
                    hit_any = True
            if hit_any:
                # Clear all remaining bunkers in the line of the laser and kill the laser segment
                for b in list(bunker_group):
                    exp = Explosion(b.rect.centerx, b.rect.centery, size=96)
                    self.explosions.add(exp)
                    self.all_sprites.add(exp)
                    b.kill()
                bullet.kill()
                return

        # 2. Normal projectile / physical object collision using pixel-perfect mask overlap
        hit_bunker = pygame.sprite.spritecollideany(
            bullet, bunker_group, pygame.sprite.collide_mask
        )
        if hit_bunker:
            # Special case: Fists and PoisonGlobs deal massive damage and generate special explosions
            if isinstance(bullet, Fist) or isinstance(bullet, PoisonGlob):
                # Generate large primary explosion slightly offset randomly
                offset_x1 = random.randint(-FIST_EXPLOSION_OFFSET_LARGE, FIST_EXPLOSION_OFFSET_LARGE)
                offset_y1 = random.randint(-FIST_EXPLOSION_OFFSET_LARGE, FIST_EXPLOSION_OFFSET_LARGE)
                exp1_x = hit_bunker.rect.centerx + offset_x1
                exp1_y = hit_bunker.rect.centery + offset_y1
                
                exp1 = Explosion(exp1_x, exp1_y, size=FIST_EXPLOSION_SIZE_LARGE)
                self.explosions.add(exp1)
                self.all_sprites.add(exp1)
                
                # Generate a smaller secondary explosion positioned roughly opposite to the first
                offset_x2 = -offset_x1 + random.randint(-FIST_EXPLOSION_OFFSET_SMALL, FIST_EXPLOSION_OFFSET_SMALL)
                offset_y2 = -offset_y1 + random.randint(-FIST_EXPLOSION_OFFSET_SMALL, FIST_EXPLOSION_OFFSET_SMALL)
                exp2_x = hit_bunker.rect.centerx + offset_x2
                exp2_y = hit_bunker.rect.centery + offset_y2
                
                exp2 = Explosion(exp2_x, exp2_y, size=FIST_EXPLOSION_SIZE_SMALL)
                self.explosions.add(exp2)
                self.all_sprites.add(exp2)
                
                # If it's a PoisonGlob, destroy it but don't spawn a puddle on the bunker
                if isinstance(bullet, PoisonGlob):
                    bullet.puddle_group = False 
                    bullet.has_spawned = True
                    bullet.kill()
                # Apply heavy damage
                hit_bunker.take_damage()
            else:
                # Normal bullet damage application
                damage = getattr(bullet, "damage", 1)
                for _ in range(damage):
                    hit_bunker.take_damage()
                    
            # Check if bunker was completely destroyed to trigger final explosion
            if not hit_bunker.alive():
                exp = Explosion(hit_bunker.rect.centerx, hit_bunker.rect.centery, size=96)
                self.explosions.add(exp)
                self.all_sprites.add(exp)
                
            # If the bullet has a piercing stat, reduce it instead of instant kill
            if hasattr(bullet, "pierce"):
                bullet.pierce -= 1
                if bullet.pierce <= 0:
                    bullet.kill()
            else:
                bullet.kill()

    def rebuild_bunkers(self):
        """
        Called when a 'Bunker PowerUp' is collected.
        Destroys any remnants of old bunkers and spans 4 fresh ones with visual effects.
        """
        # Destroy current active bunkers with an explosion effect
        for b in self.bunkers:
            explosion = Explosion(b.rect.centerx, b.rect.centery, size=96)
            self.explosions.add(explosion)
            self.all_sprites.add(explosion)
            b.kill()
        
        # Spawn new ones based on predefined locations and angles
        angles = [0, 90, 180, 270]
        variants = ["satellite", "satellit2", "satellit3", "satellit4"]
        for i, variant in enumerate(variants):
            x_pos = 250 + (i * 190)
            new_bunker = Bunker(x_pos, SCREEN_HEIGHT - 120, variant=variant, angle=angles[i])
            self.bunkers.add(new_bunker)
            self.all_sprites.add(new_bunker)
            
            # Add electrical visual effect marking their respawn
            respawn_effect = BunkerRespawnEffect(x_pos, SCREEN_HEIGHT - 120, size=128)
            self.explosions.add(respawn_effect)
            self.all_sprites.add(respawn_effect)

    def _reset(self):
        """
        Wipes the entire game board and resets variables for a fresh game or retry.
        """
        # Reset LEDs
        self.leds.send_effect("A", "pulse", 99, 0, 255, 0, speed=50, repeat=0, priority=1)
        self.warning_played = False
        self.warning_led_active = False

        # Reset primary stats
        self.score = 0
        self.level = TEST_START_LEVEL
        self.lives = 3
        self.wave_number = 1
        self.poison_tick_timer = POISON_DAMAGE_DELAY

        self._endless_wave_spawned = True
        self.player_shots = 0
        
        # Pre-initialize player to avoid NoneType errors during group cleanup
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
        self.player.current_scale = 1.0 
        self.bunker_transition_y = 0.0  
        
        # 3. Sprite Group Cleanup
        if hasattr(self, 'miniboss_group'):
            for boss in self.miniboss_group:
                boss.kill()
        self.miniboss_group = pygame.sprite.Group()
        
        if hasattr(self, 'puddle_group'):
            for puddle in self.puddle_group:
                puddle.kill()

        self.all_sprites = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.puddle_group = pygame.sprite.Group()
        self.bunkers = pygame.sprite.Group()
        self.ufo_group = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.comets = pygame.sprite.Group()
        self.bonus_items = pygame.sprite.Group() 
        self.headerbar = pygame.sprite.GroupSingle()

        # Properly initialize main player character
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
        self.player.current_scale = 1.0 
        self.player.exact_y = float(SCREEN_HEIGHT - TRANSITION_PLAYER_Y_NORMAL_OFFSET)
        self.player_invuln_timer = 0
        
        # Setup player engine boost effect
        self.player_boost = PlayerBoost(self.player)
        self.all_sprites.add(self.player_boost)
        self.all_sprites.add(self.player)

        # Reset environmental variables
        self.SCROLL = INITIAL_SCROLL
        self.planet_index = 0  
        self.planet_sliding = True
        if 0 in self.planets:
            self.planet_y = -self.planets[0].get_height()
        
        self.current_background_layers = self.level_backgrounds[self.level]
        self.layer_offsets = [INITIAL_SCROLL] * PARALLAX_LAYERS
        self.bunker_transition_y = 0.0

        # Generate the first wave of enemies
        self.create_enemy_wave()
        self.enemy_direction = 1
        self.enemy_move_down = 10
        self.headerbar.add(HeaderBar(self.screen, self.font))
        
        # Generate the starting set of bunkers
        angles = [0, 90, 180, 270]
        variants = ["satellite", "satellit2", "satellit3", "satellit4"]
        for i, variant in enumerate(variants):
            x_pos = 250 + (i * 190)
            self.bunkers.add(Bunker(x_pos, SCREEN_HEIGHT - 120, variant=variant, angle=angles[i]))

        # Reset spawn timers
        self.ufo_timer = int(UFO_SPAWN_TIME * FPS)
        self.mini_boss_spawned = False
        self.boss_healthbar = None 
        
        # Reset transition engine states
        self.level_cleared_timer = 0
        self.is_transition_active = False
        self.transition_state = None
        self.transition_timer = 0
        self.current_speed_factors = list(PARALLAX_SPEED_FACTORS)
        self.next_planet_index = None
        self.next_planet_y = 0
        self.next_planet_sliding = False
        self.decel_normal_frames = 0

    def _present(self):
        """
        Scales the 1080x1080 internal game surface (self.game_surface) and draws it
        onto the user's actual screen resolution, maintaining aspect ratio.
        """
        self.display.fill((0, 0, 0))
        sw, sh = self.display.get_size()
        scale = min(sw / SCREEN_WIDTH, sh / SCREEN_HEIGHT)
        nw, nh = int(SCREEN_WIDTH * scale), int(SCREEN_HEIGHT * scale)
        scaled_surf = pygame.transform.scale(self.game_surface, (nw, nh))
        # Center the scaled surface on the screen (adds black bars if monitor isn't square)
        self.display.blit(scaled_surf, ((sw - nw) // 2, (sh - nh) // 2))
        pygame.display.flip()

    def _spawn_bonus_item(self):
        """Spawnt ein zufälliges Bonus Item (100, 200, 300, 400) oben am Bildschirm."""
        roll = random.random()
        cumulative = 0.0
        chosen_points = 100
        
        for points, chance in BONUS_ITEM_PROBABILITIES.items():
            cumulative += chance
            if roll <= cumulative:
                chosen_points = points
                break
                
        # Zufällige X-Position im spielbaren Bereich
        x_pos = random.randint(100, SCREEN_WIDTH - 100)
        item = BonusPointItem(x_pos, -50, BONUS_ITEM_SPEED, chosen_points)
        
        self.bonus_items.add(item)
        self.all_sprites.add(item)

    def _run_transition(self):
        """
        Executes the hyperspace cinematic transition sequence between levels.
        It uses a sub-state machine (amplify -> hold -> decel_to_thresh -> decel_to_normal)
        to manipulate parallax scroll speeds, player scaling, and bunker offsets.
        """
        # Initialization phase: start the acceleration
        if not self.is_transition_active:
            self.is_transition_active = True
            self.transition_state = "amplify"
            # Send warp LED effect
            self.leds.send_effect("A", "chase", 0, 255, 255, 255, speed=22, repeat=13, priority=2)
            self.current_speed_factors = list(PARALLAX_SPEED_FACTORS)
            self.decel_normal_frames = 0
            return

        # Ramping helper closures
        def _ramp_up(factors, step, max_factor):
            return [min(f + step, max_factor) for f in factors]

        def _ramp_down(factors, step, target):
            return [max(f - step, target) for f in factors]

        # Determine target scaling for player and bunkers based on the current sequence state
        if self.transition_state == "amplify":
            target_scale = TRANSITION_PLAYER_SCALE_MAX   
            target_bunker_y = TRANSITION_BUNKER_Y_DOWN 
        elif self.transition_state in ("hold", "decel_to_thresh"):
            target_scale = TRANSITION_PLAYER_SCALE_MAX
            target_bunker_y = TRANSITION_BUNKER_Y_DOWN
        else:
            # Revert to normal scales as we arrive at the new level
            target_scale = TRANSITION_PLAYER_SCALE_NORMAL   
            target_bunker_y = TRANSITION_BUNKER_Y_UP  

        # Apply easing algorithms to smoothly interpolate current scales/offsets towards targets
        self.player.current_scale += (target_scale - self.player.current_scale) * TRANSITION_PLAYER_SCALE_EASING
        self.bunker_transition_y += (target_bunker_y - self.bunker_transition_y) * TRANSITION_BUNKER_EASING
        for b in self.bunkers:
            b.transition_y = self.bunker_transition_y

        # Phase 1: Accelerate backgrounds to hyper-speed
        if self.transition_state == "amplify":
            self.current_speed_factors = _ramp_up(
                self.current_speed_factors, AMPLIFY_STEP, AMPLIFY_MAX_FACTOR
            )
            # Once max speed reached, swap normal backgrounds for star streak backgrounds
            if all(abs(f - AMPLIFY_MAX_FACTOR) < 1e-5 for f in self.current_speed_factors):
                self.current_background_layers = self.transition_background
                self.transition_state = "hold"
                self.transition_timer = TRANSITION_HOLD_FRAMES
            return

        # Phase 2: Hold max speed (hyperspace travel)
        if self.transition_state == "hold":
            # FIX: Items spawnen jetzt früher, damit sie Zeit zum Fallen haben!
            # Item 1 ganz am Anfang der Flugphase
            if self.transition_timer == TRANSITION_HOLD_FRAMES - 10:
                self._spawn_bonus_item()
                
            # Item 2 in der Mitte der Flugphase
            if self.transition_timer == TRANSITION_HOLD_FRAMES - 90:
                self._spawn_bonus_item()
                
            self.transition_timer -= 1
            if self.transition_timer <= 0:
                self.transition_state = "decel_to_thresh"
            return

        # Phase 3: Initial heavy deceleration while still showing star streaks
        if self.transition_state == "decel_to_thresh":
            self.current_speed_factors = _ramp_down(
                self.current_speed_factors, DECEL_STEP, THRESHOLD_FACTOR
            )
            if all(abs(f - THRESHOLD_FACTOR) < 1e-5 for f in self.current_speed_factors):
                self.transition_state = "decel_to_normal"
            return

        # Phase 4: Final soft deceleration back into regular level backgrounds
        if self.transition_state == "decel_to_normal":
            self.decel_normal_frames += 1
            
            # Start sliding the next planet into view slightly before deceleration finishes
            if self.decel_normal_frames == 160 and not self.next_planet_sliding:
                next_idx = self.planet_index + 1
                if next_idx in self.planets:
                    self.next_planet_index = next_idx
                    self.next_planet_y = -self.planets[next_idx].get_height()
                    self.next_planet_sliding = True
            
            # Swap visuals over to the destination level
            if self.current_background_layers != self.level_backgrounds[self.level]:
                self.current_background_layers = self.level_backgrounds[self.level]

            if self.transition_timer > 0:
                self.transition_timer -= 1
                return

            # Easing calculations to gradually drop layer speeds individually
            new_factors = []
            all_reached = True
            for i, current_f in enumerate(self.current_speed_factors):
                target_f = PARALLAX_SPEED_FACTORS[i]
                if current_f > target_f:
                    next_f = max(current_f - DECEL_STEP, target_f)
                else:
                    next_f = target_f
                
                new_factors.append(next_f)
                if abs(next_f - target_f) > 1e-5:
                    all_reached = False
                    
            self.current_speed_factors = new_factors

            # Transition fully complete, start next gameplay stage
            if all_reached:
                self._spawn_miniboss()
                self.mini_boss_spawned = True
                self.is_transition_active = False
                self.transition_state = None
                self.state = self.STATE_PLAYING
                
                # Assign the newly arrived planet
                if self.next_planet_sliding and self.next_planet_index is not None:
                    self.planet_index = self.next_planet_index
                    self.planet_y = self.next_planet_y
                    self.planet_sliding = self.next_planet_sliding
                else:
                    self.planet_index += 1
                    if self.planet_index in self.planets:
                        self.planet_y = -self.planets[self.planet_index].get_height()
                    else:
                        self.planet_y = 0
                    self.planet_sliding = True
                    
                self.next_planet_index = None
                self.next_planet_sliding = False
                self.current_speed_factors = list(PARALLAX_SPEED_FACTORS)
            return

    def _spawn_ufo(self):
        """Spawns the red bonus saucer at the top of the screen."""
        ufo = UFO()
        self.ufo_group.add(ufo)
        self.all_sprites.add(ufo)

    def _spawn_miniboss(self):
        """
        Dynamically initializes and spawns the specific boss associated with the current level.
        Applies health/speed modifiers based on the MINIBOSS_SETTINGS dictionary.
        """
        boss_map = {
            1: BossSmall1,
            2: BossSmall2,
            3: BossSmall3,
            4: BossSmall4,
            5: EndBoss,
        }
        boss_cls = boss_map.get(self.level, BossSmall1)
        settings = MINIBOSS_SETTINGS.get(self.level, MINIBOSS_SETTINGS[1])
        boss = boss_cls(health=settings.get("health", 3), speed=settings.get("speed", 2))
        
        # Apply any extra specific class variables to the instantiated boss
        extra = getattr(boss, "extra_settings", None)
        if isinstance(extra, dict):
            for k, v in extra.items():
                setattr(boss, k, v)
        
        self.miniboss_group.add(boss)
        self.all_sprites.add(boss)
        
        # Ensures that fist projectiles (Level 1/5) are rendered on top of the boss
        if hasattr(boss, "fist_group"):
            self.all_sprites.add(boss.fist_group)
            
        self.boss_healthbar = BossHealthBar(boss)

    def _play_music(self, trak_path, volume = 0.2):
        """Helper to swap audio tracks smoothly without restarting already playing tracks."""
        if self.current_track != trak_path:
            pygame.mixer.music.load(trak_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
            self.current_track = trak_path

    def create_enemy_wave(self):
        """
        Populates the board with standard enemies based on game mode.
        Story mode pulls from predefined maps, Endless mode scales difficulty infinitely.
        """
        if self.game_mode == "story":
            settings = ENEMY_WAVE_SETTINGS.get(self.level, ENEMY_WAVE_SETTINGS[1])
            rows = settings["rows"]
            cols = settings["cols"]
            self.enemy_speed = settings.get("speed", ENEMY_SPEED)
            self.enemy_shoot_chance = settings.get("shoot_chance", ENEMY_SHOOT_CHANCE)
        else:
            # Procedural scaling for endless survival mode
            rows = min(6, 3 + (self.wave_number // 5)) 
            cols = 8
            self.enemy_speed = ENEMY_SPEED + (self.wave_number * 0.2)
            self.enemy_shoot_chance = ENEMY_SHOOT_CHANCE + (self.wave_number * 0.005)
        
        # Enemy grid generation
        x_margin, y_margin = 50, 100
        spacing_x, spacing_y = 80, 60
        for row in range(int(rows)):
            for col in range(int(cols)):
                x = x_margin + col * spacing_x
                y = y_margin + row * spacing_y
                enemy = Enemy(x, y, row)
                enemy.speed = int(self.enemy_speed)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

    def _handle_enemy_movement(self):
        """
        Calculates group movements for regular enemies (Space Invaders style).
        Moves them horizontally, then drops them down a row when hitting a screen edge.
        """
        move_sideways = True
        for enemy in self.enemies:
            # Edge detection based on current travel direction
            if self.enemy_direction == 1 and enemy.rect.right >= SCREEN_WIDTH - 10:
                move_sideways = False
                break
            if self.enemy_direction == -1 and enemy.rect.left <= 10:
                move_sideways = False
                break
                
        if not move_sideways:
            # Shift entire block downward and invert horizontal velocity
            for enemy in self.enemies:
                enemy.rect.y += self.enemy_move_down
            self.enemy_direction *= -1
        else:
            # Continue horizontal travel
            for enemy in self.enemies:
                enemy.move(self.enemy_direction)

    def _enemy_shooting(self):
        """Randomly selects standard enemies to fire bullets downward."""
        for enemy in self.enemies:
            if random.random() < self.enemy_shoot_chance:
                bullet = enemy.shoot()
                self.enemy_bullets.add(bullet)
                self.all_sprites.add(bullet)

    def _check_collisions(self):
        """
        The central collision detection and resolution engine.
        Handles taking damage, dealing damage, piercing logic, powerup collection,
        and state changes (Game Over) across all object types.
        """
        # Decrease invulnerability timer for the player
        if hasattr(self, 'player_invuln_timer') and self.player_invuln_timer > 0:
            self.player_invuln_timer -= 1
            
        # 1. Player Bullets vs Regular Enemies
        hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, True, False)
        if hits:
            self.enemy_explosion.play()
            # LED effect for enemy kill
            for seg in range(1, 5):
                self.leds.send_effect("A", "blink", seg, 200, 255, 0, speed=1, repeat=10, priority=2)
                
            for enemy, bullets in hits.items():
                explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                self.explosions.add(explosion)
                self.all_sprites.add(explosion)
                
                # Resolve player bullet piercing 
                for b in bullets:
                    b.pierce -= 1
                    if b.pierce <= 0:
                        b.kill()
                        
                # Randomly determine if the enemy drops a powerup upon death (disabled during boss fights)
                if not self.mini_boss_spawned:
                    roll = random.random()
                    cumulative = 0.0
                    for p_type, chance in POWERUP_DROP_CHANCES.items():
                        cumulative += chance
                        if roll < cumulative:
                            powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, POWERUP_FALL_SPEED, p_type)
                            self.powerups.add(powerup)
                            self.all_sprites.add(powerup)
                            break
            self.score += len(hits) * 100
        
        # 2. Player Bullets vs UFO
        bonushits = pygame.sprite.groupcollide(self.ufo_group, self.player_bullets, True, False)
        if bonushits:
            for seg in range(1, 6):
                self.leds.send_effect("A", "blink", seg, 255, 0, 0, speed=2, repeat=2, priority=4)
            for ufo, bullets in bonushits.items():
                self.score += random.choice(UFO_SCORE_OPTIONS)
                explosion = Explosion(ufo.rect.centerx, ufo.rect.centery, size=48)
                self.explosions.add(explosion)
                self.all_sprites.add(explosion)
                for b in bullets:
                    b.pierce -= 1
                    if b.pierce <= 0:
                        b.kill()

        player_hit = False
        
        # 3. Enemy Beam/Laser vs Player
        laser_objects = []
        for boss in self.miniboss_group:
            if hasattr(boss, "laser_lines"):
                laser_objects.extend(list(boss.laser_lines))
        for bullet in list(self.enemy_bullets):
            if self._is_laser_line(bullet) and bullet not in laser_objects:
                laser_objects.append(bullet)
                
        for laser in laser_objects:
            if any(self.player.rect.colliderect(hitbox) for hitbox in laser.get_hitboxes()):
                player_hit = True
                self.lives -= getattr(laser, "damage", 1)  
                self.ufo_damage.play()
                laser.kill()
            
        # 4. Standard Enemy Projectiles vs Player
        for bullet in list(self.enemy_bullets):
            if self._is_laser_line(bullet):
                continue 
            if pygame.sprite.collide_rect(bullet, self.player):
                player_hit = True
                dmg = getattr(bullet, "damage", 1)
                self.lives -= dmg
                
                # Special explosion effect for the large Boss 1/5 fist
                if isinstance(bullet, Fist):
                    exp = Explosion(bullet.rect.centerx, bullet.rect.centery, size=64)
                    self.explosions.add(exp)
                    self.all_sprites.add(exp)
                    
                bullet.kill()

        # 5. Poison Puddle Area Denial (Damage over time)
        in_puddle = False
        for puddle in list(self.puddle_group):
            active_rect = getattr(puddle, 'hitbox', puddle.rect)
            if active_rect.colliderect(self.player.rect):
                in_puddle = True
                break
                
        if in_puddle:
            # Track how long the player has stood in the puddle
            if not hasattr(self, 'poison_tick_timer'):
                self.poison_tick_timer = POISON_DAMAGE_DELAY
            self.poison_tick_timer -= 1
            
            # Apply damage and debuff if player remains in puddle too long
            if self.poison_tick_timer <= 0:
                self.lives -= 1
                player_hit = True
                self.poison_tick_timer = 300
                
                # Apply slow and weapon-lock debuffs
                self.player.poison_debuff_timer = POISON_DEBUFF_DURATION
                self.player.speed = int(self.player.base_speed * POISON_SPEED_MULTIPLIER)
        else:
            # Reset timer instantly when leaving the puddle
            self.poison_tick_timer = POISON_DAMAGE_DELAY

        # Resolve Player Hit Event (Blinks LEDs or ends game)
        if player_hit:
            if self.lives > 0:
                for seg in range(1, 5):
                    self.leds.send_effect("A", "blink", seg, 255, 0, 0, speed=1, repeat=10, priority=2)
            else:
                self.game_over.play()
                self.leds.send_effect("A", "wipe", 99, 255, 0, 0, speed=50, repeat=1, priority=4)
                
                explosion = Explosion(self.player.rect.centerx, self.player.rect.centery)
                self.explosions.add(explosion)
                self.all_sprites.add(explosion)
                self.player.kill()
                self.player_boost.kill()
                self.state = self.STATE_GAME_OVER

        # 6. Player Bullets vs MiniBoss
        for boss in list(self.miniboss_group):
            hits = pygame.sprite.spritecollide(boss, self.player_bullets, False)
            for b in hits:
                hit_explosion = Explosion(boss.rect.centerx, boss.rect.centery, size=48)
                self.explosions.add(hit_explosion)
                for seg in range(1, 6):
                    self.leds.send_effect("A", "blink", seg, 255, 255, 255, speed=1, repeat=2, priority=3)
                self.all_sprites.add(hit_explosion)
                boss.hit()
                # BossSmall2 drops a specific bunker powerup when defeated
                if not boss.alive() and isinstance(boss, BossSmall2):
                    powerup = PowerUp(boss.rect.centerx, boss.rect.centery, POWERUP_FALL_SPEED, "bunker")
                    self.powerups.add(powerup)
                    self.all_sprites.add(powerup)
                b.pierce -= 1
                if b.pierce <= 0:
                    b.kill()

        # 7. Enemy physically reaches player's position vertically (Instant Game Over condition)
        for enemy in self.enemies:
            if enemy.rect.bottom >= self.player.rect.top:
                self.state = self.STATE_GAME_OVER

        # 8. Player collects Powerups
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        if powerup_hits:
            self.leds.send_effect("A", "blink", 1, 0, 255, 255, speed=10, repeat=5, priority=5)
            for pu in powerup_hits:
                
                # --- NEU: Collect-Effekt auch für normale Items spawnen ---
                effect = CollectEffect(pu.rect.centerx, pu.rect.centery)
                self.explosions.add(effect)
                self.all_sprites.add(effect)
                # ----------------------------------------------------------
                
                if pu.type == "comet":
                    # Spawns a friendly attack entity traveling across the screen
                    comet = Comet(SCREEN_WIDTH, COMET_SPEED, COMET_ROTATION_SPEED, TIE_FIGHTER_SPEED, TIE_FIGHTER_ROTATION_SPEED, TIE_FIGHTER_SIZE)
                    self.comets.add(comet)
                    self.all_sprites.add(comet)
                elif pu.type == "bunker":
                    self.rebuild_bunkers()
                elif pu.type == "hp":
                    self.lives += 1
                elif pu.type == "speed":
                    self.player.speed = int(self.player.base_speed * POWERUP_SPEED_MULTIPLIER)
                    self.player.speed_timer = FPS * POWERUP_SPEED_DURATION
                elif pu.type == "doubleshot":
                    self.player.weapon_type = "double"
                    self.player.weapon_timer = FPS * POWERUP_DOUBLESHOT_DURATION
                elif pu.type == "trippleshot":
                    self.player.weapon_type = "triple"
                    self.player.weapon_timer = FPS * POWERUP_TRIPLESHOT_DURATION

        # 9. Comet vs Enemy collision
        for comet in self.comets:
            comet_enemy_hits = pygame.sprite.spritecollide(comet, self.enemies, True)
            if comet_enemy_hits:
                self.enemy_explosion.play()
                for enemy in comet_enemy_hits:
                    explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                    self.explosions.add(explosion)
                    self.all_sprites.add(explosion)
                    self.score += 100

        # 10. Comet vs Boss Collision
        for boss in list(self.miniboss_group):
            comet_boss_hits = pygame.sprite.spritecollide(boss, self.comets, True)
            if comet_boss_hits:
                self.enemy_explosion.play()
                for comet in comet_boss_hits:
                    explosion = Explosion(comet.rect.centerx, comet.rect.centery, size=128)
                    self.explosions.add(explosion)
                    self.all_sprites.add(explosion)

    def _draw_hud(self):
        """Draws current points and lives to top corners (Legacy HUD)."""
        score_surf = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        lives_surf = self.font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        self.screen.blit(score_surf, (10, 10))
        self.screen.blit(lives_surf, (SCREEN_WIDTH - lives_surf.get_width() - 10, 10))

    def _draw_planet(self):
        """
        Calculates the scrolling displacement and renders the large decorative planet 
        asset in the background, beneath all gameplay elements.
        """
        planet_img = self.planets.get(self.planet_index)
        if not planet_img:
            return
        rect = planet_img.get_rect()
        rect.centerx = SCREEN_WIDTH // 2.5
        base_target_y = SCREEN_HEIGHT 
        
        try:
            scroll_offset = self.layer_offsets[1] * PLANET_SCROLL_FACTOR
        except Exception:
            scroll_offset = 1
            
        target_y = int(base_target_y + scroll_offset)
        normal_target_y = int(base_target_y + scroll_offset)

        # Handle planet panning up into frame during transitions
        if getattr(self, "planet_sliding", False):
            if self.is_transition_active:
                slide_speed = BASE_SCROLL_SPEED * self.current_speed_factors[0]
            else:
                slide_speed = 0.35
            self.planet_y += slide_speed
            if not self.is_transition_active and self.planet_y >= normal_target_y:
                self.planet_y = normal_target_y
                self.planet_sliding = False
        else:
            if not self.is_transition_active:
                self.planet_y = normal_target_y

        if self.planet_y > SCREEN_HEIGHT + planet_img.get_height():
            pass  

        rect.top = int(self.planet_y)
        self.screen.blit(planet_img, rect)
        
        # Handle the secondary planet fading in while arriving to new level
        if getattr(self, "next_planet_sliding", False) and self.next_planet_index is not None:
            next_planet_img = self.planets.get(self.next_planet_index)
            if next_planet_img:
                next_rect = next_planet_img.get_rect()
                next_rect.centerx = SCREEN_WIDTH // 2.5
                
                if self.is_transition_active:
                    next_slide_speed = BASE_SCROLL_SPEED * self.current_speed_factors[0]
                else:
                    next_slide_speed = 0.35
                
                self.next_planet_y += next_slide_speed
                
                if not self.is_transition_active:
                    try:
                        next_scroll_offset = self.layer_offsets[1] * PLANET_SCROLL_FACTOR
                    except Exception:
                        next_scroll_offset = 1
                    next_normal_target_y = int(base_target_y + next_scroll_offset)
                    if self.next_planet_y >= next_normal_target_y:
                        self.next_planet_y = next_normal_target_y
                
                if self.next_planet_y <= SCREEN_HEIGHT + next_planet_img.get_height():
                    next_rect.top = int(self.next_planet_y)
                    self.screen.blit(next_planet_img, next_rect)

    def _draw_end_screen(self):
        """Passes context data to the EndScreen class to render the Game Over or Victory panel."""
        is_victory = (self.state == self.STATE_VICTORY)
        
        self.end_screen.draw(
            self.screen, 
            self.state, 
            self.score, 
            self.player_name,
            self.selected_key_coords,
            is_victory=is_victory,
            game_mode=self.game_mode,
            wave_number=self.wave_number
        )

    def advance_level(self):
        """Handles story progression upon killing a boss and surviving the cinematic flight."""
        self.level += 1
        if self.level > self.MAX_LEVEL:
            # Game complete trigger
            self.leds.send_effect("A", "blink", 99, 255, 255, 0, speed=5, repeat=10, priority=3)
            self.state = self.STATE_VICTORY
            return
            
        # Reset systems for next level
        self.headerbar.sprite.set_level(self.level)
        self.mini_boss_spawned = False
        
        self.boss_healthbar = None # Healthbar beim Levelwechsel löschen
        self.bonus_items.empty() # Auch restliche Bonuspunkte sicherheitshalber löschen
        self.miniboss_group.empty()
        self.enemies.empty()
        self.current_background_layers = self.level_backgrounds[self.level]
        self.layer_offsets = [INITIAL_SCROLL] * PARALLAX_LAYERS
        self.create_enemy_wave()
        
        self.ufo_timer = int(UFO_SPAWN_TIME * FPS)
        self.player_shots = 0
        self.level_cleared_timer = 0
        self.state = self.STATE_PLAYING
        self.leds.send_effect("A", "pulse", 99, 0, 255, 0, speed=50, repeat=0, priority=1)
        
        self.transitioning_back_timer = 2 * FPS 

    def increase_level(self):
        """Forces level skip shortcut/debug"""
        if self.mini_boss_spawned:
            self.level += 1
            if self.level > self.MAX_LEVEL:
                self.state = self.STATE_VICTORY
                return
            self.headerbar.sprite.set_level(self.level)
            self.current_background_layers = self.level_backgrounds[self.level]
            self.layer_offsets = [INITIAL_SCROLL] * PARALLAX_LAYERS

    def run(self):
        """
        The main infinite operational loop containing event polling,
        logic/positional updates, and frame rendering.
        """
        self.led_heartbeat_timer = 0

        while True:
            # Lock loop execution speed to frames per second defined in config
            self.clock.tick(FPS)
            
            # Send periodic standby pulses to the arcade cabinet LEDs
            self.led_heartbeat_timer -= 1
            if self.led_heartbeat_timer <= 0:
                self.leds.send_effect("A", "pulse", 99, 0, 255, 0, speed=50, repeat=0, priority=1)
                self.led_heartbeat_timer = 1
            
            # Global event and keyboard polling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Global forced exit shortcut
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                
                # Input handling for Main Menu interactions
                if self.state == self.STATE_MENU:
                    self._play_music(self.music_intro, 0.7)
                    self.leds.send_effect("A", "pulse", 99, 0, 255, 0, speed=20, repeat=10, priority=1)
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_1:
                            self.game_mode = "story"
                            self._reset()
                            self.state = self.STATE_PLAYING
                        elif event.key == pygame.K_2:
                            self.game_mode = "endless"
                            self.wave_number = 1
                            self._reset()
                            self.state = self.STATE_PLAYING
                        
                # Input handling during actual gameplay
                elif self.state == self.STATE_PLAYING: 
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            bullet = self.player.shoot()
                            if bullet:
                                self.laser_sound.play()
                                self.player_bullets.add(bullet)
                                self.all_sprites.add(bullet)
                                self.player_shots += 1
                        elif event.key == pygame.K_r:
                            self._reset()
                
                # Allows restart mid-flight during the cleared level animation
                elif self.state == self.STATE_LEVEL_CLEARED:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self._reset()
                            self.state = self.STATE_PLAYING

                # Input handling for End Screen leaderboards (virtual keyboard)
                elif self.state in (self.STATE_GAME_OVER, self.STATE_VICTORY):
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.player_name = ""
                            self._reset()
                            self.state = self.STATE_PLAYING

                        # Virtual keyboard positional movement logic
                        elif event.key == pygame.K_LEFT:
                            self.selected_key_coords[0] = (self.selected_key_coords[0] - 1) % 7
                        elif event.key == pygame.K_RIGHT:
                            self.selected_key_coords[0] = (self.selected_key_coords[0] + 1) % 7
                        elif event.key == pygame.K_UP:
                            self.selected_key_coords[1] = (self.selected_key_coords[1] - 1) % 4
                        elif event.key == pygame.K_DOWN:
                            self.selected_key_coords[1] = (self.selected_key_coords[1] + 1) % 4
                        
                        # Apply currently selected virtual key
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            col, row = self.selected_key_coords
                            char = self.end_screen.keys[row][col]

                            if char == '<':
                                self.player_name = self.player_name[:-1] 
                            elif char == 'OK':
                                if len(self.player_name) > 0:
                                    self.save_highscore(self.game_mode)
                                    self.player_name = ""
                                    self.state = self.STATE_MENU 
                            else:
                                if len(self.player_name) < 12: 
                                    self.player_name += char
                        

            # Render Logic depending on application state
            if self.state == self.STATE_MENU:
                self._draw_planet()
                self.main_menu.draw(self.screen)
                self._present()

            elif self.state == self.STATE_PLAYING:
                # Active gameplay stage logic
                if self.mini_boss_spawned:
                    self._play_music(self.music_boss, 0.7)
                else:
                    self._play_music(self.music_level, 0.7)

                # Return the player smoothly to the default Y axis after flying in transition
                target_y = SCREEN_HEIGHT - TRANSITION_PLAYER_Y_NORMAL_OFFSET 
                if abs(self.player.exact_y - target_y) > 0.5:
                    self.player.exact_y += (target_y - self.player.exact_y) * TRANSITION_PLAYER_EASING_PLAYING
                
                # Execute primary player behaviors
                keys = pygame.key.get_pressed()
                self.player.move(keys, SCREEN_WIDTH)
                self.player.update_buffs()      
                self.player_boost.update(is_hyperboosting=False)  

                # Update state of all physical entities in the scene
                self.player_bullets.update()
                self.enemy_bullets.update()
                self.bunkers.update()
                self.miniboss_group.update(self.player,
                               self.all_sprites,
                               self.enemy_bullets,
                               self.explosions,
                               SCREEN_WIDTH,
                               SCREEN_HEIGHT,
                               self.puddle_group)
                self.puddle_group.update()
                self.explosions.update()
                self.powerups.update(SCREEN_HEIGHT)
                self.comets.update(SCREEN_WIDTH, SCREEN_HEIGHT)
                self.enemies.update()
                self.ufo_group.update()
                self.bonus_items.update() # NEU: Bonus Items updaten, falls sie noch ins Level ragen
                
                # Perform continuous collision checks for bunkers against active projectiles
                for bullet in self.player_bullets:
                    self.handle_bunker_collision(bullet, self.bunkers)
                for bomb in self.enemy_bullets:
                    self.handle_bunker_collision(bomb, self.bunkers)

                # Execute enemy behaviors
                self._handle_enemy_movement()
                self._enemy_shooting()
                
                # Control the mystery UFO appearance
                self.ufo_timer -= 1
                if self.ufo_timer <= 0 or self.player_shots >= UFO_SHOT_THRESHOLD:
                    self._spawn_ufo()
                    self.ufo_timer = int(UFO_SPAWN_TIME * FPS)
                    self.player_shots = 0
                
                # Process core interactions (damage, scores, etc)
                self._check_collisions()
                
                # Determine state flow based on remaining enemies and active explosions
                if not self.enemies and not self.explosions:
                    if self.game_mode == "story":
                        # Transition to cinematic state if wave cleared, progress level if boss cleared
                        if not self.mini_boss_spawned:
                            self.state = self.STATE_LEVEL_CLEARED
                            self.level_cleared_timer = 5 * FPS
                        elif self.mini_boss_spawned and not self.miniboss_group:
                            self.advance_level()
                    elif self.game_mode == "endless":
                        # Instantly loop to the next wave and increase difficulty variables in Endless mode
                        if not getattr(self, '_endless_wave_spawned', False):
                            self.wave_number += 1
                            self.create_enemy_wave()
                            self.score += 500
                            self._endless_wave_spawned = True
                            
                            # Shift backgrounds every 5 waves
                            if self.wave_number % 5 == 0:
                                self.planet_index = (self.planet_index + 1) % self.MAX_LEVEL
                                if self.planet_index in self.planets:
                                    self.planet_y = -self.planets[self.planet_index].get_height()
                                    self.planet_sliding = True
                                self.current_background_layers = self.level_backgrounds[(self.planet_index % self.MAX_LEVEL) + 1]
                                self.layer_offsets = [INITIAL_SCROLL] * PARALLAX_LAYERS
                else:
                    if self.game_mode == "endless":
                        self._endless_wave_spawned = False

                # Render background images utilizing parallax offsets
                for idx, layer_img in enumerate(self.current_background_layers):
                    offset = self.layer_offsets[idx]
                    layer_h = layer_img.get_height()
                    self.screen.blit(layer_img, (0, offset))
                    self.screen.blit(layer_img, (0, offset - layer_h))
                    self.layer_offsets[idx] = (offset + BASE_SCROLL_SPEED * self.current_speed_factors[idx]) % layer_h
                
                # Rendering active frame components
                self._draw_planet()
                self.bunkers.draw(self.screen)
                self.all_sprites.draw(self.screen)
                self.headerbar.update(self.score, self.lives)
                self.headerbar.draw(self.screen)
                
                for puddle in self.puddle_group:
                    if hasattr(puddle, 'hitbox'):
                        pygame.draw.rect(self.screen, (255, 0, 0), puddle.hitbox, 2)
                    else:
                        pygame.draw.rect(self.screen, (255, 255, 0), puddle.rect, 2)

                        
                if getattr(self, 'boss_healthbar', None):
                    self.boss_healthbar.draw(self.screen)
                
                # Dynamic warning LED integration when on low lives
                if self.lives == 1:
                    if not self.warning_played:
                        self.warning_sound.play()
                        self.warning_played = True

                    is_visible = (pygame.time.get_ticks() // 400) % 2 == 0
                    if is_visible:
                        for bar in self.headerbar:
                            warning_x = bar.rect.right + 15
                            warning_y = bar.rect.centery - (bar.warning_icon.get_height() // 2)
                            self.screen.blit(bar.warning_icon, (warning_x, warning_y))
                else:
                    self.warning_played = False
                
                self._present()

            elif self.state == self.STATE_LEVEL_CLEARED:
                # Cinematic Warp Sequence (Clears board, speeds up objects, zooms player)
                
                # Increase exit velocity of remaining sprites (fly off screen)
                for group in [self.player_bullets, self.enemy_bullets, self.powerups, self.comets, self.ufo_group]:
                    for sprite in group:
                        if hasattr(sprite, 'speed') and isinstance(sprite.speed, (int, float)):
                            sprite.speed *= TRANSITION_WARP_OUT_ACCEL
                        if hasattr(sprite, 'vel_x'):
                            sprite.vel_x *= TRANSITION_WARP_OUT_ACCEL
                        if hasattr(sprite, 'vel_y'):
                            sprite.vel_y *= TRANSITION_WARP_OUT_ACCEL
                        if hasattr(sprite, 'speed_x'):
                            sprite.speed_x *= TRANSITION_WARP_OUT_ACCEL
                        if hasattr(sprite, 'speed_y'):
                            sprite.speed_y *= TRANSITION_WARP_OUT_ACCEL

                # Update positions while applying the warp-out modifier
                self.explosions.update()      
                self.player_bullets.update()  
                self.enemy_bullets.update()
                self.powerups.update(SCREEN_HEIGHT)
                self.comets.update(SCREEN_WIDTH, SCREEN_HEIGHT)
                self.ufo_group.update()
                self.puddle_group.update()
                self.bonus_items.update()     # Lässt die Bonus Items fallen
                
               # --- Bonus Items einsammeln ---
                collected_bonus = pygame.sprite.spritecollide(self.player, self.bonus_items, True)
                for item in collected_bonus:
                    self.score += item.points
                    
                    # --- NEU: Effekt spawnen ---
                    effect = CollectEffect(item.rect.centerx, item.rect.centery)
                    self.explosions.add(effect)
                    self.all_sprites.add(effect)
                    
                    # Kleiner visueller Indikator auf den LEDs
                    self.leds.send_effect("A", "blink", 1, 255, 255, 0, speed=10, repeat=3, priority=5)
                
                # Calculate Y-axis easing for the player's ship (fly towards top center screen)
                if self.transition_state == "amplify":
                    target_y = SCREEN_HEIGHT * TRANSITION_PLAYER_Y_AMPLIFY_PCT
                    easing_speed_y = TRANSITION_PLAYER_EASING_UP  
                elif self.transition_state in ("hold", "decel_to_thresh"):
                    target_y = SCREEN_HEIGHT * TRANSITION_PLAYER_Y_HOLD_PCT
                    easing_speed_y = TRANSITION_PLAYER_EASING_DOWN  
                else: 
                    target_y = SCREEN_HEIGHT - TRANSITION_PLAYER_Y_NORMAL_OFFSET 
                    easing_speed_y = TRANSITION_PLAYER_EASING_RETURN
                    
                self.player.exact_y += (target_y - self.player.exact_y) * easing_speed_y
                
                # Still allow X-axis maneuvering during warp
                keys = pygame.key.get_pressed()
                self.player.move(keys, SCREEN_WIDTH)
                self.player.update_buffs()
                
                # Engage special hyperboost graphic logic
                self.player_boost.update(is_hyperboosting=True)
                
                # Push transition sequence logic
                self._run_transition()
                self.bunkers.update()
                
                # Render layers at hyper speeds
                for idx, layer_img in enumerate(self.current_background_layers):
                    offset = self.layer_offsets[idx]
                    layer_h = layer_img.get_height()
                    self.screen.blit(layer_img, (0, offset))
                    self.screen.blit(layer_img, (0, offset - layer_h))
                    self.layer_offsets[idx] = (offset + BASE_SCROLL_SPEED * self.current_speed_factors[idx]) % layer_h
                self._draw_planet()
                
                self.all_sprites.draw(self.screen)
                self.bunkers.draw(self.screen)
                self.headerbar.update(self.score, self.lives)
                self.headerbar.draw(self.screen)
                self._draw_hud() 
                self._present()
            
            else: 
                # Rendering for GAME OVER and VICTORY states (frozen action, UI overlay)
                self.explosions.update()
                self._draw_end_screen()
                self.explosions.draw(self.screen)
                self._present() 

    def save_highscore(self, game_mode="story"):
        """
        Saves the resulting points from an ended run into a structured local JSON file
        based on the game mode, maintaining a sorted top 5 array.
        """
        base_path = os.path.dirname(os.path.abspath(__file__))
        root_path = os.path.dirname(os.path.dirname(base_path))
        filename = os.path.join(root_path, "highsscores.json")
        
        data = {}
        
        # Open existing score file or create empty default
        if os.path.exists(filename):
            with open(filename, "r") as f:
                try: 
                    data = json.load(f)
                    if not isinstance(data, dict):
                        data = {"story": [], "endless": []}
                except:
                    data = {"story": [], "endless": []}
        
        if "story" not in data:
            data["story"] = []
        if "endless" not in data:
            data["endless"] = []
        
        # Prepare the new record
        entry = {"name": self.player_name, "score": self.score}
        if self.game_mode == "endless":
            entry["wave"] = self.wave_number
        
        data[game_mode].append(entry)
        
        # Sort and truncate list to only contain the highest top 5 results
        data[game_mode].sort(key=lambda x: x["score"], reverse=True)
        data[game_mode] = data[game_mode][:5]
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        
        print(f"Erfolg! Gespeichert in: {filename}")