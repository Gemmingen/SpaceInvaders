import pygame
import random
import sys
from src.config.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, PLAYER_SPEED,
    ENEMY_SPEED, BULLET_SPEED, UFO_SPAWN_TIME,
    UFO_SCORE_OPTIONS, UFO_SHOT_THRESHOLD,
    BACKGROUND_SCROLL_SPEED, SCROLL, ENEMY_SHOOT_CHANCE,
    ENEMY_WAVE_SETTINGS, MINIBOSS_SETTINGS,
)
from src.game.player import Player
from src.game.enemy import Enemy
from src.game.ufo import UFO
from src.game.Boss_small_1 import BossSmall1
from src.game.boss_small_2 import BossSmall2
from src.game.boss_small_3 import BossSmall3
from src.game.boss_small_4 import BossSmall4
from src.game.endboss import EndBoss
from src.game.bullet import Bullet
from src.game.bunker import Bunker
from src.game.headerbar import HeaderBar

# Helper function to slice sprites (unchanged)
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
        # Window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        # Assets
        self.background_image = pygame.image.load("assets/background/background.png").convert()
        self.background_height = self.background_image.get_height()
        self.font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 10)
        self.clock = pygame.time.Clock()
        self.state = self.STATE_MENU
        self.running = True
        self.SCROLL = SCROLL
        # Level management
        self.level = 1
        self.MAX_LEVEL = 5
        self.mini_boss_spawned = False
        self.level_cleared_timer = 0
        self.miniboss_group = pygame.sprite.Group()

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
            bullet.kill()

    def _reset(self):
        # Reset for a fresh game (menu start or full restart)
        self.score = 0
        self.lives = 3
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.bunkers = pygame.sprite.Group()
        self.ufo_group = pygame.sprite.Group()
        self.headerbar = pygame.sprite.GroupSingle()
        self.SCROLL = SCROLL  # reset scroll
        self.all_sprites.add(self.player)
        self.create_enemy_wave()
        self.enemy_direction = 1
        self.enemy_move_down = 10
        # Header bar
        self.headerbar.add(HeaderBar(self.screen, self.font))
        #self.headerbar.sprite.set_level(self.level)
        # Bunkers (satellites)
        angles = [0, 90, 180, 270]
        for i in range(4):
            x_pos = 140 + (i * 170)
            self.bunkers.add(Bunker(x_pos, SCREEN_HEIGHT - 120, angle=angles[i]))
        self.ufo_timer = int(UFO_SPAWN_TIME * FPS)
        self.player_shots = 0
        # Mini‑boss flags reset
        self.mini_boss_spawned = False
        self.miniboss_group.empty()
        self.level_cleared_timer = 0

    def create_enemy_wave(self):
        """Create normal enemy wave based on current level settings."""
        settings = ENEMY_WAVE_SETTINGS.get(self.level, ENEMY_WAVE_SETTINGS[1])
        rows = settings["rows"]
        cols = settings["cols"]
        x_margin, y_margin = 50, 60
        spacing_x, spacing_y = 80, 60
        for row in range(rows):
            for col in range(cols):
                x = x_margin + col * spacing_x
                y = y_margin + row * spacing_y
                enemy = Enemy(x, y, row)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
        # Store speed/shoot chance for possible future scaling
        self.enemy_speed = settings.get("speed", ENEMY_SPEED)
        self.enemy_shoot_chance = settings.get("shoot_chance", ENEMY_SHOOT_CHANCE)

    def _handle_enemy_movement(self):
        # Determine if any enemy hits screen edge
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
        hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, True, True)
        if hits:
            self.score += len(hits) * 100
        bonushits = pygame.sprite.groupcollide(self.ufo_group, self.player_bullets, True, True)
        if bonushits:
            self.score += random.choice(UFO_SCORE_OPTIONS)
        if pygame.sprite.spritecollide(self.player, self.enemy_bullets, True):
            self.lives -= 1
        # Mini‑boss collisions
        for boss in self.miniboss_group:
            hits = pygame.sprite.spritecollide(boss, self.player_bullets, True)
            for _ in hits:
                boss.hit()
        # Enemy reaching player
        for enemy in self.enemies:
            if enemy.rect.bottom >= self.player.rect.top:
                self.state = self.STATE_GAME_OVER

    def _draw_hud(self):
        score_surf = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        lives_surf = self.font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        self.screen.blit(score_surf, (10, 10))
        self.screen.blit(lives_surf, (SCREEN_WIDTH - lives_surf.get_width() - 10, 10))

    def _draw_menu(self):
        self.screen.fill((0, 0, 0))
        title = self.font.render("Space Invaders", True, (255, 255, 255))
        prompt = self.font.render("Press Enter to Start", True, (255, 255, 255))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()

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
        pygame.display.flip()

    def _spawn_ufo(self):
        ufo = UFO()
        self.ufo_group.add(ufo)
        self.all_sprites.add(ufo)

    def _spawn_miniboss(self):
        # Spawn the appropriate miniboss for the current level
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
        # Some bosses (e.g., BossSmall3, BossSmall4, BossFist) may need extra config – fetch if present
        extra = getattr(boss, "extra_settings", None)
        if isinstance(extra, dict):
            for k, v in extra.items():
                setattr(boss, k, v)
        # If the boss has a visual fist group, add those sprites **before** the boss itself
        # so they are rendered underneath the boss.
        if hasattr(boss, "fist_group"):
            self.all_sprites.add(boss.fist_group)
        self.miniboss_group.add(boss)
        self.all_sprites.add(boss)

    def advance_level(self):
        self.level += 1
        if self.level > self.MAX_LEVEL:
            self.state = self.STATE_VICTORY
            return
        # Update header bar
        self.headerbar.sprite.set_level(self.level)
        # Reset for next wave
        self.mini_boss_spawned = False
        self.miniboss_group.empty()
        self.enemies.empty()
        self.create_enemy_wave()
        self.ufo_timer = int(UFO_SPAWN_TIME * FPS)
        self.player_shots = 0
        self.level_cleared_timer = 0
        self.state = self.STATE_PLAYING

    def run(self):
        while True:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.state == self.STATE_MENU:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.state = self.STATE_PLAYING
                        self._reset()
                elif self.state == self.STATE_PLAYING:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        bullet = self.player.shoot()
                        if bullet:
                            self.player_bullets.add(bullet)
                            self.all_sprites.add(bullet)
                            self.player_shots += 1
                elif self.state in (self.STATE_GAME_OVER, self.STATE_VICTORY, self.STATE_LEVEL_CLEARED):
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self._reset()
                            self.state = self.STATE_PLAYING
                        elif event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
            # Update & render
            if self.state == self.STATE_MENU:
                self._draw_menu()
            elif self.state == self.STATE_PLAYING:
                keys = pygame.key.get_pressed()
                self.player.move(keys, SCREEN_WIDTH)
                self.player_bullets.update()
                self.enemy_bullets.update()
                self.bunkers.update()
                # Update minibosses so they move / animate
                self.miniboss_group.update(self.player, all_sprites=self.all_sprites, enemy_bullets=self.enemy_bullets, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
                for bullet in self.player_bullets:
                    self.handle_bunker_collision(bullet, self.bunkers)
                for bomb in self.enemy_bullets:
                    self.handle_bunker_collision(bomb, self.bunkers)
                # Enemy behavior
                self.enemies.update()
                self._handle_enemy_movement()
                self._enemy_shooting()
                # UFO handling
                self.ufo_group.update()
                self.ufo_timer -= 1
                if self.ufo_timer <= 0 or self.player_shots >= UFO_SHOT_THRESHOLD:
                    self._spawn_ufo()
                    self.ufo_timer = int(UFO_SPAWN_TIME * FPS)
                    self.player_shots = 0
                self._check_collisions()
                # Level progression
                if not self.enemies and not self.mini_boss_spawned:
                    self.state = self.STATE_LEVEL_CLEARED
                    self.level_cleared_timer = 5 * FPS
                elif self.mini_boss_spawned and not self.miniboss_group:
                    self.advance_level()
                # Rendering
                self.SCROLL = (self.SCROLL + BACKGROUND_SCROLL_SPEED) % self.background_height
                self.screen.blit(self.background_image, (0, self.SCROLL))
                self.screen.blit(self.background_image, (0, self.SCROLL - self.background_height))
                self.bunkers.draw(self.screen)
                self.all_sprites.draw(self.screen)
                self.player_bullets.draw(self.screen)
                self.enemy_bullets.draw(self.screen)
                self.headerbar.update(self.score, self.lives)
                self.headerbar.draw(self.screen)
                if self.lives == 1:
                    if (pygame.time.get_ticks() // 400) % 2 == 0:
                        for bar in self.headerbar:
                            warning_x = bar.rect.right + 15
                            warning_y = bar.rect.centery - (bar.warning_icon.get_height() // 2)
                            self.screen.blit(bar.warning_icon, (warning_x, warning_y))
                pygame.display.flip()
            elif self.state == self.STATE_LEVEL_CLEARED:
                # Show cooldown overlay
                self._draw_hud()
                overlay = self.font.render("Level cleared! New wave approaching", True, (255, 255, 0))
                self.screen.blit(overlay, (SCREEN_WIDTH // 2 - overlay.get_width() // 2, SCREEN_HEIGHT // 2))
                pygame.display.flip()
                self.level_cleared_timer -= 1
                if self.level_cleared_timer <= 0:
                    self._spawn_miniboss()
                    self.mini_boss_spawned = True
                    self.state = self.STATE_PLAYING
            else:
                self._draw_end_screen()

    @property
    def Player(self):
        """Compatibility alias for the player sprite (use .player)."""
        return self.player
