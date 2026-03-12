import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
pygame.init()
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.game.boss_small_2 import BossSmall2
from src.game.game import Game
from src.game.player import Player

# Initialize game and reset to set up sprite groups
game = Game()
game._reset()
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)

boss = BossSmall2()
boss.start_attack()

# Simulate updates for several frames
for i in range(300):
    boss.update(player=player, all_sprites=game.all_sprites, enemy_bullets=game.enemy_bullets, explosions=game.explosions)
    if i % 30 == 0:
        print(i, boss.attack_substate, boss.laser_count)
