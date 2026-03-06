import pygame
import random
import sys
from src.config.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, PLAYER_SPEED,
    ENEMY_SPEED, BULLET_SPEED, UFO_SPAWN_TIME,
    UFO_SCORE_OPTIONS, UFO_SHOT_THRESHOLD,
    BASE_SCROLL_SPEED, INITIAL_SCROLL, PARALLAX_LAYERS, PARALLAX_SPEED_FACTORS,
    LEVEL_BACKGROUND_PATTERN, TRANSITION_BACKGROUND_PATTERN,
    ENEMY_SHOOT_CHANCE,
    ENEMY_WAVE_SETTINGS, MINIBOSS_SETTINGS,
    POWERUP_DROP_CHANCES, POWERUP_FALL_SPEED, COMET_SPEED, COMET_ROTATION_SPEED,
    POWERUP_SPEED_DURATION, POWERUP_DOUBLESHOT_DURATION, POWERUP_TRIPLESHOT_DURATION,
        POWERUP_SPEED_MULTIPLIER, TIE_FIGHTER_SPEED, TIE_FIGHTER_SIZE, TIE_FIGHTER_ROTATION_SPEED,
        AMPLIFY_STEP, DECEL_STEP, AMPLIFY_MAX_FACTOR, THRESHOLD_FACTOR, TRANSITION_HOLD_FRAMES,
        PLANET_SCROLL_FACTOR
    )
