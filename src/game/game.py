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
        FIST_EXPLOSION_SIZE_LARGE, FIST_EXPLOSION_SIZE_SMALL
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

# Helper function to slice sprites
def get_image(sheet, x, y, width, height):
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    image.blit(sheet, (0, 0), (x, y, width, height))
    return image.convert_alpha()

class Game:
    STATE_MENU = "menu"
    STATE_PLAYING = "playing"
    STATE_GAME_OVER = "game_over"
    STATE_VICTORY = "victory"
    STATE_LEVEL_CLEARED = "level_cleared"

    def __init__(self):
        # Compatibility alias: allow access via Game.Player
        pygame.init()
        pygame.mixer.init()

        self.leds = LedController("ws://localhost:8765")
        self.leds.attract_pause()
        self.warning_led_active = False#
        # --- MAUSZEIGER VERSTECKEN ---
        pygame.mouse.set_visible(False)

        #Leaderboard
        self.player_name = ""
        self.selected_key_coords = [0, 0]
        #music/sounds
        self.music_intro = ("assets/music/intro.mp3")
        self.music_level = ("assets/music/02 Pluto.mp3")
        self.music_boss = ("assets/music/03 Pluto Boss.mp3")
        
        self.laser_sound = pygame.mixer.Sound("assets/music/lasershot.mp3")
        self.enemy_explosion = pygame.mixer.Sound("assets/music/enemyexplosion.mp3")
        self.ufo_damage = pygame.mixer.Sound("assets/music/ufodamage.mp3")
        self.warning_sound = pygame.mixer.Sound("assets/music/warning.mp3")
        self.game_over = pygame.mixer.Sound("assets/music/gameover.mp3")
        self.warning_sound.set_volume(0.4)
        self.current_track = None
        self.music_playing = False
        self.warning_played = False 
        
        self.game_mode = "story"
        self.wave_number = 1
        # Window
        # Determine desktop resolution for full‑screen
        info = pygame.display.Info()
        self.full_w, self.full_h = info.current_w, info.current_h
        # Create a true full‑screen window
        self.display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        # Update stored dimensions after setting mode
        self.full_w, self.full_h = self.display.get_width(), self.display.get_height()
        # Create an off‑screen surface for the actual game (1080×1080)
        self.game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        # Keep a legacy alias for existing code that expects self.screen
        self.screen = self.game_surface
        pygame.display.set_caption("Space Invaders")
        # Initial level (needed before loading backgrounds)
        self.level = 1
        self.planet_index = 0  # reset planet sequence for a fresh game (planet_0 visible)
        # Assets
        # Load parallax background layers for each level
        self.level_backgrounds = {}
        for lvl in range(1, 6):
            layers = []
            for layer in range(PARALLAX_LAYERS):
                path = LEVEL_BACKGROUND_PATTERN.format(level=lvl, layer=layer)
                try:
                    img = pygame.image.load(path).convert()
                except Exception:
                    # Fallback placeholder surface (black) if image not found
                    img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    img.fill((0, 0, 0))
                layers.append(img)
            self.level_backgrounds[lvl] = layers
        # Load transition background layers (4 layers)
        self.transition_background = []
        for layer in range(PARALLAX_LAYERS):
            path = TRANSITION_BACKGROUND_PATTERN.format(layer=layer)
            try:
                img = pygame.image.load(path).convert()
            except Exception:
                # Fallback placeholder surface (black) if transition image missing
                img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                img.fill((0, 0, 0))
            self.transition_background.append(img)
        # Set current background layers for the starting level
        self.current_background_layers = self.level_backgrounds[self.level]
        # Offsets for each parallax layer
        self.layer_offsets = [INITIAL_SCROLL] * PARALLAX_LAYERS
        # Font and clock (unchanged)
        self.font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 10)
        self.clock = pygame.time.Clock()
        # Main menu still needs a background image – reuse the first layer of level 1 as fallback
        self.main_menu = MainMenu(self.font)
        self.main_menu = MainMenu(self.font)
        self.end_screen = EndScreen(self.font)

        self.state = self.STATE_MENU
        self.running = True
        self.SCROLL = INITIAL_SCROLL
        # Level management
        self.MAX_LEVEL = 5
        # Load planet images for each level (static props displayed behind sprites)
        self.planets = {}
        # Load planet images indexed by transition count (planet_0.png, planet_1.png, ...)
        from src.config.config import PLANET_PATTERN, PLANET_SCALE
        self.planets = {}
        self.planet_index = 0  # start with planet_0 shown before any transition
        # Initialize planet animation state
        self.planet_y = 0
        self.planet_sliding = False
        for idx in range(self.MAX_LEVEL):  # loads planet_0 .. planet_{MAX_LEVEL-1}
            path = PLANET_PATTERN.format(idx=idx)
            try:
                img = pygame.image.load(path).convert_alpha()
            except Exception:
                # Fallback transparent placeholder if image missing
                img = pygame.Surface((200, 200), pygame.SRCALPHA)
            # Apply global scaling factor to the planet image
            if PLANET_SCALE != 1.0:
                width = int(img.get_width() * PLANET_SCALE)
                height = int(img.get_height() * PLANET_SCALE)
                img = pygame.transform.scale(img, (width, height))
            self.planets[idx] = img

        # After loading all planets, initialize animation for the first planet
        if 0 in self.planets:
            self.planet_y = -self.planets[0].get_height()
        else:
            self.planet_y = 0
        self.planet_sliding = True
        # Next planet tracking for transition slide-in
        self.next_planet_index = None
        self.next_planet_y = 0
        self.next_planet_sliding = False
        self.decel_normal_frames = 0
        
        # Transition Offset für Bunker
        self.bunker_transition_y = 0.0

        self.mini_boss_spawned = False
        self.level_cleared_timer = 0
        self.miniboss_group = pygame.sprite.Group()
        # Transition related flags
        self.is_transition_active = False
        self.transition_state = None
        self.transition_timer = 0
        # Mutable speed factors used during transition phases
        self.current_speed_factors = list(PARALLAX_SPEED_FACTORS)

    def _is_laser_line(self, obj):
        """Helper to detect LaserLine objects (or any object exposing hitboxes)."""
        return hasattr(obj, "get_hitboxes")

    def handle_bunker_collision(self, bullet, bunker_group):
        """Handle collisions between projectiles (including lasers) and bunkers.
        LaserLine objects and LaserSegments instantly destroy any bunker they intersect and
        are then removed from the game. Regular bullets apply damage and respect pierce.
        """
        # ---------- Laser handling (LaserLine or segments) ----------
        if self._is_laser_line(bullet) or isinstance(bullet, LaserSegment):
            # Gather hitboxes: LaserLine provides a list, segment provides its rect.
            hitboxes = bullet.get_hitboxes() if self._is_laser_line(bullet) else [bullet.rect]
            hit_any = False
            for b in list(bunker_group):
                if any(laser_rect.colliderect(b.rect) for laser_rect in hitboxes):
        
                    exp = Explosion(b.rect.centerx, b.rect.centery, size=96)
                    self.explosions.add(exp)
                    self.all_sprites.add(exp)
                    b.kill()
                    hit_any = True
            if hit_any:
                # Remove all bunkers (laser clears entire line)
                bunker_group.empty()
                bullet.kill()
                return

        # ---------- Normal projectile handling ----------
        hit_bunker = pygame.sprite.spritecollideany(
            bullet, bunker_group, pygame.sprite.collide_mask
        )
        if hit_bunker:
            # Special case: PoisonGlob instantly destroys bunker
            if isinstance(bullet, PoisonGlob):
                # Explosion at the bunker location
                exp = Explosion(hit_bunker.rect.centerx, hit_bunker.rect.centery, size=96)
                self.explosions.add(exp)
                self.all_sprites.add(exp)
                # Destroy the bunker
                hit_bunker.kill()
                # Suppress the poison puddle (cloud) from spawning
                bullet.puddle_group = None
                bullet.has_spawned = True
                # Remove the glob itself
                bullet.kill()
                return
            
            # Fist has its own special effect
            if isinstance(bullet, Fist):
                # 1. Große Explosion zufällig auf dem Bunker
                offset_x1 = random.randint(-FIST_EXPLOSION_OFFSET_LARGE, FIST_EXPLOSION_OFFSET_LARGE)
                offset_y1 = random.randint(-FIST_EXPLOSION_OFFSET_LARGE, FIST_EXPLOSION_OFFSET_LARGE)
                exp1_x = hit_bunker.rect.centerx + offset_x1
                exp1_y = hit_bunker.rect.centery + offset_y1
                
                exp1 = Explosion(exp1_x, exp1_y, size=FIST_EXPLOSION_SIZE_LARGE)
                self.explosions.add(exp1)
                self.all_sprites.add(exp1)
                
                # 2. Zweite, kleinere Explosion (gegenüberliegend, damit sie nicht überlappen)
                # Wir negieren den ersten Offset und addieren etwas Zufall
                offset_x2 = -offset_x1 + random.randint(-FIST_EXPLOSION_OFFSET_SMALL, FIST_EXPLOSION_OFFSET_SMALL)
                offset_y2 = -offset_y1 + random.randint(-FIST_EXPLOSION_OFFSET_SMALL, FIST_EXPLOSION_OFFSET_SMALL)
                exp2_x = hit_bunker.rect.centerx + offset_x2
                exp2_y = hit_bunker.rect.centery + offset_y2
                
                exp2 = Explosion(exp2_x, exp2_y, size=FIST_EXPLOSION_SIZE_SMALL)
                self.explosions.add(exp2)
                self.all_sprites.add(exp2)
                
                hit_bunker.take_damage()
            else:
                damage = getattr(bullet, "damage", 1)
                for _ in range(damage):
                    hit_bunker.take_damage()
            # Explosion when bunker is fully destroyed
            if not hit_bunker.alive():
                # Bunker destroyed – create explosion and add to both groups
                exp = Explosion(hit_bunker.rect.centerx, hit_bunker.rect.centery, size=96)
                self.explosions.add(exp)
                self.all_sprites.add(exp)
            # Piercing logic
            if hasattr(bullet, "pierce"):
                bullet.pierce -= 1
                if bullet.pierce <= 0:
                    bullet.kill()
                # ----- Poison puddles (area denial) -----
                for puddle in list(self.puddle_group):
                    if pygame.sprite.collide_rect(puddle, self.player):
                        if self.player_invuln_timer == 0:
                            self.lives -= 1
                            self.player_invuln_timer = 30  # ~0.5 sec
                        player_hit = True
            else:
                bullet.kill()
                # ----- Poison puddles (area denial) -----
                for puddle in list(self.puddle_group):
                    if pygame.sprite.collide_rect(puddle, self.player):
                        if self.player_invuln_timer == 0:
                            self.lives -= 1
                            self.player_invuln_timer = 30  # ~0.5 sec
                        player_hit = True

    def rebuild_bunkers(self):
        # Alte Reste der Bunker zerstören
        for b in self.bunkers:
            explosion = Explosion(b.rect.centerx, b.rect.centery, size=96)
            self.explosions.add(explosion)
            self.all_sprites.add(explosion)
            b.kill()
        
        # Neue, makellose Bunker spawnen
        angles = [0, 90, 180, 270]
        variants = ["satellite", "satellit2", "satellit3", "satellit4"]
        for i, variant in enumerate(variants):
            x_pos = 250 + (i * 190)
            
            # Bunker-Objekt erstellen
            new_bunker = Bunker(x_pos, SCREEN_HEIGHT - 120, variant=variant, angle=angles[i])
            self.bunkers.add(new_bunker)
            self.all_sprites.add(new_bunker)
            
            # NEU: Coole Blitz-Animation (lighting_skill6) darüber legen
            # Da die Effekt-Klasse update() nutzt, können wir sie einfach in "explosions" packen,
            # die Gruppe wird im Spiel-Loop ohnehin jeden Frame geupdated.
            respawn_effect = BunkerRespawnEffect(x_pos, SCREEN_HEIGHT - 120, size=128)
            self.explosions.add(respawn_effect)
            self.all_sprites.add(respawn_effect)

    def _reset(self):
        """Reset the game state for a fresh start or full restart."""
        # 1. LED and Sound Initialization
        self.leds.send_effect("A", "pulse", 99, 0, 255, 0, speed=50, repeat=0, priority=1)
        self.warning_played = False
        self.warning_led_active = False

        # 2. Score and Level Management
        self.score = 0
        self.level = TEST_START_LEVEL
        self.lives = 3
        self.wave_number = 1
        self._endless_wave_spawned = True  
        self.player_shots = 0

        # 3. Sprite Group Cleanup
        # Crucial: Empty the miniboss group BEFORE initializing new groups 
        # to prevent stale bosses from syncing old projectiles.
        if hasattr(self, 'miniboss_group'):
            self.miniboss_group.empty()
            
        # Ensure all existing puddles are explicitly removed
        if hasattr(self, 'puddle_group'):
            for puddle in self.puddle_group:
                puddle.kill()

        # Initialize/Re-initialize all sprite groups
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
        self.miniboss_group = pygame.sprite.Group()
        self.headerbar = pygame.sprite.GroupSingle()

        # 4. Player Initialization
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
        self.player.current_scale = 1.0 
        self.player.exact_y = float(SCREEN_HEIGHT - TRANSITION_PLAYER_Y_NORMAL_OFFSET)
        self.player_invuln_timer = 0
        
        # Player Boost initialization (placed behind the ship)
        self.player_boost = PlayerBoost(self.player)
        self.all_sprites.add(self.player_boost)
        self.all_sprites.add(self.player)

        # 5. Environment and Level Setup
        self.SCROLL = INITIAL_SCROLL
        self.planet_index = 0  
        self.planet_sliding = True
        if 0 in self.planets:
            self.planet_y = -self.planets[0].get_height()
        
        self.current_background_layers = self.level_backgrounds[self.level]
        self.layer_offsets = [INITIAL_SCROLL] * PARALLAX_LAYERS
        self.bunker_transition_y = 0.0

        # Create initial world objects
        self.create_enemy_wave()
        self.enemy_direction = 1
        self.enemy_move_down = 10
        self.headerbar.add(HeaderBar(self.screen, self.font))
        
        # Spawn initial Bunkers
        angles = [0, 90, 180, 270]
        variants = ["satellite", "satellit2", "satellit3", "satellit4"]
        for i, variant in enumerate(variants):
            x_pos = 250 + (i * 190)
            self.bunkers.add(Bunker(x_pos, SCREEN_HEIGHT - 120, variant=variant, angle=angles[i]))

        # 6. Timer and State Flag Resets
        self.ufo_timer = int(UFO_SPAWN_TIME * FPS)
        self.mini_boss_spawned = False
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
        """Blittet die game_surface skaliert und zentriert auf den echten Monitor."""
        self.display.fill((0, 0, 0))
        sw, sh = self.display.get_size()
        
        # Berechne Skalierungsfaktor (Aspect Ratio 1:1 beibehalten)
        scale = min(sw / SCREEN_WIDTH, sh / SCREEN_HEIGHT)
        nw, nh = int(SCREEN_WIDTH * scale), int(SCREEN_HEIGHT * scale)
        
        # Skaliere das Spielfeld qualitativ hochwertig
        scaled_surf = pygame.transform.scale(self.game_surface, (nw, nh))
        
        # Zentriere die Fläche (schwarze Balken bei nicht-quadratischen Monitoren)
        self.display.blit(scaled_surf, ((sw - nw) // 2, (sh - nh) // 2))
        pygame.display.flip()

    def _run_transition(self):
        """Handle the multi‑stage transition background when a level is cleared.
        This method is called every frame while self.state == self.STATE_LEVEL_CLEARED.
        It manipulates self.current_speed_factors, swaps backgrounds, and
        advances the internal sub‑state machine.
        """
        # -----------------------------------------------------------------
        # Initialise the transition on the first call after entering the state
        # -----------------------------------------------------------------
        if not self.is_transition_active:
            self.is_transition_active = True
            self.transition_state = "amplify"

            self.leds.send_effect("A", "chase", 0, 255, 255, 255, speed=22, repeat=13, priority=2)

            # start from the normal per‑layer factors
            self.current_speed_factors = list(PARALLAX_SPEED_FACTORS)
            self.decel_normal_frames = 0
            return

        # Helper lambdas for ramping up/down
        def _ramp_up(factors, step, max_factor):
            return [min(f + step, max_factor) for f in factors]

        def _ramp_down(factors, step, target):
            return [max(f - step, target) for f in factors]

        # ---------------------------------------------------------------
        # Ziele für Animationen basierend auf Transition Phase
        # ---------------------------------------------------------------
        if self.transition_state == "amplify":
            target_scale = TRANSITION_PLAYER_SCALE_MAX   
            target_bunker_y = TRANSITION_BUNKER_Y_DOWN 
        elif self.transition_state in ("hold", "decel_to_thresh"):
            target_scale = TRANSITION_PLAYER_SCALE_MAX
            target_bunker_y = TRANSITION_BUNKER_Y_DOWN
        else: # "decel_to_normal"
            target_scale = TRANSITION_PLAYER_SCALE_NORMAL   
            target_bunker_y = TRANSITION_BUNKER_Y_UP  

        # Easing anwenden auf Scale und Bunker-Offset
        self.player.current_scale += (target_scale - self.player.current_scale) * TRANSITION_PLAYER_SCALE_EASING
        
        self.bunker_transition_y += (target_bunker_y - self.bunker_transition_y) * TRANSITION_BUNKER_EASING
        for b in self.bunkers:
            b.transition_y = self.bunker_transition_y


        # ---------------------------------------------------------------
        # A – Amplify phase: increase speed until the peak factor is hit
        # ---------------------------------------------------------------
        if self.transition_state == "amplify":
    
            self.current_speed_factors = _ramp_up(
                self.current_speed_factors, AMPLIFY_STEP, AMPLIFY_MAX_FACTOR
            )
            # When every layer has reached the max, swap to the transition bg
            if all(abs(f - AMPLIFY_MAX_FACTOR) < 1e-5 for f in self.current_speed_factors):
                self.current_background_layers = self.transition_background
                self.transition_state = "hold"
                self.transition_timer = TRANSITION_HOLD_FRAMES
            return

        # ---------------------------------------------------------------
        # B – Hold phase: keep the transition background for a fixed time
        # ---------------------------------------------------------------
        if self.transition_state == "hold":
            self.transition_timer -= 1
            if self.transition_timer <= 0:
                self.transition_state = "decel_to_thresh"
            return

        # ---------------------------------------------------------------
        # C – Decelerate to the threshold factor while still on transition bg
        # ---------------------------------------------------------------
        if self.transition_state == "decel_to_thresh":
            self.current_speed_factors = _ramp_down(
                self.current_speed_factors, DECEL_STEP, THRESHOLD_FACTOR
            )
            if all(abs(f - THRESHOLD_FACTOR) < 1e-5 for f in self.current_speed_factors):
                self.transition_state = "decel_to_normal"
            return

        # ---------------------------------------------------------------
        # E – Decelerate back to the original per‑layer factors
        # ---------------------------------------------------------------
        if self.transition_state == "decel_to_normal":
            # Track frames in decel_to_normal phase
            self.decel_normal_frames += 1
            
            # Total frames in this phase: (40 - 0) / 0.1 = 400 frames
            # Initialize next planet 60 frames (1 second) before end
            if self.decel_normal_frames == 340 and not self.next_planet_sliding:
                next_idx = self.planet_index + 1
                if next_idx in self.planets:
                    self.next_planet_index = next_idx
                    self.next_planet_y = -self.planets[next_idx].get_height()
                    self.next_planet_sliding = True
            
            # 1. Sicherstellen, dass die neuen Layer gesetzt sind
            # self.level_backgrounds[self.level] MUSS eine Liste von z.B. 4 Images sein
            if self.current_background_layers != self.level_backgrounds[self.level]:
                self.current_background_layers = self.level_backgrounds[self.level]

            if self.transition_timer > 0:
                self.transition_timer -= 1
                return

            # 2. Sanftes Abbremsen auf die Ziel-Faktoren der einzelnen Layer
            # Wir nutzen hier direkt PARALLAX_SPEED_FACTORS als Zielwerte
            new_factors = []
            all_reached = True
            for i, current_f in enumerate(self.current_speed_factors):
                target_f = PARALLAX_SPEED_FACTORS[i]
                if current_f > target_f:
                    next_f = max(current_f - DECEL_STEP, target_f)
                else:
                    next_f = target_f # Falls er schon drunter war
                
                new_factors.append(next_f)
                if abs(next_f - target_f) > 1e-5:
                    all_reached = False
                    
            self.current_speed_factors = new_factors

            # 3. Wenn alle Layer ihre Normalgeschwindigkeit erreicht haben
            if all_reached:
                self._spawn_miniboss()
                self.mini_boss_spawned = True
                self.is_transition_active = False
                self.transition_state = None
                self.state = self.STATE_PLAYING
                # Promote the next planet that was sliding in during transition
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
                # Reset next planet tracking
                self.next_planet_index = None
                self.next_planet_sliding = False
                # WICHTIG: Faktoren final festschreiben
                self.current_speed_factors = list(PARALLAX_SPEED_FACTORS)
            return

    def _spawn_ufo(self):
        ufo = UFO()
        self.ufo_group.add(ufo)
        self.all_sprites.add(ufo)

    def _spawn_miniboss(self):
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
        extra = getattr(boss, "extra_settings", None)
        if isinstance(extra, dict):
            for k, v in extra.items():
                setattr(boss, k, v)
        
        self.miniboss_group.add(boss)
        self.all_sprites.add(boss)
        
        # WICHTIG: NACH dem Boss hinzufügen, damit die Fäuste VOR ihm gezeichnet werden!
        if hasattr(boss, "fist_group"):
            self.all_sprites.add(boss.fist_group)

    def _play_music(self, trak_path, volume = 0.2):
        if self.current_track != trak_path:
            pygame.mixer.music.load(trak_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
            self.current_track = trak_path

    def create_enemy_wave(self):
        """Create normal enemy wave based on current level settings."""
        if self.game_mode == "story":
            settings = ENEMY_WAVE_SETTINGS.get(self.level, ENEMY_WAVE_SETTINGS[1])
            rows = settings["rows"]
            cols = settings["cols"]
            self.enemy_speed = settings.get("speed", ENEMY_SPEED)
            self.enemy_shoot_chance = settings.get("shoot_chance", ENEMY_SHOOT_CHANCE)
        else:
        # ENDLESS LOGIK: Schwierigkeit steigt mit self.wave_number
            rows = min(6, 3 + (self.wave_number // 5)) # Alle 5 Wellen eine Reihe mehr
            cols = 8
            self.enemy_speed = ENEMY_SPEED + (self.wave_number * 0.2)
            self.enemy_shoot_chance = ENEMY_SHOOT_CHANCE + (self.wave_number * 0.005)
        
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
        move_sideways = True
        for enemy in self.enemies:
            if self.enemy_direction == 1 and enemy.rect.right >= SCREEN_WIDTH - 10:
                move_sideways = False
                break
            if self.enemy_direction == -1 and enemy.rect.left <= 10:
                move_sideways = False
                break
        if not move_sideways:
            for enemy in self.enemies:
                enemy.rect.y += self.enemy_move_down
            self.enemy_direction *= -1
        else:
            for enemy in self.enemies:
                enemy.move(self.enemy_direction)

    def _enemy_shooting(self):
        for enemy in self.enemies:
            if random.random() < self.enemy_shoot_chance:
                bullet = enemy.shoot()
                self.enemy_bullets.add(bullet)
                self.all_sprites.add(bullet)

    def _check_collisions(self):
        # Enemy vs player bullet (WICHTIG: dokill2=False für Pierce-Mechanik)
        # Decrease the player's invulnerability timer if active
        if hasattr(self, 'player_invuln_timer') and self.player_invuln_timer > 0:
            self.player_invuln_timer -= 1
        hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, True, False)
        if hits:
            self.enemy_explosion.play()
            for seg in range(1, 5):
                self.leds.send_effect("A", "blink", seg, 200, 255, 0, speed=1, repeat=10, priority=2)
            for enemy, bullets in hits.items():
                explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                self.explosions.add(explosion)
                self.all_sprites.add(explosion)
                # Pierce von beteiligten Kugeln abziehen
                for b in bullets:
                    b.pierce -= 1
                    if b.pierce <= 0:
                        b.kill()
                # Neues PowerUp Drop-System:
                if not self.mini_boss_spawned:
                    roll = random.random()
                    cumulative = 0.0
                    for p_type, chance in POWERUP_DROP_CHANCES.items():
                        cumulative += chance
                        if roll < cumulative:
                            powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, POWERUP_FALL_SPEED, p_type)
                            self.powerups.add(powerup)
                            self.all_sprites.add(powerup)
                            break  # Verhindert, dass ein Gegner 2 Items droppt
            self.score += len(hits) * 100
        
        # UFO vs player bullet
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

        # Collision handling – lasers and regular enemy bullets
        player_hit = False
        # ----- LaserLine handling (from minibosses and any LaserLine in enemy_bullets) -----
        laser_objects = []
        # Collect lasers stored in minibosses
        for boss in self.miniboss_group:
            if hasattr(boss, "laser_lines"):
                laser_objects.extend(list(boss.laser_lines))
        # Also collect any LaserLine that might be directly in enemy_bullets
        for bullet in list(self.enemy_bullets):
            if self._is_laser_line(bullet) and bullet not in laser_objects:
                laser_objects.append(bullet)
        # Process each laser – one life per laser hit
        for laser in laser_objects:
            if any(self.player.rect.colliderect(hitbox) for hitbox in laser.get_hitboxes()):
                player_hit = True
                self.lives -= getattr(laser, "damage", 1)  # LaserLine damage (currently 1)
                self.ufo_damage.play()
                laser.kill()
            
        # ----- Regular enemy bullets (non‑laser) -----
        for bullet in list(self.enemy_bullets):
            if self._is_laser_line(bullet):
                continue  # already handled above
            if pygame.sprite.collide_rect(bullet, self.player):
                player_hit = True
                dmg = getattr(bullet, "damage", 1)
                self.lives -= dmg
                
                # NEU: Explosion wenn die Faust den Spieler trifft
                if isinstance(bullet, Fist):
                    exp = Explosion(bullet.rect.centerx, bullet.rect.centery, size=64)
                    self.explosions.add(exp)
                    self.all_sprites.add(exp)
                    
                bullet.kill()
                # ----- Poison puddles (area denial) -----
                for puddle in list(self.puddle_group):
                    if pygame.sprite.collide_rect(puddle, self.player):
                        if self.player_invuln_timer == 0:
                            self.lives -= 1
                            self.player_invuln_timer = 30  # ~0.5 sec
                        player_hit = True
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

        # Mini‑boss collisions
        for boss in list(self.miniboss_group):
            hits = pygame.sprite.spritecollide(boss, self.player_bullets, False)
            for b in hits:
                hit_explosion = Explosion(boss.rect.centerx, boss.rect.centery, size=48)
                self.explosions.add(hit_explosion)
                for seg in range(1, 6):
                    self.leds.send_effect("A", "blink", seg, 255, 255, 255, speed=1, repeat=2, priority=3)
                self.all_sprites.add(hit_explosion)
                boss.hit()
                if not boss.alive() and isinstance(boss, BossSmall2):
                    powerup = PowerUp(boss.rect.centerx, boss.rect.centery, POWERUP_FALL_SPEED, "bunker")
                    self.powerups.add(powerup)
                    self.all_sprites.add(powerup)
                b.pierce -= 1
                if b.pierce <= 0:
                    b.kill()

        # Enemy reaching player
        for enemy in self.enemies:
            if enemy.rect.bottom >= self.player.rect.top:
                self.state = self.STATE_GAME_OVER

        # POWERUP SAMMELN
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        if powerup_hits:
            self.leds.send_effect("A", "blink", 1, 0, 255, 255, speed=10, repeat=5, priority=5)
            for pu in powerup_hits:
                if pu.type == "comet":
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

        # Komet trifft Gegner
        for comet in self.comets:
            comet_enemy_hits = pygame.sprite.spritecollide(comet, self.enemies, True)
            if comet_enemy_hits:
                self.enemy_explosion.play()
                for enemy in comet_enemy_hits:
                    explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                    self.explosions.add(explosion)
                    self.all_sprites.add(explosion)
                    self.score += 100

        # Komet trifft auf Boss
        for boss in list(self.miniboss_group):
            comet_boss_hits = pygame.sprite.spritecollide(boss, self.comets, True)
            if comet_boss_hits:
                self.enemy_explosion.play()
                for comet in comet_boss_hits:
                    explosion = Explosion(comet.rect.centerx, comet.rect.centery, size=128)
                    self.explosions.add(explosion)
                    self.all_sprites.add(explosion)


    def _draw_hud(self):
        """Draw score and lives HUD."""
        score_surf = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        lives_surf = self.font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        self.screen.blit(score_surf, (10, 10))
        self.screen.blit(lives_surf, (SCREEN_WIDTH - lives_surf.get_width() - 10, 10))

    def _draw_planet(self):
        """Draw the planet that corresponds to the current post‑transition index.
        Called only while self.state == STATE_PLAYING.
        """
        # Planet index is always >= 0 (planet_0 shown at start)
        planet_img = self.planets.get(self.planet_index)
        if not planet_img:
            return
        rect = planet_img.get_rect()
        rect.centerx = SCREEN_WIDTH // 2.5
        # Base vertical target position (middle‑lower part of screen) with background scroll offset
        base_target_y = SCREEN_HEIGHT
        try:
            scroll_offset = self.layer_offsets[1] * PLANET_SCROLL_FACTOR
        except Exception:
            scroll_offset = 1
        target_y = int(base_target_y + scroll_offset)
        # Calculate the normal target Y (used when not in a transition)
        normal_target_y = int(base_target_y + scroll_offset)

        # If the planet is sliding, move it toward the (normal) target position.
        # During a transition we accelerate the slide speed, but we *do not* stop sliding
        # until the transition is over and the normal target has been reached.
        if getattr(self, "planet_sliding", False):
            # Choose slide speed based on whether a transition is active
            if self.is_transition_active:
                slide_speed = BASE_SCROLL_SPEED * self.current_speed_factors[0]
            else:
                slide_speed = 0.35
            self.planet_y += slide_speed
            # When not in a transition, stop sliding once we reach the normal target
            if not self.is_transition_active and self.planet_y >= normal_target_y:
                self.planet_y = normal_target_y
                self.planet_sliding = False
        else:
            # When not sliding and not in a transition, keep the planet anchored to the normal target
            if not self.is_transition_active:
                self.planet_y = normal_target_y
            # If we are in a transition and not sliding, we keep the current planet_y so it continues moving off‑screen

        # Safe despawn – hide the planet once it has fully moved below the visible area
        if self.planet_y > SCREEN_HEIGHT + planet_img.get_height():
            pass  # Don't return, may still need to draw next planet

        # Position the planet using its top coordinate
        rect.top = int(self.planet_y)
        self.screen.blit(planet_img, rect)
        
        # Draw the next planet if it's sliding in during transition
        if getattr(self, "next_planet_sliding", False) and self.next_planet_index is not None:
            next_planet_img = self.planets.get(self.next_planet_index)
            if next_planet_img:
                next_rect = next_planet_img.get_rect()
                next_rect.centerx = SCREEN_WIDTH // 2.5
                
                # Use background scroll speed (layer 0 speed factor) during transition
                if self.is_transition_active:
                    next_slide_speed = BASE_SCROLL_SPEED * self.current_speed_factors[0]
                else:
                    next_slide_speed = 0.35
                
                self.next_planet_y += next_slide_speed
                
                # After transition ends, behave like normal planet
                if not self.is_transition_active:
                    try:
                        next_scroll_offset = self.layer_offsets[1] * PLANET_SCROLL_FACTOR
                    except Exception:
                        next_scroll_offset = 1
                    next_normal_target_y = int(base_target_y + next_scroll_offset)
                    if self.next_planet_y >= next_normal_target_y:
                        self.next_planet_y = next_normal_target_y
                
                # Don't draw if fully off-screen below
                if self.next_planet_y <= SCREEN_HEIGHT + next_planet_img.get_height():
                    next_rect.top = int(self.next_planet_y)
                    self.screen.blit(next_planet_img, next_rect)

    def _draw_end_screen(self):
        """Ruft die externe EndScreen-Klasse auf, um Sieg oder Niederlage anzuzeigen."""
        # Bestimme, ob es ein Sieg ist (True) oder Game Over (False)
        is_victory = (self.state == self.STATE_VICTORY)
        
        # Zeichne das Overlay und den Text über die aktuelle game_surface
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
        self.level += 1
        if self.level > self.MAX_LEVEL:
            self.leds.send_effect("A", "blink", 99, 255, 255, 0, speed=5, repeat=10, priority=3)
            self.state = self.STATE_VICTORY
            return
        self.headerbar.sprite.set_level(self.level)
        self.mini_boss_spawned = False
        self.miniboss_group.empty()
        self.enemies.empty()
        # Update background for the new level
        self.current_background_layers = self.level_backgrounds[self.level]
        self.layer_offsets = [INITIAL_SCROLL] * PARALLAX_LAYERS
        self.create_enemy_wave()
        self.ufo_timer = int(UFO_SPAWN_TIME * FPS)
        self.player_shots = 0
        self.level_cleared_timer = 0
        self.state = self.STATE_PLAYING
        self.leds.send_effect("A", "pulse", 99, 0, 255, 0, speed=50, repeat=0, priority=1)
        
        # NEU: Spieler fliegt zurück auf seine "Linie" unten (Easing)
        self.transitioning_back_timer = 2 * FPS # Dauer des Rückflugs

    def increase_level(self):
        if self.mini_boss_spawned:
            self.level += 1
            if self.level > self.MAX_LEVEL:
                self.state = self.STATE_VICTORY
                return
            self.headerbar.sprite.set_level(self.level)
            self.current_background_layers = self.level_backgrounds[self.level]
            self.layer_offsets = [INITIAL_SCROLL] * PARALLAX_LAYERS

    def run(self):
        self.led_heartbeat_timer = 0

        while True:
            self.clock.tick(FPS)
            self.led_heartbeat_timer -= 1
            if self.led_heartbeat_timer <= 0:
                # Sendet den Standard-Effekt (Pulsieren Grün)
                self.leds.send_effect("A", "pulse", 99, 0, 255, 0, speed=50, repeat=0, priority=1)
                self.led_heartbeat_timer = 1
            
            # --- 1. EVENT HANDLING (NUR EINGABEN) ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # --- GLOBAL QUIT CHECK ---
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                
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
                        
                elif self.state == self.STATE_PLAYING: 
                    if event.type == pygame.KEYDOWN:
                        # --- NEU: Schießen per Einzelklick im EVENT LOOP ---
                        if event.key == pygame.K_SPACE:
                            bullet = self.player.shoot()
                            if bullet:
                                self.laser_sound.play()
                                self.player_bullets.add(bullet)
                                self.all_sprites.add(bullet)
                                self.player_shots += 1
                        elif event.key == pygame.K_r:
                            self._reset()
                
                # Wenn das Level geschafft ist (Keine Highscore-Eingabe hier!)
                elif self.state == self.STATE_LEVEL_CLEARED:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self._reset()
                            self.state = self.STATE_PLAYING

                # Highscore-Eingabe (Nur bei Game Over oder Victory)
                elif self.state in (self.STATE_GAME_OVER, self.STATE_VICTORY):
                    if event.type == pygame.KEYDOWN:
                        # Schnell-Neustart / Beenden
                        if event.key == pygame.K_r:
                            self.player_name = ""
                            self._reset()
                            self.state = self.STATE_PLAYING

                        # 1. Navigation auf der Tastatur
                        elif event.key == pygame.K_LEFT:
                            self.selected_key_coords[0] = (self.selected_key_coords[0] - 1) % 7
                        elif event.key == pygame.K_RIGHT:
                            self.selected_key_coords[0] = (self.selected_key_coords[0] + 1) % 7
                        elif event.key == pygame.K_UP:
                            self.selected_key_coords[1] = (self.selected_key_coords[1] - 1) % 4
                        elif event.key == pygame.K_DOWN:
                            self.selected_key_coords[1] = (self.selected_key_coords[1] + 1) % 4
                        
                        # 2. Buchstabe auswählen / Löschen / OK (mit Enter oder Leertaste)
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            # Hol dir das aktuell markierte Zeichen aus der EndScreen-Matrix
                            col, row = self.selected_key_coords
                            char = self.end_screen.keys[row][col]

                            if char == '<':
                                # Löscht den letzten Buchstaben
                                self.player_name = self.player_name[:-1] 
                            elif char == 'OK':
                                # Speichert, wenn ein Name da ist, und geht ins Menü
                                if len(self.player_name) > 0:
                                    self.save_highscore(self.game_mode)
                                    self.player_name = ""
                                    self.state = self.STATE_MENU 
                            else:
                                # Fügt Buchstaben hinzu (Maximal 12 Zeichen)
                                if len(self.player_name) < 12: 
                                    self.player_name += char
                        

            # --- 2. UPDATES & RENDERING (AUSSERHALB DER EVENT-SCHLEIFE) ---
            
            if self.state == self.STATE_MENU:
                # Draw the background planet (planet_0) behind the menu
                self._draw_planet()
                # Draw the main menu UI on top
                self.main_menu.draw(self.screen)
                self._present()

            elif self.state == self.STATE_PLAYING:
                # Musik Update
                if self.mini_boss_spawned:
                    self._play_music(self.music_boss, 0.7)
                else:
                    self._play_music(self.music_level, 0.7)

                # --- 1. Y-Achsen Easing (Nach Transition weich zurück auf Normalhöhe) ---
                target_y = SCREEN_HEIGHT - TRANSITION_PLAYER_Y_NORMAL_OFFSET # Normalhöhe
                if abs(self.player.exact_y - target_y) > 0.5:
                    self.player.exact_y += (target_y - self.player.exact_y) * TRANSITION_PLAYER_EASING_PLAYING
                
                # --- 2. Spieler-Logik & Buffs ---
                keys = pygame.key.get_pressed()
                self.player.move(keys, SCREEN_WIDTH)
                self.player.update_buffs()      
                # Im normalen Spiel: Normaler Boost
                self.player_boost.update(is_hyperboosting=False)  

                # --- 3. ALLE GRUPPEN UPDATEN (Jede strikt nur 1x!) ---
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
                
                # --- 4. Kollisionen mit Bunkern prüfen ---
                for bullet in self.player_bullets:
                    self.handle_bunker_collision(bullet, self.bunkers)
                for bomb in self.enemy_bullets:
                    self.handle_bunker_collision(bomb, self.bunkers)
                

                # --- 5. Timer, Gegner-Logik & generelle Kollisionen ---
                self._handle_enemy_movement()
                self._enemy_shooting()
                
                self.ufo_timer -= 1
                if self.ufo_timer <= 0 or self.player_shots >= UFO_SHOT_THRESHOLD:
                    self._spawn_ufo()
                    self.ufo_timer = int(UFO_SPAWN_TIME * FPS)
                    self.player_shots = 0
                
                self._check_collisions()
                
                # --- 6. Level Progress Check ---
                if not self.enemies and not self.explosions:
                    if self.game_mode == "story":
                        if not self.mini_boss_spawned:
                            # Level geschafft! Wechsle in den Transition-State
                            self.state = self.STATE_LEVEL_CLEARED
                            self.level_cleared_timer = 5 * FPS
                        elif self.mini_boss_spawned and not self.miniboss_group:
                            self.advance_level()
                    elif self.game_mode == "endless":
                        # ENDLESS MODUS: Nächste Welle sofort spawnen
                        if not getattr(self, '_endless_wave_spawned', False):
                            self.wave_number += 1
                            self.create_enemy_wave()
                            self.score += 500
                            self._endless_wave_spawned = True
                            # Cycle background/planet every 5 waves
                            if self.wave_number % 5 == 0:
                                self.planet_index = (self.planet_index + 1) % self.MAX_LEVEL
                                if self.planet_index in self.planets:
                                    self.planet_y = -self.planets[self.planet_index].get_height()
                                    self.planet_sliding = True
                                self.current_background_layers = self.level_backgrounds[(self.planet_index % self.MAX_LEVEL) + 1]
                                self.layer_offsets = [INITIAL_SCROLL] * PARALLAX_LAYERS
                else:
                    # Reset the flag when enemies are present
                    if self.game_mode == "endless":
                        self._endless_wave_spawned = False

                # --- 7. Zeichnen ---
                # Parallax background drawing (all layers)
                for idx, layer_img in enumerate(self.current_background_layers):
                    offset = self.layer_offsets[idx]
                    layer_h = layer_img.get_height()
                    self.screen.blit(layer_img, (0, offset))
                    self.screen.blit(layer_img, (0, offset - layer_h))
                    self.layer_offsets[idx] = (offset + BASE_SCROLL_SPEED * self.current_speed_factors[idx]) % layer_h
                # Draw the planet after all background layers but before any sprites (enemies, bunkers, etc.)
                self._draw_planet()
                
                self.bunkers.draw(self.screen)
                self.all_sprites.draw(self.screen)
                self.headerbar.update(self.score, self.lives)
                self.headerbar.draw(self.screen)
                
                # Warning Icon Logik
                if self.lives == 1:
                    # 1. Sound Trigger
                    if not self.warning_played:
                        self.warning_sound.play()
                        self.warning_played = True

                    # 2. Visuelles Icon Blinken
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
                
                # --- Warp-Out-Effekt für alle verbleibenden Objekte ---
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

                self.explosions.update()      # Lässt Explosionen zu Ende animieren
                self.player_bullets.update()  # Lässt Schüsse aus dem Bild fliegen
                self.enemy_bullets.update()
                self.powerups.update(SCREEN_HEIGHT)
                self.comets.update(SCREEN_WIDTH, SCREEN_HEIGHT)
                self.ufo_group.update()
                self.puddle_group.update()
                
                # --- Y-Achsen Easing für den Cinematic Flight ---
                if self.transition_state == "amplify":
                    # Schießt sanft hoch auf 20% des Bildschirms (ca. 80% hoch)
                    target_y = SCREEN_HEIGHT * TRANSITION_PLAYER_Y_AMPLIFY_PCT
                    easing_speed_y = TRANSITION_PLAYER_EASING_UP  # Sehr weich
                elif self.transition_state in ("hold", "decel_to_thresh"):
                    # Fällt sanft zurück auf 50% der Bildschirmmitte
                    target_y = SCREEN_HEIGHT * TRANSITION_PLAYER_Y_HOLD_PCT
                    easing_speed_y = TRANSITION_PLAYER_EASING_DOWN  # Noch weicher
                else: # "decel_to_normal"
                    # Fliegt extrem weich zurück in die Ausgangsposition
                    target_y = SCREEN_HEIGHT - TRANSITION_PLAYER_Y_NORMAL_OFFSET 
                    easing_speed_y = TRANSITION_PLAYER_EASING_RETURN
                    
                self.player.exact_y += (target_y - self.player.exact_y) * easing_speed_y
                
                # --- Spielerbewegung und HYPERBOOST während der Transition ---
                keys = pygame.key.get_pressed()
                # Spieler bleibt auf X-Achse beweglich, wendet am Ende intern exact_y an!
                self.player.move(keys, SCREEN_WIDTH)
                self.player.update_buffs()
                
                # HYPERBOOST aktivieren (wächst sanft an und nutzt die 4 Frames)
                self.player_boost.update(is_hyperboosting=True)
                
                # Run transition logic (amplify, hold, decelerate, load next level)
                # (Hier rutschen auch die Bunker sanft aus dem Bild)
                self._run_transition()
                self.bunkers.update()
                
                # Draw the current background (could be level background or transition)
                for idx, layer_img in enumerate(self.current_background_layers):
                    offset = self.layer_offsets[idx]
                    layer_h = layer_img.get_height()
                    self.screen.blit(layer_img, (0, offset))
                    self.screen.blit(layer_img, (0, offset - layer_h))
                    # advance offset using the (potentially modified) speed factors
                    self.layer_offsets[idx] = (offset + BASE_SCROLL_SPEED * self.current_speed_factors[idx]) % layer_h
                # Draw the static planet for the current level
                self._draw_planet()
                
                # Draw regular game elements on top of the background
                self.all_sprites.draw(self.screen)
                self.bunkers.draw(self.screen)
                self.headerbar.update(self.score, self.lives)
                self.headerbar.draw(self.screen)
                self._draw_hud()
                self._present()
            
            else: # GAME_OVER / VICTORY
                self.explosions.update()
                self._draw_end_screen()
                self.explosions.draw(self.screen)
                self._present() 

    def save_highscore(self, game_mode="story"):
        # Pfad-Logik: Findet den Hauptordner deines Projekts
        base_path = os.path.dirname(os.path.abspath(__file__))
        # Da game.py in src/game/ liegt, gehen wir zwei Ebenen hoch
        root_path = os.path.dirname(os.path.dirname(base_path))
        filename = os.path.join(root_path, "highsscores.json")
        
        data = {}
        
        # 1. Bestehende Scores laden
        if os.path.exists(filename):
            with open(filename, "r") as f:
                try: 
                    data = json.load(f)
                    # Sicherstellen, dass es ein Dict ist
                    if not isinstance(data, dict):
                        data = {"story": [], "endless": []}
                except:
                    data = {"story": [], "endless": []}
        
        # Ensure both keys exist
        if "story" not in data:
            data["story"] = []
        if "endless" not in data:
            data["endless"] = []
        
        # 2. Aktuellen Versuch hinzufügen
        entry = {"name": self.player_name, "score": self.score}
        if self.game_mode == "endless":
            entry["wave"] = self.wave_number
        
        data[game_mode].append(entry)
        
        # 3. Sortieren (höchster Score oben)
        data[game_mode].sort(key=lambda x: x["score"], reverse=True)
        
        # 4. Nur die Top 5 behalten
        data[game_mode] = data[game_mode][:5]
        
        # 5. Speichern
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        
        # Kleine Hilfe für dich im Terminal:
        print(f"Erfolg! Gespeichert in: {filename}")