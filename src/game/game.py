import pygame
import random
import sys
from src.config.config import (SCREEN_WIDTH, SCREEN_HEIGHT, FPS, PLAYER_SPEED, 
                               ENEMY_SPEED, BULLET_SPEED, UFO_SPAWN_TIME, 
                               UFO_SPEED, UFO_SCORE_OPTIONS, UFO_SHOT_THRESHOLD, 
                               BACKGROUND_SCROLL_SPEED, SCROLL)
from src.game.player import Player
from src.game.enemy import Enemy
from src.game.ufo import UFO
from src.game.bullet import Bullet
from src.game.bunker import Bunker

# Hilfsfunktion zum Ausschneiden von Sprites
def get_image(sheet, x, y, width, height):
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    image.blit(sheet, (0, 0), (x, y, width, height))
    return image.convert_alpha() # Optimiert für die Grafikkarte

class Game:
    STATE_MENU = "menu"
    STATE_PLAYING = "playing"
    STATE_GAME_OVER = "game_over"
    STATE_VICTORY = "victory"

    def __init__(self):
        pygame.init()
        # 1. Zuerst das Fenster erstellen (Video Mode setzen)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        
        # 2. Assets EINMALIG laden
        self.background_image = pygame.image.load("assets/background/background.png").convert()
        self.background_height = self.background_image.get_height()
        

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        
        self.state = self.STATE_MENU
        self.running = True
        self.SCROLL = SCROLL # Initialer Scroll-Wert
        self._reset()

    def handle_bunker_collision(self, bullet, bunker_group):
        hit_bunker = pygame.sprite.spritecollideany(bullet, bunker_group)
        if hit_bunker:
            offset = (bullet.rect.x - hit_bunker.rect.x, bullet.rect.y - hit_bunker.rect.y)
            overlap_pos = hit_bunker.mask.overlap(bullet.mask, offset)
            if overlap_pos:
                erase_x, erase_y = overlap_pos[0] - 3, overlap_pos[1] - 3
                brush = pygame.mask.Mask((6, 8), fill=True)
                hit_bunker.mask.erase(brush, (erase_x, erase_y))

                for x in range(6):
                    for y in range(8):
                        px, py = erase_x + x, erase_y + y
                        if 0 <= px < hit_bunker.image.get_width() and \
                           0 <= py < hit_bunker.image.get_height():
                            hit_bunker.image.set_at((px, py), (0, 0, 0, 0))
                bullet.kill()

    def _reset(self):
        self.score = 0
        self.lives = 3
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.bunkers = pygame.sprite.Group()
        self.ufo_group = pygame.sprite.Group()
        
        self.all_sprites.add(self.player)
        self._create_enemies()
        
        self.enemy_direction = 1
        self.enemy_move_down = 10
        self.ufo_timer = int(UFO_SPAWN_TIME * FPS)
        self.player_shots = 0
        
        for i in range(4):
            x_pos = 100 + (i * 180)
            self.bunkers.add(Bunker(x_pos, SCREEN_HEIGHT - 120))

    def _create_enemies(self):
        rows, cols = 5, 5
        x_margin, y_margin = 50, 60
        spacing_x, spacing_y = 80, 60
        for row in range(rows):
            for col in range(cols):
                enemy = Enemy(x_margin + col * spacing_x, y_margin + row * spacing_y)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

    def _handle_enemy_movement(self):
        move_down = False
        for enemy in self.enemies:
            if (self.enemy_direction == 1 and enemy.rect.right >= SCREEN_WIDTH - 10) or \
               (self.enemy_direction == -1 and enemy.rect.left <= 10):
                move_down = True
                break
        
        if move_down:
            for enemy in self.enemies:
                enemy.rect.y += self.enemy_move_down
            self.enemy_direction *= -1
        else:
            for enemy in self.enemies:
                enemy.move(self.enemy_direction)

    def _enemy_shooting(self):
        for enemy in self.enemies:
            if random.random() < 0.001:
                bullet = enemy.shoot()
                self.enemy_bullets.add(bullet)
                self.all_sprites.add(bullet)

    def _check_collisions(self):
        hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, True, True)  
        if hits: self.score += len(hits) * 100

        bonushits = pygame.sprite.groupcollide(self.ufo_group, self.player_bullets, True, True)
        if bonushits:
            self.score += random.choice(UFO_SCORE_OPTIONS)
        
        if pygame.sprite.spritecollide(self.player, self.enemy_bullets, True):
            self.lives -= 1

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
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//3))
        self.screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT//2))
        pygame.display.flip()

    def _draw_end_screen(self):
        self.screen.fill((0, 0, 0))
        msg = "Game Over" if self.state == self.STATE_GAME_OVER else "You Win!"
        color = (255, 0, 0) if self.state == self.STATE_GAME_OVER else (0, 255, 0)
        
        msg_surf = self.font.render(msg, True, color)
        score_surf = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        instr_surf = self.font.render("Press R to Restart or Q to Quit", True, (255, 255, 255))
        
        self.screen.blit(msg_surf, (SCREEN_WIDTH//2 - msg_surf.get_width()//2, SCREEN_HEIGHT//3))
        self.screen.blit(score_surf, (SCREEN_WIDTH//2 - score_surf.get_width()//2, SCREEN_HEIGHT//3 + 40))
        self.screen.blit(instr_surf, (SCREEN_WIDTH//2 - instr_surf.get_width()//2, SCREEN_HEIGHT//2))
        pygame.display.flip()

    def _spawn_ufo(self):
        ufo = UFO()
        self.ufo_group.add(ufo)
        self.all_sprites.add(ufo)

    def run(self):
        while True:
            self.clock.tick(FPS)
            
            # 1. Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if self.state == self.STATE_MENU:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.state = self.STATE_PLAYING
                elif self.state == self.STATE_PLAYING:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        bullet = self.player.shoot()
                        if bullet:
                            self.player_bullets.add(bullet)
                            self.all_sprites.add(bullet)
                            self.player_shots += 1
                elif self.state in (self.STATE_GAME_OVER, self.STATE_VICTORY):
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self._reset()
                            self.state = self.STATE_PLAYING
                        elif event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()

            # 2. Updates & Rendering
            if self.state == self.STATE_MENU:
                self._draw_menu()
            elif self.state == self.STATE_PLAYING:
                # --- UPDATE LOGIK ---
                keys = pygame.key.get_pressed()
                self.player.move(keys, SCREEN_WIDTH)
                self.player_bullets.update()
                self.enemy_bullets.update()
                self.ufo_group.update()
                self._handle_enemy_movement()
                self._enemy_shooting()
                
                self.ufo_timer -= 1
                if self.ufo_timer <= 0 or self.player_shots >= UFO_SHOT_THRESHOLD:
                    self._spawn_ufo()
                    self.ufo_timer = int(UFO_SPAWN_TIME * FPS)
                    self.player_shots = 0

                self._check_collisions()
                
                # Bullet vs Bunker
                for b in self.player_bullets: self.handle_bunker_collision(b, self.bunkers)
                for b in self.enemy_bullets: self.handle_bunker_collision(b, self.bunkers)

                # Sieg/Niederlage Check
                if not self.enemies: self.state = self.STATE_VICTORY
                if self.lives <= 0: self.state = self.STATE_GAME_OVER

                # --- RENDERING (REIHENFOLGE WICHTIG!) ---
                # A. Hintergrund zuerst (Scrolling)
                self.SCROLL = (self.SCROLL + BACKGROUND_SCROLL_SPEED) % self.background_height
                self.screen.blit(self.background_image, (0, self.SCROLL))
                self.screen.blit(self.background_image, (0, self.SCROLL - self.background_height))

                # B. Dann die Objekte
                self.bunkers.draw(self.screen)
                self.all_sprites.draw(self.screen)
                self.player_bullets.draw(self.screen)
                self.enemy_bullets.draw(self.screen)

                # C. HUD zum Schluss
                self._draw_hud()
                pygame.display.flip()
            else:
                self._draw_end_screen()
