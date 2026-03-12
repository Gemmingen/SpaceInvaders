import pygame
from src.game.game import Game
from src.game.boss_small_2 import BossSmall2
from src.game.laser_line import LaserLine

pygame.init()
pygame.display.set_mode((1,1))

game = Game()
# Initialise groups and bunkers
game._reset()
print('Initial bunkers:', len(game.bunkers))

boss = BossSmall2()
# set references for boss
boss._player = game.player
boss._all_sprites = game.all_sprites
boss._enemy_bullets = game.enemy_bullets
boss._explosions = game.explosions

game.miniboss_group.add(boss)

boss.start_attack()

laser_found = False
for frame in range(600):
    boss.update(player=game.player, all_sprites=game.all_sprites, enemy_bullets=game.enemy_bullets, explosions=game.explosions)
    # Check enemy bullets for LaserLine
    for bullet in list(game.enemy_bullets):
        if isinstance(bullet, LaserLine):
            laser_found = True
            # print once when first found
            print('LaserLine present at frame', frame)
            # handle bunker collision
            game.handle_bunker_collision(bullet, game.bunkers)
    if laser_found and len(game.bunkers) == 0:
        break
print('Bunkers after laser:', len(game.bunkers))