from src.game.player import Player, PlayerBoost
from src.game.enemy import Enemy
from src.game.explosion import Explosion, BunkerRespawnEffect
from src.game.ufo import UFO
from src.game.Boss_small_1 import BossSmall1
from src.game.boss_small_2 import BossSmall2
from src.game.boss_small_3 import BossSmall3
from src.game.boss_small_4 import BossSmall4
from src.game.fist import Fist
from src.game.endboss import EndBoss
from src.game.bullet import Bullet
from src.game.bunker import Bunker
from src.game.headerbar import HeaderBar
from src.game.powerup import PowerUp, Comet
from src.game.mainmenue import MainMenu

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
        self.main_menu = MainMenu(self.font, self.level_backgrounds[1][0])
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
                img = pygame.transform.smoothscale(img, (width, height))
            self.planets[idx] = img

        # After loading all planets, initialize animation for the first planet
        if 0 in self.planets:
            self.planet_y = -self.planets[0].get_height()
        else:
            self.planet_y = 0
        self.planet_sliding = True

        self.mini_boss_spawned = False
        self.level_cleared_timer = 0
        self.miniboss_group = pygame.sprite.Group()
        # Transition related flags
        self.is_transition_active = False
        self.transition_state = None
        self.transition_timer = 0
        # Mutable speed factors used during transition phases
        self.current_speed_factors = list(PARALLAX_SPEED_FACTORS)

    def handle_bunker_collision(self, bullet, bunker_group):
        """Exact mask collision – apply bullet‑specific damage to a bunker."""
        hit_bunker = pygame.sprite.spritecollideany(
            bullet, bunker_group, pygame.sprite.collide_mask
        )
        if hit_bunker:
            # bullets may carry a custom damage attribute (default = 1)
            damage = getattr(bullet, "damage", 1)
            for _ in range(damage):
                hit_bunker.take_damage()
                
            # Explosion bei Faust-Treffer auf dem Bunker
            if isinstance(bullet, Fist):
                from src.game.explosion import Explosion
                import random
                
                # 1. Haupt-Explosion (groß, genau am Einschlagspunkt)
                impact_x = (bullet.rect.centerx + hit_bunker.rect.centerx) // 2
                impact_y = (bullet.rect.centery + hit_bunker.rect.centery) // 2
                
                main_explosion = Explosion(impact_x, impact_y, size=64)
                self.explosions.add(main_explosion)
                self.all_sprites.add(main_explosion)
                
                # 2. Zusätzliche kleine Explosion mit garantiertem Abstand
                min_distance_sq = 40 ** 2  # Mindestabstand zum Quadrat (40 Pixel)
                sec_x, sec_y = impact_x, impact_y
                
                found = False
                for _ in range(10):
                    offset_x = random.randint(-45, 45)
                    offset_y = random.randint(-45, 45)
                    sec_x = hit_bunker.rect.centerx + offset_x
                    sec_y = hit_bunker.rect.centery + offset_y
                    dist_sq = (sec_x - impact_x)**2 + (sec_y - impact_y)**2
                    if dist_sq >= min_distance_sq:
                        found = True
                        break
                if not found:
                    sec_x, sec_y = impact_x, impact_y
                secondary_explosion = Explosion(sec_x, sec_y, size=32)
                
                self.explosions.add(secondary_explosion)
                self.all_sprites.add(secondary_explosion)

            # If the bunker was destroyed, spawn a large explosion (size 64)
            if not hit_bunker.alive():
                from src.game.explosion import Explosion
                explosion = Explosion(hit_bunker.rect.centerx,
                                      hit_bunker.rect.centery,
                                      size=64)
                self.explosions.add(explosion)
                self.all_sprites.add(explosion)
                
            # Pierce System für Bullets berücksichtigen
            if hasattr(bullet, "pierce"):
                bullet.pierce -= 1
                if bullet.pierce <= 0:
                    bullet.kill()
            else:
                bullet.kill()

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
        # Reset for a fresh game (menu start or full restart)
        self.score = 0
        self.level = 1
        self.planet_index = 0  # reset planet sequence for a fresh game (planet_0 visible)
        self.lives = 3
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
        self.all_sprites = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.bunkers = pygame.sprite.Group()
        self.ufo_group = pygame.sprite.Group()
        
        self.powerups = pygame.sprite.Group()
        self.comets = pygame.sprite.Group()
        
        self.headerbar = pygame.sprite.GroupSingle()
        self.SCROLL = INITIAL_SCROLL  # reset scroll
        # Reset background to level 1 (or current level after reset)
        self.current_background_layers = self.level_backgrounds[self.level]
        self.layer_offsets = [INITIAL_SCROLL] * PARALLAX_LAYERS
        
        self.all_sprites.add(self.player)
        
        # Player Boost erzeugen
        self.player_boost = PlayerBoost(self.player)
        self.all_sprites.add(self.player_boost)
        
        self.create_enemy_wave()
        self.enemy_direction = 1
        self.enemy_move_down = 10
        # Header bar
        self.headerbar.add(HeaderBar(self.screen, self.font))
        # Bunkers (satellites)
        angles = [0, 90, 180, 270]
        variants = ["satellite", "satellit2", "satellit3", "satellit4"]
        for i, variant in enumerate(variants):
            x_pos = 250 + (i * 190)
            self.bunkers.add(
                Bunker(
                    x_pos,
                    SCREEN_HEIGHT - 120,
                    variant=variant,
                    angle=angles[i],
                )
            )
        self.ufo_timer = int(UFO_SPAWN_TIME * FPS)
        self.player_shots = 0
        # Mini‑boss flags reset
        self.mini_boss_spawned = False
        self.miniboss_group.empty()
        self.level_cleared_timer = 0
        # Reset transition flags for a fresh start
        self.is_transition_active = False
        self.transition_state = None
        self.transition_timer = 0
        self.current_speed_factors = list(PARALLAX_SPEED_FACTORS)

    def _present(self):
        """Blit the game surface onto the full‑screen display with black borders and flip."""
        self.display.fill((0, 0, 0))
        x = (self.full_w - SCREEN_WIDTH) // 2
        y = (self.full_h - SCREEN_HEIGHT) // 2
        self.display.blit(self.game_surface, (x, y))
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
            # start from the normal per‑layer factors
            self.current_speed_factors = list(PARALLAX_SPEED_FACTORS)
            return

        # Helper lambdas for ramping up/down
        def _ramp_up(factors, step, max_factor):
            return [min(f + step, max_factor) for f in factors]

        def _ramp_down(factors, step, target):
            return [max(f - step, target) for f in factors]

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
                # Advance planet index after each completed transition
                self.planet_index += 1
                # Reset planet animation for the new planet
                if self.planet_index in self.planets:
                    self.planet_y = -self.planets[self.planet_index].get_height()
                else:
                    self.planet_y = 0
                self.planet_sliding = True
                # WICHTIG: Faktoren final festschreiben
                self.current_speed_factors = list(PARALLAX_SPEED_FACTORS)
            return


    def _play_music(self, trak_path, volume = 0.2):
        if self.current_track != trak_path:
            pygame.mixer.music.load(trak_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
            self.current_track = trak_path

    def create_enemy_wave(self):
        """Create normal enemy wave based on current level settings."""
        settings = ENEMY_WAVE_SETTINGS.get(self.level, ENEMY_WAVE_SETTINGS[1])
        rows = settings["rows"]
        cols = settings["cols"]
        x_margin, y_margin = 50, 100
        spacing_x, spacing_y = 80, 60
        for row in range(int(rows)):
            for col in range(int(cols)):
                x = x_margin + col * spacing_x
                y = y_margin + row * spacing_y
                enemy = Enemy(x, y, row)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
        self.enemy_speed = settings.get("speed", ENEMY_SPEED)
        self.enemy_shoot_chance = settings.get("shoot_chance", ENEMY_SHOOT_CHANCE)

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
        hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, True, False)
        if hits:
            self.enemy_explosion.play()
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
                            break # Verhindert, dass ein Gegner 2 Items droppt
                        
            self.score += len(hits) * 100

        # UFO vs player bullet
        bonushits = pygame.sprite.groupcollide(self.ufo_group, self.player_bullets, True, False)
        if bonushits:
            for ufo, bullets in bonushits.items():
                self.score += random.choice(UFO_SCORE_OPTIONS)
                explosion = Explosion(ufo.rect.centerx, ufo.rect.centery, size=48)
                self.explosions.add(explosion)
                self.all_sprites.add(explosion)
                for b in bullets:
                    b.pierce -= 1
                    if b.pierce <= 0:
                        b.kill()

        # Player vs enemy bullet collisions
        if pygame.sprite.spritecollide(self.player, self.enemy_bullets, True):
            self.ufo_damage.play()
            self.lives -= 1
            if self.lives <= 0:
                self.game_over.play()
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
                self.all_sprites.add(hit_explosion)
                boss.hit()
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
            return

        # Position the planet using its top coordinate
        rect.top = int(self.planet_y)
        self.screen.blit(planet_img, rect)

    def _draw_end_screen(self):
        self.screen.fill((0, 0, 0))
        if self.state == self.STATE_GAME_OVER:
            msg = "Game Over"
            color = (255, 0, 0)
        else:
            if self.level > self.MAX_LEVEL:
                msg = "You beat all 5 levels!"
            else:
                msg = "You Win!"
            color = (0, 255, 0)
        msg_surf = self.font.render(msg, True, color)
        score_surf = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        instr_surf = self.font.render("Press R to Restart or Q to Quit", True, (255, 255, 255))
        self.screen.blit(msg_surf, (SCREEN_WIDTH // 2 - msg_surf.get_width() // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, SCREEN_HEIGHT // 3 + 40))
        self.screen.blit(instr_surf, (SCREEN_WIDTH // 2 - instr_surf.get_width() // 2, SCREEN_HEIGHT // 2))
        self._present()

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
        if hasattr(boss, "fist_group"):
            self.all_sprites.add(boss.fist_group)
        self.miniboss_group.add(boss)
        self.all_sprites.add(boss)

    def advance_level(self):
        self.level += 1
        if self.level > self.MAX_LEVEL:
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
        while True:
            self.clock.tick(FPS)
            
            # --- 1. EVENT HANDLING (NUR EINGABEN) ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if self.state == self.STATE_MENU:
                    self._play_music(self.music_intro, 0.7)
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self._reset() # Zuerst resetten
                        self.state = self.STATE_PLAYING
                
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
                        elif event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
                
                elif self.state in (self.STATE_GAME_OVER, self.STATE_VICTORY, self.STATE_LEVEL_CLEARED):
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self._reset()
                            self.state = self.STATE_PLAYING
                        elif event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()

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

                # --- 1. Spieler-Logik & Buffs ---
                keys = pygame.key.get_pressed()
                self.player.move(keys, SCREEN_WIDTH)
                self.player.update_buffs()      
                self.player_boost.update()  

                # --- 2. ALLE GRUPPEN UPDATEN (Jede strikt nur 1x!) ---
                self.player_bullets.update()
                self.enemy_bullets.update()
                self.bunkers.update()
                self.miniboss_group.update(self.player, all_sprites=self.all_sprites, enemy_bullets=self.enemy_bullets, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
                self.explosions.update()
                self.powerups.update(SCREEN_HEIGHT)
                self.comets.update(SCREEN_WIDTH, SCREEN_HEIGHT)
                self.enemies.update()
                self.ufo_group.update()
                
                # --- 3. Kollisionen mit Bunkern prüfen ---
                for bullet in self.player_bullets:
                    self.handle_bunker_collision(bullet, self.bunkers)
                for bomb in self.enemy_bullets:
                    self.handle_bunker_collision(bomb, self.bunkers)

                # --- 4. Timer, Gegner-Logik & generelle Kollisionen ---
                self._handle_enemy_movement()
                self._enemy_shooting()
                
                self.ufo_timer -= 1
                if self.ufo_timer <= 0 or self.player_shots >= UFO_SHOT_THRESHOLD:
                    self._spawn_ufo()
                    self.ufo_timer = int(UFO_SPAWN_TIME * FPS)
                    self.player_shots = 0
                
                self._check_collisions()
                
                # --- 5. Level Progress Check ---
                if not self.enemies and not self.mini_boss_spawned and not self.explosions:
 
                    self.state = self.STATE_LEVEL_CLEARED
                    self.level_cleared_timer = 5 * FPS
                elif self.mini_boss_spawned and not self.miniboss_group:
                    self.advance_level()

                # --- 6. Zeichnen ---
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
                # Run transition logic (amplify, hold, decelerate, load next level)
                self._run_transition()
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