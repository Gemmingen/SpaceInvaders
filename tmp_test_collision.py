import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
pygame.init()
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from src.game.game import Game
from src.game.boss_small_2 import BossSmall2
from src.game.player import Player

# Setup game and reset groups
game = Game()
game._reset()
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)

boss = BossSmall2()
# Add boss to miniboss group so its laser hitboxes are considered
game.miniboss_group.add(boss)
# Also add its sprite to all_sprites for consistency
game.all_sprites.add(boss)

boss.start_attack()
# Fast‑forward through flash, orb spawn, charge to reach barrage
for _ in range(200):
    boss.update(player=player, all_sprites=game.all_sprites, enemy_bullets=game.enemy_bullets, explosions=game.explosions)

print('State after init:', boss.attack_substate, 'laser count', boss.laser_count)

if boss.laser_lines:
    laser = next(iter(boss.laser_lines))
    # Position player roughly in the middle of the left segment
    target_x = (laser.left_orb_x + laser.left_end) // 2
    player.rect.centerx = target_x
    # Run collision detection
    game._check_collisions()
    print('Player lives after collision (should be less than 3):', game.lives)
else:
    print('No laser lines created')
