import pygame
import random
import sys
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, PLAYER_SPEED, ENEMY_SPEED, BULLET_SPEED
from src.game.player import Player
from src.game.enemy import Enemy
from src.game.bullet import Bullet

class Game:
    # Possible game states
    STATE_MENU = "menu"
    STATE_PLAYING = "playing"
    STATE_GAME_OVER = "game_over"
    STATE_VICTORY = "victory"
    def __init__(self):
        # Initialize pygame components
        self.state = self.STATE_MENU
        self._reset()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self._reset()
        self.running = True

    def _reset(self):
        """Reset game state for a new round"""
        self.score = 0
        self.lives = 3
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player_bullets = self.player.bullets
        self.enemy_bullets = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self._create_enemies()
        self.enemy_direction = 1
        self.enemy_move_down = 10

    def _create_enemies(self):
        rows = 3
        cols = 7
        x_margin = 60
        y_margin = 60
        spacing_x = 80
        spacing_y = 60
        for row in range(rows):
            for col in range(cols):
                x = x_margin + col * spacing_x
                y = y_margin + row * spacing_y
                enemy = Enemy(x, y)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

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
            # Move down and reverse direction
            for enemy in self.enemies:
                enemy.rect.y += self.enemy_move_down
            self.enemy_direction *= -1
        else:
            # Move horizontally
            for enemy in self.enemies:
                enemy.move(self.enemy_direction)

    def _enemy_shooting(self):
        # Each enemy has a small chance to fire each frame
        for enemy in self.enemies:
            if random.random() < 0.002:  # adjust probability as needed
                bullet = enemy.shoot()
                self.enemy_bullets.add(bullet)
                self.all_sprites.add(bullet)

    def _check_collisions(self):
        # Player bullets hitting enemies
        hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, True, True)
        if hits:
            self.score += len(hits) * 100
        # Enemy bullets hitting player
        hits_player = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        if hits_player:
            self.lives -= 1
            if self.lives <= 0:
                self.running = False
        # Enemies reaching player area
        for enemy in self.enemies:
            if enemy.rect.bottom >= self.player.rect.top:
                self.running = False
                break

    def _draw_hud(self):
        score_surf = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        lives_surf = self.font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        self.screen.blit(score_surf, (10, 10))
        self.screen.blit(lives_surf, (SCREEN_WIDTH - lives_surf.get_width() - 10, 10))

    def _draw_menu(self):
        self.screen.fill((0, 0, 0))
        title_surf = self.font.render("Space Invaders", True, (255, 255, 255))
        prompt_surf = self.font.render("Press Enter to Start", True, (255, 255, 255))
        self.screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(prompt_surf, (SCREEN_WIDTH // 2 - prompt_surf.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()

    def _draw_end_screen(self):
        self.screen.fill((0, 0, 0))
        if self.state == self.STATE_GAME_OVER:
            msg = "Game Over"
            color = (255, 0, 0)
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

    def run(self):
        while True:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # State-specific event handling
                if self.state == self.STATE_MENU:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.state = self.STATE_PLAYING
                elif self.state == self.STATE_PLAYING:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.player.shoot()
                elif self.state in (self.STATE_GAME_OVER, self.STATE_VICTORY):
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self._reset()
                            self.state = self.STATE_PLAYING
                        elif event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()

            # State-specific updates and rendering
            if self.state == self.STATE_MENU:
                self._draw_menu()
                continue

            if self.state == self.STATE_PLAYING:
                keys = pygame.key.get_pressed()
                self.player.move(keys, SCREEN_WIDTH)

                # Update bullets
                self.player_bullets.update()
                self.enemy_bullets.update()

                # Enemy behavior
                self._handle_enemy_movement()
                self._enemy_shooting()

                # Collisions
                self._check_collisions()

                # Check win/lose conditions
                if not self.enemies:
                    self.state = self.STATE_VICTORY
                if self.lives <= 0:
                    self.state = self.STATE_GAME_OVER

                # Rendering
                self.screen.fill((0, 0, 0))
                self.all_sprites.add(self.player_bullets)
                self.all_sprites.draw(self.screen)
                self._draw_hud()
                pygame.display.flip()
                continue

            # Game over or victory screens
            self._draw_end_screen()


    def _game_over(self):
        self.screen.fill((0, 0, 0))
        game_over_surf = self.font.render("Game Over", True, (255, 0, 0))
        final_score_surf = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(game_over_surf, (SCREEN_WIDTH // 2 - game_over_surf.get_width() // 2,
                                         SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(final_score_surf, (SCREEN_WIDTH // 2 - final_score_surf.get_width() // 2,
                                            SCREEN_HEIGHT // 2 + 10))
        pygame.display.flip()
        # Wait for a short period before exiting
        pygame.time.wait(3000)