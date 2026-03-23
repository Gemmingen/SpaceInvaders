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
    BONUS_ITEM_SPEED, BONUS_ITEM_PROBABILITIES,
    STORY_ENEMY_BASE_MOVE_DOWN, STORY_ENEMY_MOVE_DOWN_INCREMENT,
    ENDLESS_ENEMY_BASE_MOVE_DOWN, ENDLESS_ENEMY_MOVE_DOWN_INCREMENT,
    ENDLESS_BASE_COLS, ENDLESS_BASE_ROWS, ENDLESS_MAX_ROWS,
    ENDLESS_ROW_INCREMENT_WAVES, ENDLESS_SPEED_INCREMENT,
    ENDLESS_BASE_SHOOT_CHANCE, ENDLESS_SHOOT_CHANCE_INCREMENT
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
from src.game.boss_healthbar import BossHealthBar
from src.game.bonus_points import BonusPointItem, CollectEffect

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
        pygame.init()
        pygame.mixer.init()

        self.leds = LedController("ws://localhost:8765")
        self.leds.attract_pause()
        self.warning_led_active = False
        pygame.mouse.set_visible(False)

        self.num_players = 1
        self.player1_name = ""
        self.player2_name = ""
        self.selected_key_coords_p1 = [0, 0]
        self.selected_key_coords_p2 = [0, 0]
        self.p1_done = False
        self.p2_done = False
        
        self.music_intro = ("assets/music/intro.mp3")
        self.music_level = ("assets/music/02 Pluto.mp3")
        self.music_boss_1 = ("assets/music/03 Pluto Boss.mp3")
        self.music_boss_2 = ("assets/music/secondboss.mp3")
        self.music_boss_3 = ("assets/music/thirdboss.mp3")
        self.music_boss_4 = ("assets/music/fourthboss.mp3")
        self.music_boss_5 = ("assets/music/endboss.mp3")
        self.music_victory = ("assets/music/winbackround.mp3")
        
        
        self.laser_sound = pygame.mixer.Sound("assets/music/lasershot.mp3")
        self.enemy_explosion = pygame.mixer.Sound("assets/music/enemyexplosion.mp3")
        self.sfx_ufo_damage = pygame.mixer.Sound("assets/music/ufodamage.mp3")
        self.warning_sound = pygame.mixer.Sound("assets/music/warning.mp3")
        self.game_over = pygame.mixer.Sound("assets/music/gameover.mp3")
        self.boss_spawn_sound = pygame.mixer.Sound("assets/music/bossspawn.mp3")
        self.collect_points_sound  = pygame.mixer.Sound("assets/music/powerupsound.mp3")
        self.victory_voice = pygame.mixer.Sound("assets/music/youwin.mp3")
        self.boss_death_sound = pygame.mixer.Sound("assets/music/enemyexplosion.mp3")
        self.transition_sound = pygame.mixer.Sound("assets/music/transition.mp3")
        self.warning_sound.set_volume(0.4)
        self.boss_death_sound.set_volume(0.4)
        self.laser_sound.set_volume(0.1)
        self.enemy_explosion.set_volume(0.1)
        self.collect_points_sound.set_volume(0.1)
        self.transition_sound.set_volume(0.2)


        self.current_track = None
        self.music_playing = False
        self.warning_played = False 
        
        self.game_mode = "story"
        
        info = pygame.display.Info()
        self.full_w, self.full_h = info.current_w, info.current_h
        self.display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.full_w, self.full_h = self.display.get_width(), self.display.get_height()
        
        self.game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen = self.game_surface
        pygame.display.set_caption("Space Invaders")
        
        self.level_backgrounds = {}
        for lvl in range(1, 6):
            layers = []
            for layer in range(PARALLAX_LAYERS):
                path = LEVEL_BACKGROUND_PATTERN.format(level=lvl, layer=layer)
                try:
                    img = pygame.image.load(path).convert()
                except Exception:
                    img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    img.fill((0, 0, 0))
                layers.append(img)
            self.level_backgrounds[lvl] = layers
            
        self.transition_background = []
        for layer in range(PARALLAX_LAYERS):
            path = TRANSITION_BACKGROUND_PATTERN.format(layer=layer)
            try:
                img = pygame.image.load(path).convert()
            except Exception:
                img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                img.fill((0, 0, 0))
            self.transition_background.append(img)
            
        self.font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 10)
        self.clock = pygame.time.Clock()
        self.main_menu = MainMenu(self.font)
        self.end_screen = EndScreen(self.font)
        self.menu_selection = 0
        self.state = self.STATE_MENU
        self.running = True
        self.MAX_LEVEL = 5
        
        # --- FIX: Initialize background variables needed for the Main Menu ---
        self.level = 1
        self.planet_index = 0  
        self.layer_offsets = [INITIAL_SCROLL] * PARALLAX_LAYERS
        self.current_background_layers = self.level_backgrounds[self.level]
        self.is_transition_active = False
        self.current_speed_factors = list(PARALLAX_SPEED_FACTORS)
        # -------------------------------------------------------------------

        from src.config.config import PLANET_PATTERN, PLANET_SCALE
        self.planets = {}
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

        # --- FIX: Initialize planet slide variables needed for the Main Menu ---
        if 0 in self.planets:
            self.planet_y = -self.planets[0].get_height()
        else:
            self.planet_y = 0
            
        self.planet_sliding = True
        self.next_planet_index = None
        self.next_planet_y = 0
        self.next_planet_sliding = False
        # -----------------------------------------------------------------------

        # Define all variables managed by independent boards dynamically for Versus mode
        self.BOARD_VARS = [
            'score', 'level', 'lives', 'wave_number', 'poison_tick_timer', '_endless_wave_spawned',
            'player_shots', 'bunker_transition_y', 'mini_boss_spawned', 'level_cleared_timer',
            'miniboss_group', 'puddle_group', 'all_sprites', 'explosions', 'enemies',
            'player_bullets', 'enemy_bullets', 'bunkers', 'ufo_group', 'powerups', 'comets',
            'bonus_items', 'headerbar', 'active_players', 'player1', 'player1_boost',
            'player2', 'player2_boost', 'player_invuln_timer', 'SCROLL', 'planet_index', 
            'planet_sliding', 'planet_y', 'next_planet_index', 'next_planet_y', 
            'next_planet_sliding', 'decel_normal_frames', 'current_background_layers', 
            'layer_offsets', 'enemy_speed', 'enemy_shoot_chance', 'enemy_direction', 
            'enemy_move_down', 'ufo_timer', 'boss_healthbar', 'game_surface', 'screen', 
            'state', 'is_transition_active', 'transition_state', 'transition_timer',
            'current_speed_factors', 'transitioning_back_timer'
        ]

    def _save_context(self, b_id):
        self.boards[b_id] = {var: getattr(self, var) for var in self.BOARD_VARS if hasattr(self, var)}

    def _load_context(self, b_id):
        for var, val in self.boards[b_id].items():
            setattr(self, var, val)

    def _is_laser_line(self, obj):
        return hasattr(obj, "get_hitboxes")

    def handle_bunker_collision(self, bullet, bunker_group):
        if self._is_laser_line(bullet) or isinstance(bullet, LaserSegment):
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
                for b in list(bunker_group):
                    exp = Explosion(b.rect.centerx, b.rect.centery, size=96)
                    self.explosions.add(exp)
                    self.all_sprites.add(exp)
                    b.kill()
                bullet.kill()
                return

        hit_bunker = pygame.sprite.spritecollideany(
            bullet, bunker_group, pygame.sprite.collide_mask
        )
        if hit_bunker:
            if isinstance(bullet, Fist) or isinstance(bullet, PoisonGlob):
                offset_x1 = random.randint(-FIST_EXPLOSION_OFFSET_LARGE, FIST_EXPLOSION_OFFSET_LARGE)
                offset_y1 = random.randint(-FIST_EXPLOSION_OFFSET_LARGE, FIST_EXPLOSION_OFFSET_LARGE)
                exp1_x = hit_bunker.rect.centerx + offset_x1
                exp1_y = hit_bunker.rect.centery + offset_y1
                
                exp1 = Explosion(exp1_x, exp1_y, size=FIST_EXPLOSION_SIZE_LARGE)
                self.explosions.add(exp1)
                self.all_sprites.add(exp1)
                
                offset_x2 = -offset_x1 + random.randint(-FIST_EXPLOSION_OFFSET_SMALL, FIST_EXPLOSION_OFFSET_SMALL)
                offset_y2 = -offset_y1 + random.randint(-FIST_EXPLOSION_OFFSET_SMALL, FIST_EXPLOSION_OFFSET_SMALL)
                exp2_x = hit_bunker.rect.centerx + offset_x2
                exp2_y = hit_bunker.rect.centery + offset_y2
                
                exp2 = Explosion(exp2_x, exp2_y, size=FIST_EXPLOSION_SIZE_SMALL)
                self.explosions.add(exp2)
                self.all_sprites.add(exp2)
                
                if isinstance(bullet, PoisonGlob):
                    bullet.puddle_group = False 
                    bullet.has_spawned = True
                    bullet.kill()
                hit_bunker.take_damage()
                hit_bunker.take_damage()
                hit_bunker.take_damage() #Damit die bissle mehr schaden machen, macht ja irgendwie nur sinn 
            else:
                damage = getattr(bullet, "damage", 1)
                for _ in range(damage):
                    hit_bunker.take_damage()
                    
            if not hit_bunker.alive():
                exp = Explosion(hit_bunker.rect.centerx, hit_bunker.rect.centery, size=96)
                self.explosions.add(exp)
                self.all_sprites.add(exp)
                
            if hasattr(bullet, "pierce"):
                bullet.pierce -= 1
                if bullet.pierce <= 0:
                    bullet.kill()
            else:
                bullet.kill()

    def rebuild_bunkers(self):
        for b in self.bunkers:
            explosion = Explosion(b.rect.centerx, b.rect.centery, size=96)
            self.explosions.add(explosion)
            self.all_sprites.add(explosion)
            b.kill()
        
        angles = [0, 90, 180, 270]
        variants = ["satellite", "satellit2", "satellit3", "satellit4"]
        for i, variant in enumerate(variants):
            x_pos = 250 + (i * 190)
            new_bunker = Bunker(x_pos, SCREEN_HEIGHT - 120, variant=variant, angle=angles[i])
            self.bunkers.add(new_bunker)
            self.all_sprites.add(new_bunker)
            
            respawn_effect = BunkerRespawnEffect(x_pos, SCREEN_HEIGHT - 120, size=128)
            self.explosions.add(respawn_effect)
            self.all_sprites.add(respawn_effect)

    def _reset(self):
        self.leds.send_effect("A", "pulse", 99, 0, 255, 0, speed=50, repeat=0, priority=1)
        self.warning_played = False
        self.warning_led_active = False

        self.player1_name = ""
        self.player2_name = ""
        self.p1_done = False
        self.p2_done = False
        self.selected_key_coords_p1 = [0, 0]
        self.selected_key_coords_p2 = [0, 0]
        
        if self.game_mode == "versus":
            self.boards = {1: {}, 2: {}}
            self.versus_over_timer = 3 * FPS
            self._versus_end_surface_created = False
            for b_id in (1, 2):
                self._reset_board(b_id)
                self._save_context(b_id)
            self._load_context(1)
        else:
            self.boards = None
            self._reset_board(None)

    def _reset_board(self, b_id):
        self.score = 0
        self.level = TEST_START_LEVEL
        self.lives = 3 if (self.game_mode != "story" or self.num_players == 1) else 6
        self.wave_number = 1
        self.poison_tick_timer = POISON_DAMAGE_DELAY

        self._endless_wave_spawned = True
        self.player_shots = 0
        self.bunker_transition_y = 0.0  
        
        if hasattr(self, 'miniboss_group'):
            for boss in getattr(self, 'miniboss_group', []):
                boss.kill()
        self.miniboss_group = pygame.sprite.Group()
        
        if hasattr(self, 'puddle_group'):
            for puddle in getattr(self, 'puddle_group', []):
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

        self.game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen = self.game_surface

        self.active_players = []
        
        if b_id is None: # Non-versus setup
            p1_x = SCREEN_WIDTH // 2 - (50 if self.num_players == 2 else 0)
            self.player1 = Player(p1_x, SCREEN_HEIGHT - 30, player_id=1)
            self.player1.current_scale = 1.0 
            self.player1.exact_y = float(SCREEN_HEIGHT - TRANSITION_PLAYER_Y_NORMAL_OFFSET)
            self.active_players.append(self.player1)
            self.player1_boost = PlayerBoost(self.player1)
            self.all_sprites.add(self.player1_boost, self.player1)

            self.player2 = None
            self.player2_boost = None
            if self.num_players == 2:
                self.player2 = Player(SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT - 30, player_id=2)
                self.player2.current_scale = 1.0
                self.player2.exact_y = float(SCREEN_HEIGHT - TRANSITION_PLAYER_Y_NORMAL_OFFSET)
                self.active_players.append(self.player2)
                
                self.player2_boost = PlayerBoost(self.player2)
                self.all_sprites.add(self.player2_boost, self.player2)
        else: # Versus mode setup
            self.player1 = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30, player_id=b_id)
            self.player1.current_scale = 1.0 
            self.player1.exact_y = float(SCREEN_HEIGHT - TRANSITION_PLAYER_Y_NORMAL_OFFSET)
            self.active_players.append(self.player1)
            self.player1_boost = PlayerBoost(self.player1)
            self.all_sprites.add(self.player1_boost, self.player1)
            self.player2 = None
            self.player2_boost = None

        self.player_invuln_timer = 0
        self.SCROLL = INITIAL_SCROLL
        self.planet_index = 0  
        self.planet_sliding = True
        self.planet_y = -self.planets[0].get_height() if 0 in self.planets else 0
        
        self.current_background_layers = self.level_backgrounds[self.level]
        self.layer_offsets = [INITIAL_SCROLL] * PARALLAX_LAYERS

        self.create_enemy_wave()
        self.enemy_direction = 1
        self.headerbar.add(HeaderBar(self.screen, self.font))
        if self.game_mode in ["endless", "versus"]:
            self.headerbar.sprite.set_wave(self.wave_number)
        else:
            self.headerbar.sprite.set_level(self.level)
        angles = [0, 90, 180, 270]
        variants = ["satellite", "satellit2", "satellit3", "satellit4"]
        for i, variant in enumerate(variants):
            x_pos = 250 + (i * 190)
            self.bunkers.add(Bunker(x_pos, SCREEN_HEIGHT - 120, variant=variant, angle=angles[i]))

        self.ufo_timer = int(UFO_SPAWN_TIME * FPS)
        self.mini_boss_spawned = False
        self.boss_healthbar = None 
        
        self.level_cleared_timer = 0
        self.is_transition_active = False
        self.transition_state = None
        self.transition_timer = 0
        self.current_speed_factors = list(PARALLAX_SPEED_FACTORS)
        self.next_planet_index = None
        self.next_planet_y = 0
        self.next_planet_sliding = False
        self.decel_normal_frames = 0
        self.transitioning_back_timer = 0
        self.state = self.STATE_PLAYING

    def _present(self):
        self.display.fill((0, 0, 0))
        sw, sh = self.display.get_size()
        scale = min(sw / SCREEN_WIDTH, sh / SCREEN_HEIGHT)
        nw, nh = int(SCREEN_WIDTH * scale), int(SCREEN_HEIGHT * scale)
        scaled_surf = pygame.transform.scale(self.game_surface, (nw, nh))
        self.display.blit(scaled_surf, ((sw - nw) // 2, (sh - nh) // 2))
        pygame.display.flip()

    def _present_versus(self):
        self.display.fill((0, 0, 0))
        sw, sh = self.display.get_size()
        
        scale = min((sw / 2) / SCREEN_WIDTH, sh / SCREEN_HEIGHT)
        nw, nh = int(SCREEN_WIDTH * scale), int(SCREEN_HEIGHT * scale)
        
        surf1 = self.boards[1]['game_surface']
        surf2 = self.boards[2]['game_surface']
        
        scaled_p1 = pygame.transform.scale(surf1, (nw, nh))
        scaled_p2 = pygame.transform.scale(surf2, (nw, nh))
        
        total_w = nw * 2
        start_x = (sw - total_w) // 2
        start_y = (sh - nh) // 2
        
        self.display.blit(scaled_p1, (start_x, start_y))
        self.display.blit(scaled_p2, (start_x + nw, start_y))
        
        pygame.draw.line(self.display, (255, 255, 255), (start_x + nw, start_y), (start_x + nw, start_y + nh), 4)
        pygame.display.flip()

    def _spawn_bonus_item(self):
        roll = random.random()
        cumulative = 0.0
        chosen_points = 100
        
        for points, chance in BONUS_ITEM_PROBABILITIES.items():
            cumulative += chance
            if roll <= cumulative:
                chosen_points = points
                break
                
        x_pos = random.randint(100, SCREEN_WIDTH - 100)
        item = BonusPointItem(x_pos, -50, BONUS_ITEM_SPEED, chosen_points)
        self.bonus_items.add(item)
        self.all_sprites.add(item)

    def _run_transition(self):
        if not self.is_transition_active:
            self.transition_sound.play()
            self.is_transition_active = True
            self.transition_state = "amplify"
            self.leds.send_effect("A", "chase", 0, 255, 255, 255, speed=22, repeat=13, priority=2)
            self.current_speed_factors = list(PARALLAX_SPEED_FACTORS)
            self.decel_normal_frames = 0
            return

        def _ramp_up(factors, step, max_factor):
            return [min(f + step, max_factor) for f in factors]

        def _ramp_down(factors, step, target):
            return [max(f - step, target) for f in factors]

        if self.transition_state == "amplify":
            target_scale = TRANSITION_PLAYER_SCALE_MAX   
            target_bunker_y = TRANSITION_BUNKER_Y_DOWN 
        elif self.transition_state in ("hold", "decel_to_thresh"):
            target_scale = TRANSITION_PLAYER_SCALE_MAX
            target_bunker_y = TRANSITION_BUNKER_Y_DOWN
        else:
            target_scale = TRANSITION_PLAYER_SCALE_NORMAL   
            target_bunker_y = TRANSITION_BUNKER_Y_UP  

        for player in self.active_players:
            player.current_scale += (target_scale - player.current_scale) * TRANSITION_PLAYER_SCALE_EASING
            
        self.bunker_transition_y += (target_bunker_y - self.bunker_transition_y) * TRANSITION_BUNKER_EASING
        for b in self.bunkers:
            b.transition_y = self.bunker_transition_y

        if self.transition_state == "amplify":
            self.current_speed_factors = _ramp_up(
                self.current_speed_factors, AMPLIFY_STEP, AMPLIFY_MAX_FACTOR
            )
            if all(abs(f - AMPLIFY_MAX_FACTOR) < 1e-5 for f in self.current_speed_factors):
                self.current_background_layers = self.transition_background
                self.transition_state = "hold"
                self.transition_timer = TRANSITION_HOLD_FRAMES
            return

        if self.transition_state == "hold":
            if self.transition_timer == TRANSITION_HOLD_FRAMES - 10:
                self._spawn_bonus_item()
            if self.transition_timer == TRANSITION_HOLD_FRAMES - 90:
                self._spawn_bonus_item()
                
            self.transition_timer -= 1
            if self.transition_timer <= 0:
                self.transition_state = "decel_to_thresh"
            return

        if self.transition_state == "decel_to_thresh":
            self.current_speed_factors = _ramp_down(
                self.current_speed_factors, DECEL_STEP, THRESHOLD_FACTOR
            )
            if all(abs(f - THRESHOLD_FACTOR) < 1e-5 for f in self.current_speed_factors):
                self.transition_state = "decel_to_normal"
            return

        if self.transition_state == "decel_to_normal":
            self.decel_normal_frames += 1
            
            if self.decel_normal_frames == 160 and not self.next_planet_sliding:
                next_idx = self.planet_index + 1
                if next_idx in self.planets:
                    self.next_planet_index = next_idx
                    self.next_planet_y = -self.planets[next_idx].get_height()
                    self.next_planet_sliding = True
            
            if self.current_background_layers != self.level_backgrounds[self.level]:
                self.current_background_layers = self.level_backgrounds[self.level]

            if self.transition_timer > 0:
                self.transition_timer -= 1
                return

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

            if all_reached:
                self._spawn_miniboss()
                self.mini_boss_spawned = True
                self.is_transition_active = False
                self.transition_state = None
                self.state = self.STATE_PLAYING
                
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
        self.boss_spawn_sound.play()
        self.miniboss_group.add(boss)
        self.all_sprites.add(boss)
        
        if hasattr(boss, "fist_group"):
            self.all_sprites.add(boss.fist_group)
            
        self.boss_healthbar = BossHealthBar(boss)

    def _play_music(self, trak_path, volume = 1):
        if self.current_track != trak_path:
            pygame.mixer.music.load(trak_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
            self.current_track = trak_path

    def create_enemy_wave(self):
        if self.game_mode == "story":
            settings = ENEMY_WAVE_SETTINGS.get(self.level, ENEMY_WAVE_SETTINGS[1])
            rows = settings["rows"]
            cols = settings["cols"]
            self.enemy_speed = settings.get("speed", ENEMY_SPEED)
            self.enemy_shoot_chance = settings.get("shoot_chance", ENEMY_SHOOT_CHANCE)
            
            # Story Mode Drop-Skalierung
            self.enemy_move_down = int(STORY_ENEMY_BASE_MOVE_DOWN + (self.level - 1) * STORY_ENEMY_MOVE_DOWN_INCREMENT)
            
        else:
            # Procedural scaling for endless survival mode
            rows = min(ENDLESS_MAX_ROWS, ENDLESS_BASE_ROWS + (self.wave_number // ENDLESS_ROW_INCREMENT_WAVES)) 
            cols = ENDLESS_BASE_COLS
            self.enemy_speed = ENEMY_SPEED + (self.wave_number * ENDLESS_SPEED_INCREMENT)
            
            # Hier nutzen wir jetzt die neue Basis-Wahrscheinlichkeit:
            self.enemy_shoot_chance = ENDLESS_BASE_SHOOT_CHANCE + (self.wave_number * ENDLESS_SHOOT_CHANCE_INCREMENT)
            
            # Endless Mode Drop-Skalierung
            self.enemy_move_down = int(ENDLESS_ENEMY_BASE_MOVE_DOWN + (self.wave_number - 1) * ENDLESS_ENEMY_MOVE_DOWN_INCREMENT)
        
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
                
                for b in bullets:
                    b.pierce -= 1
                    if b.pierce <= 0:
                        b.kill()
                        
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
        
        laser_objects = []
        for boss in self.miniboss_group:
            if hasattr(boss, "laser_lines"):
                laser_objects.extend(list(boss.laser_lines))
        for bullet in list(self.enemy_bullets):
            if self._is_laser_line(bullet) and bullet not in laser_objects:
                laser_objects.append(bullet)
                
        for laser in laser_objects:
            hit_this_frame = False
            for player in self.active_players:
                if any(player.rect.colliderect(hitbox) for hitbox in laser.get_hitboxes()):
                    hit_this_frame = True
                    
            
            if hit_this_frame:
                player_hit = True
                self.lives -= getattr(laser, "damage", 1)  
                self.sfx_ufo_damage.play()
                laser.kill()
            
        for bullet in list(self.enemy_bullets):
            if self._is_laser_line(bullet):
                continue 
            
            for player in self.active_players:
                if pygame.sprite.collide_rect(bullet, player):
                    player_hit = True
                    dmg = getattr(bullet, "damage", 1)
                    self.lives -= dmg
                    
                    if isinstance(bullet, Fist):
                        exp = Explosion(bullet.rect.centerx, bullet.rect.centery, size=64)
                        self.explosions.add(exp)
                        self.all_sprites.add(exp)
                        
                    bullet.kill()
                    break

        in_puddle = False
        for puddle in list(self.puddle_group):
            active_rect = getattr(puddle, 'hitbox', puddle.rect)
            for player in self.active_players:
                if active_rect.colliderect(player.rect):
                    in_puddle = True
                    if getattr(self, 'poison_tick_timer', POISON_DAMAGE_DELAY) <= 1:
                        player.poison_debuff_timer = POISON_DEBUFF_DURATION
                        player.speed = int(player.base_speed * POISON_SPEED_MULTIPLIER)
                    break
            if in_puddle:
                break
                
        if in_puddle:
            if not hasattr(self, 'poison_tick_timer'):
                self.poison_tick_timer = POISON_DAMAGE_DELAY
            self.poison_tick_timer -= 1
            if self.poison_tick_timer <= 0:
                self.lives -= 1
                player_hit = True
                self.poison_tick_timer = 300
        else:
            self.poison_tick_timer = POISON_DAMAGE_DELAY

        if player_hit:
            self.sfx_ufo_damage.play()
            if self.lives > 0:
                for seg in range(1, 5):
                    self.leds.send_effect("A", "blink", seg, 255, 0, 0, speed=1, repeat=10, priority=2)
            else:
                self.game_over.play()
                self.leds.send_effect("A", "wipe", 99, 255, 0, 0, speed=50, repeat=1, priority=4)
                
                for player in self.active_players:
                    explosion = Explosion(player.rect.centerx, player.rect.centery)
                    self.explosions.add(explosion)
                    self.all_sprites.add(explosion)
                    player.kill()
                    
                if getattr(self, 'player1_boost', None):
                    self.player1_boost.kill()
                if getattr(self, 'player2_boost', None):
                    self.player2_boost.kill()
                    
                self.state = self.STATE_GAME_OVER

        for boss in list(self.miniboss_group):
            hits = pygame.sprite.spritecollide(boss, self.player_bullets, False)
            self.score += len(hits) * 100 #Damit die grünen Wixer auch punkte geben 
            for b in hits:
                hit_explosion = Explosion(boss.rect.centerx, boss.rect.centery, size=48)
                self.explosions.add(hit_explosion)
                self.boss_death_sound.play()
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


        for enemy in self.enemies:
            for player in self.active_players:
                if enemy.rect.bottom >= player.rect.top:
                    self.state = self.STATE_GAME_OVER
                    break

        for player in self.active_players:
            powerup_hits = pygame.sprite.spritecollide(player, self.powerups, True)
            if powerup_hits:
                self.collect_points_sound.play()
                self.leds.send_effect("A", "blink", 1, 0, 255, 255, speed=10, repeat=5, priority=5)
                for pu in powerup_hits:
                    effect = CollectEffect(pu.rect.centerx, pu.rect.centery)
                    self.explosions.add(effect)
                    self.all_sprites.add(effect)
                    
                    if pu.type == "comet":
                        comet = Comet(SCREEN_WIDTH, COMET_SPEED, COMET_ROTATION_SPEED, TIE_FIGHTER_SPEED, TIE_FIGHTER_ROTATION_SPEED, TIE_FIGHTER_SIZE)
                        self.comets.add(comet)
                        self.all_sprites.add(comet)
                    elif pu.type == "bunker":
                        self.rebuild_bunkers()
                    elif pu.type == "hp":
                        self.lives += 1
                    elif pu.type == "speed":
                        player.speed = int(player.base_speed * POWERUP_SPEED_MULTIPLIER)
                        player.speed_timer = FPS * POWERUP_SPEED_DURATION
                    elif pu.type == "doubleshot":
                        player.weapon_type = "double"
                        player.weapon_timer = FPS * POWERUP_DOUBLESHOT_DURATION
                    elif pu.type == "trippleshot":
                        player.weapon_type = "triple"
                        player.weapon_timer = FPS * POWERUP_TRIPLESHOT_DURATION

        for comet in self.comets:
            comet_enemy_hits = pygame.sprite.spritecollide(comet, self.enemies, True)
            if comet_enemy_hits:
                self.enemy_explosion.play()
                for enemy in comet_enemy_hits:
                    explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                    self.explosions.add(explosion)
                    self.all_sprites.add(explosion)
                    self.score += 100

        for boss in list(self.miniboss_group):
            comet_boss_hits = pygame.sprite.spritecollide(boss, self.comets, True)
            if comet_boss_hits:
                self.enemy_explosion.play()
                for comet in comet_boss_hits:
                    explosion = Explosion(comet.rect.centerx, comet.rect.centery, size=128)
                    self.explosions.add(explosion)
                    self.all_sprites.add(explosion)

    def _draw_hud(self):
        score_surf = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        lives_surf = self.font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        self.screen.blit(score_surf, (10, 10))
        self.screen.blit(lives_surf, (SCREEN_WIDTH - lives_surf.get_width() - 10, 10))

    def _draw_planet(self):
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

        rect.top = int(self.planet_y)
        self.screen.blit(planet_img, rect)
        
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
        is_victory = (self.state == self.STATE_VICTORY)
        
        self.end_screen.draw(
            self.screen, 
            self.state, 
            self.score, 
            self.player1_name,
            self.player2_name,
            self.selected_key_coords_p1,
            self.selected_key_coords_p2,
            self.p1_done,
            self.p2_done,
            num_players=self.num_players,
            is_victory=is_victory,
            game_mode=self.game_mode,
            wave_number=self.wave_number
        )

    def advance_level(self):
        self.level += 1
        if self.level > self.MAX_LEVEL:
            pygame.mixer.music.stop()
            self._play_music(self.music_victory, 0.7) 
            self.victory_voice.play()
            self.leds.send_effect("A", "blink", 99, 255, 255, 0, speed=5, repeat=10, priority=3)
            self.state = self.STATE_VICTORY
            return
            
        self.headerbar.sprite.set_level(self.level)
        self.mini_boss_spawned = False
        
        self.boss_healthbar = None
        self.bonus_items.empty()
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
        if self.mini_boss_spawned:
            self.level += 1
            if self.level > self.MAX_LEVEL:
                self.state = self.STATE_VICTORY
                return
            self.headerbar.sprite.set_level(self.level)
            self.current_background_layers = self.level_backgrounds[self.level]
            self.layer_offsets = [INITIAL_SCROLL] * PARALLAX_LAYERS

    def _draw_board_frozen(self):
        for idx, layer_img in enumerate(self.current_background_layers):
            offset = self.layer_offsets[idx]
            layer_h = layer_img.get_height()
            self.screen.blit(layer_img, (0, offset))
            self.screen.blit(layer_img, (0, offset - layer_h))
            
        self._draw_planet()
        self.bunkers.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.headerbar.draw(self.screen)
        
        font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 30)
        over_surf = font.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(over_surf, over_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))

    def _update_gameplay(self, keys):
        if self.mini_boss_spawned:
            boss_tracks = {
                        1: self.music_boss_1,
                        2: self.music_boss_2,
                        3: self.music_boss_3,
                        4: self.music_boss_4,
                        5: self.music_boss_5
                    }
            current_boss_music = boss_tracks.get(self.level, self.music_boss_1)
            self._play_music(current_boss_music, 0.7)
        else:
            self._play_music(self.music_level, 0.7)

        target_y = SCREEN_HEIGHT - TRANSITION_PLAYER_Y_NORMAL_OFFSET 
        for player in self.active_players:
            if abs(player.exact_y - target_y) > 0.5:
                player.exact_y += (target_y - player.exact_y) * TRANSITION_PLAYER_EASING_PLAYING
        
        for player in self.active_players:
            player.move(keys, SCREEN_WIDTH)
            player.update_buffs()      
        
        if getattr(self, 'player1_boost', None):
            self.player1_boost.update(is_hyperboosting=False)  
        if getattr(self, 'player2_boost', None):
            self.player2_boost.update(is_hyperboosting=False)

        self.player_bullets.update()
        self.enemy_bullets.update()
        self.bunkers.update()
        self.miniboss_group.update(self.player1,
                       self.all_sprites,
                       self.enemy_bullets,
                       self.explosions,
                       SCREEN_WIDTH,
                       SCREEN_HEIGHT,
                       self.puddle_group,
                       active_players=self.active_players)
        self.puddle_group.update()
        self.explosions.update()
        self.powerups.update(SCREEN_HEIGHT)
        self.comets.update(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.enemies.update()
        self.ufo_group.update()
        self.bonus_items.update()
        
        for bullet in self.player_bullets:
            self.handle_bunker_collision(bullet, self.bunkers)
        for bomb in self.enemy_bullets:
            self.handle_bunker_collision(bomb, self.bunkers)

        self._handle_enemy_movement()
        self._enemy_shooting()
        
        self.ufo_timer -= 1
        if self.ufo_timer <= 0 or self.player_shots >= UFO_SHOT_THRESHOLD:
            self._spawn_ufo()
            self.ufo_timer = int(UFO_SPAWN_TIME * FPS)
            self.player_shots = 0
        
        self._check_collisions()
        
        if not self.enemies and not self.explosions:
            if self.game_mode == "story":
                if not self.mini_boss_spawned:
                    self.state = self.STATE_LEVEL_CLEARED
                    self.level_cleared_timer = 5 * FPS
                elif self.mini_boss_spawned and not self.miniboss_group:
                    self.advance_level()
            elif self.game_mode == "endless" or self.game_mode == "versus":
                if not getattr(self, '_endless_wave_spawned', False):
                    self.wave_number += 1
                    self.headerbar.sprite.set_wave(self.wave_number)  # <--- NEUE ZEILE
                    self.create_enemy_wave()
                    self.score += 500
                    self._endless_wave_spawned = True
                    
                    if self.wave_number % 5 == 0:
                        self.planet_index = (self.planet_index + 1) % self.MAX_LEVEL
                        if self.planet_index in self.planets:
                            self.planet_y = -self.planets[self.planet_index].get_height()
                            self.planet_sliding = True
                        self.current_background_layers = self.level_backgrounds[(self.planet_index % self.MAX_LEVEL) + 1]
                        self.layer_offsets = [INITIAL_SCROLL] * PARALLAX_LAYERS
        else:
            if self.game_mode == "endless" or self.game_mode == "versus":
                self._endless_wave_spawned = False

        for idx, layer_img in enumerate(self.current_background_layers):
            offset = self.layer_offsets[idx]
            layer_h = layer_img.get_height()
            self.screen.blit(layer_img, (0, offset))
            self.screen.blit(layer_img, (0, offset - layer_h))
            self.layer_offsets[idx] = (offset + BASE_SCROLL_SPEED * self.current_speed_factors[idx]) % layer_h
        
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

    def run(self):
        self.led_heartbeat_timer = 0

        while True:
            self.clock.tick(FPS)
            
            self.led_heartbeat_timer -= 1
            if self.led_heartbeat_timer <= 0:
                self.leds.send_effect("A", "pulse", 99, 0, 255, 0, speed=50, repeat=0, priority=1)
                self.led_heartbeat_timer = 1
                
            # --- Bestimme den globalen Zustand sicher ---
            current_state = self.state
            if self.state != self.STATE_MENU and self.game_mode == "versus" and hasattr(self, 'boards') and self.boards:
                b1_state = self.boards.get(1, {}).get('state', self.STATE_GAME_OVER)
                b2_state = self.boards.get(2, {}).get('state', self.STATE_GAME_OVER)
                # Das Spiel läuft weiter, solange noch MINDESTENS EIN Spieler lebt
                if b1_state == self.STATE_PLAYING or b2_state == self.STATE_PLAYING:
                    current_state = self.STATE_PLAYING
                else:
                    current_state = self.STATE_GAME_OVER
            # --------------------------------------------------

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                    self.state = self.STATE_MENU
                    current_state = self.STATE_MENU
                    self.p1_done = False  
                    self.p2_done = False
                    continue
                
                if current_state == self.STATE_MENU:
                    self._play_music(self.music_intro, 0.7)
                    self.leds.send_effect("A", "pulse", 99, 0, 255, 0, speed=20, repeat=10, priority=1)
                    if event.type == pygame.KEYDOWN:
                        
                        # --- Navigation Logic ---
                        if event.key in (pygame.K_w, pygame.K_UP):
                            if self.menu_selection == 2: self.menu_selection = 0
                            elif self.menu_selection == 3: self.menu_selection = 1
                            elif self.menu_selection == 4: self.menu_selection = 2
                        elif event.key in (pygame.K_s, pygame.K_DOWN):
                            if self.menu_selection == 0: self.menu_selection = 2
                            elif self.menu_selection == 1: self.menu_selection = 3
                            elif self.menu_selection in (2, 3): self.menu_selection = 4
                        elif event.key in (pygame.K_a, pygame.K_LEFT):
                            if self.menu_selection == 1: self.menu_selection = 0
                            elif self.menu_selection == 3: self.menu_selection = 2
                        elif event.key in (pygame.K_d, pygame.K_RIGHT):
                            if self.menu_selection == 0: self.menu_selection = 1
                            elif self.menu_selection == 2: self.menu_selection = 3
                            
                        # --- Selection Confirmation ---
                        elif event.key in (pygame.K_SPACE, pygame.K_KP0):
                            if self.menu_selection == 0:
                                self.game_mode, self.num_players = "story", 1
                                self._reset()
                                current_state = self.STATE_PLAYING
                            elif self.menu_selection == 1:
                                self.game_mode, self.num_players = "endless", 1
                                self.wave_number = 1
                                self._reset()
                                current_state = self.STATE_PLAYING
                            elif self.menu_selection == 2:
                                self.game_mode, self.num_players = "story", 2
                                self._reset()
                                current_state = self.STATE_PLAYING
                            elif self.menu_selection == 3:
                                self.game_mode, self.num_players = "endless", 2
                                self.wave_number = 1
                                self._reset()
                                current_state = self.STATE_PLAYING
                            elif self.menu_selection == 4:
                                self.game_mode, self.num_players = "versus", 2
                                self._reset()
                                current_state = self.STATE_PLAYING
                        
                elif current_state == self.STATE_PLAYING: 
                    if event.type == pygame.KEYDOWN:
                        if self.game_mode == "versus":
                            if event.key == pygame.K_SPACE:
                                self._load_context(1)
                                if getattr(self, 'player1', None) and self.player1.alive() and self.state == self.STATE_PLAYING:
                                    bullet = self.player1.shoot()
                                    if bullet:
                                        self.laser_sound.play()
                                        self.player_bullets.add(bullet)
                                        self.all_sprites.add(bullet)
                                        self.player_shots += 1
                                self._save_context(1)
                            elif event.key == pygame.K_KP0:
                                self._load_context(2)
                                if getattr(self, 'player1', None) and self.player1.alive() and self.state == self.STATE_PLAYING:
                                    bullet = self.player1.shoot()
                                    if bullet:
                                        self.laser_sound.play()
                                        self.player_bullets.add(bullet)
                                        self.all_sprites.add(bullet)
                                        self.player_shots += 1
                                self._save_context(2)
                        else:
                            if event.key == pygame.K_SPACE and getattr(self, 'player1', None) and self.player1.alive():
                                bullet = self.player1.shoot()
                                if bullet:
                                    self.laser_sound.play()
                                    self.player_bullets.add(bullet)
                                    self.all_sprites.add(bullet)
                                    self.player_shots += 1
                            if event.key == pygame.K_KP0 and self.num_players == 2 and getattr(self, 'player2', None) and self.player2.alive():
                                bullet = self.player2.shoot()
                                if bullet:
                                    self.laser_sound.play()
                                    self.player_bullets.add(bullet)
                                    self.all_sprites.add(bullet)
                                    self.player_shots += 1
                        if event.key == pygame.K_r:
                            self._reset()
                            current_state = self.STATE_PLAYING
                
                elif current_state == self.STATE_LEVEL_CLEARED:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self._reset()
                            current_state = self.STATE_PLAYING

                elif current_state in (self.STATE_GAME_OVER, self.STATE_VICTORY):
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self._reset()
                            current_state = self.STATE_PLAYING

                        if not self.p1_done:
                            if event.key == pygame.K_a: self.selected_key_coords_p1[0] = (self.selected_key_coords_p1[0] - 1) % 7
                            elif event.key == pygame.K_d: self.selected_key_coords_p1[0] = (self.selected_key_coords_p1[0] + 1) % 7
                            elif event.key == pygame.K_w: self.selected_key_coords_p1[1] = (self.selected_key_coords_p1[1] - 1) % 4
                            elif event.key == pygame.K_s: self.selected_key_coords_p1[1] = (self.selected_key_coords_p1[1] + 1) % 4
                            elif event.key == pygame.K_SPACE:
                                col, row = self.selected_key_coords_p1
                                char = self.end_screen.keys[row][col]

                                if char == '<':
                                    self.player1_name = self.player1_name[:-1] 
                                elif char == 'OK':
                                    if len(self.player1_name) > 0:
                                        self.p1_done = True
                                else:
                                    if len(self.player1_name) < 12: 
                                        self.player1_name += char
                                        
                        if self.num_players == 2 and not self.p2_done:
                            if event.key == pygame.K_LEFT: self.selected_key_coords_p2[0] = (self.selected_key_coords_p2[0] - 1) % 7
                            elif event.key == pygame.K_RIGHT: self.selected_key_coords_p2[0] = (self.selected_key_coords_p2[0] + 1) % 7
                            elif event.key == pygame.K_UP: self.selected_key_coords_p2[1] = (self.selected_key_coords_p2[1] - 1) % 4
                            elif event.key == pygame.K_DOWN: self.selected_key_coords_p2[1] = (self.selected_key_coords_p2[1] + 1) % 4
                            elif event.key == pygame.K_KP0:
                                col, row = self.selected_key_coords_p2
                                char = self.end_screen.keys[row][col]

                                if char == '<':
                                    self.player2_name = self.player2_name[:-1] 
                                elif char == 'OK':
                                    if len(self.player2_name) > 0:
                                        self.p2_done = True
                                else:
                                    if len(self.player2_name) < 12: 
                                        self.player2_name += char

                        if (self.num_players == 1 and self.p1_done) or (self.num_players == 2 and self.p1_done and self.p2_done):
                            self.save_highscore()
                            self.state = self.STATE_MENU 
                            current_state = self.STATE_MENU
                            self.p1_done = False
                            self.p2_done = False

            if current_state == self.STATE_MENU:
                self._draw_planet()
                self.main_menu.draw(self.screen, getattr(self, 'menu_selection', 0))
                self._present()

            elif current_state == self.STATE_PLAYING:
                keys = pygame.key.get_pressed()
                if self.game_mode == "versus":
                    for b_id in (1, 2):
                        self._load_context(b_id)
                        # Aktualisiere das Board nur, wenn dieser Spieler noch lebt
                        if self.state == self.STATE_PLAYING:
                            self._update_gameplay(keys)
                        # Friere das Board ein, falls dieser Spieler bereits Game Over ist
                        elif self.state == self.STATE_GAME_OVER:
                            self.explosions.update()
                            self._draw_board_frozen()
                        self._save_context(b_id)
                    self._present_versus()
                else:
                    self._update_gameplay(keys)
                    self._present()

            elif current_state == self.STATE_LEVEL_CLEARED:
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

                self.explosions.update()      
                self.player_bullets.update()  
                self.enemy_bullets.update()
                self.powerups.update(SCREEN_HEIGHT)
                self.comets.update(SCREEN_WIDTH, SCREEN_HEIGHT)
                self.ufo_group.update()
                self.puddle_group.update()
                self.bonus_items.update()     
                
                for player in self.active_players:
                    collected_bonus = pygame.sprite.spritecollide(player, self.bonus_items, True)
                    for item in collected_bonus:
                        self.collect_points_sound.play()
                        self.score += item.points
                        effect = CollectEffect(item.rect.centerx, item.rect.centery)
                        self.explosions.add(effect)
                        self.all_sprites.add(effect)
                        self.leds.send_effect("A", "blink", 1, 255, 255, 0, speed=10, repeat=3, priority=5)
                
                if self.transition_state == "amplify":
                    target_y = SCREEN_HEIGHT * TRANSITION_PLAYER_Y_AMPLIFY_PCT
                    easing_speed_y = TRANSITION_PLAYER_EASING_UP  
                elif self.transition_state in ("hold", "decel_to_thresh"):
                    target_y = SCREEN_HEIGHT * TRANSITION_PLAYER_Y_HOLD_PCT
                    easing_speed_y = TRANSITION_PLAYER_EASING_DOWN  
                else: 
                    target_y = SCREEN_HEIGHT - TRANSITION_PLAYER_Y_NORMAL_OFFSET 
                    easing_speed_y = TRANSITION_PLAYER_EASING_RETURN
                    
                for player in self.active_players:
                    player.exact_y += (target_y - player.exact_y) * easing_speed_y
                
                keys = pygame.key.get_pressed()
                for player in self.active_players:
                    player.move(keys, SCREEN_WIDTH)
                    player.update_buffs()
                
                if getattr(self, 'player1_boost', None):
                    self.player1_boost.update(is_hyperboosting=True)
                if getattr(self, 'player2_boost', None):
                    self.player2_boost.update(is_hyperboosting=True)
                
                self._run_transition()
                self.bunkers.update()
                
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
                if self.game_mode == "versus" and getattr(self, '_versus_end_surface_created', False) == False:
                    self.game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    self.screen = self.game_surface
                    self._versus_end_surface_created = True

                self.explosions.update()
                if self.game_mode == "versus":
                    self.end_screen.draw(
                        self.screen, 
                        self.state, 
                        self.boards[1]['score'],
                        self.player1_name,
                        self.player2_name,
                        self.selected_key_coords_p1,
                        self.selected_key_coords_p2,
                        self.p1_done,
                        self.p2_done,
                        num_players=self.num_players,
                        is_victory=False,
                        game_mode=self.game_mode,
                        wave_number=self.boards[1]['wave_number'],
                        score_p2=self.boards[2]['score'],
                        wave_p2=self.boards[2]['wave_number']
                    )
                else:
                    self._draw_end_screen()
                self.explosions.draw(self.screen)
                self._present()

    def save_highscore(self):
        if self.game_mode == "versus":
            filename_base = "highscores_mp.json"
            mode_key = "mp_versus"
        elif self.num_players == 1:
            filename_base = "highscores_sp.json"
            mode_key = "sp_" + self.game_mode
        else:
            filename_base = "highscores_mp.json"
            mode_key = "mp_" + self.game_mode
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        root_path = os.path.dirname(os.path.dirname(base_path))
        filename = os.path.join(root_path, filename_base)
        
        data = {}
        if os.path.exists(filename):
            with open(filename, "r") as f:
                try: 
                    data = json.load(f)
                    if not isinstance(data, dict):
                        data = {}
                except:
                    data = {}
        
        if mode_key not in data:
            data[mode_key] = []
        
        if self.game_mode == "versus":
            # Save Player 1 as a separate entry
            entry_p1 = {
                "name": self.player1_name,
                "score": self.boards[1]['score'],
                "wave": self.boards[1]['wave_number']
            }
            # Save Player 2 as a separate entry
            entry_p2 = {
                "name": self.player2_name,
                "score": self.boards[2]['score'],
                "wave": self.boards[2]['wave_number']
            }
            data[mode_key].append(entry_p1)
            data[mode_key].append(entry_p2)
        else:
            if self.num_players == 1: 
                name_entry = self.player1_name
            else: 
                name_entry = f"{self.player1_name} & {self.player2_name}"
                
            entry = {"name": name_entry, "score": self.score}
            if self.game_mode == "endless":
                entry["wave"] = self.wave_number
            data[mode_key].append(entry)
        
        # Sort and keep top 5
        data[mode_key].sort(key=lambda x: x.get("score", 0), reverse=True)
        data[mode_key] = data[mode_key][:5]
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        
        print(f"Erfolg! Gespeichert in: {filename}")