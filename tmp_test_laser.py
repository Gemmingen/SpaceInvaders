import pygame
from src.game.game import Game
from src.game.boss_small_2 import BossSmall2

pygame.init()
pygame.display.set_mode((1,1))

game = Game()
# Initialize game state to have bunkers
game._reset()
print('Initial bunkers:', len(game.bunkers))

boss = BossSmall2()
game.miniboss_group.add(boss)
# Set references used by boss (player, groups) because updates rely on them
boss._player = game.player
boss._all_sprites = game.all_sprites
boss._enemy_bullets = game.enemy_bullets
boss._explosions = game.explosions

boss.start_attack()
# Run enough frames to reach laser firing (move, flash, orb spawn, laser charge)
for _ in range(400):
    boss.update(player=game.player, all_sprites=game.all_sprites, enemy_bullets=game.enemy_bullets, explosions=game.explosions)
    # Process bunker collisions for any enemy bullets (including lasers)
    for bullet in list(game.enemy_bullets):
        game.handle_bunker_collision(bullet, game.bunkers)
    if len(game.bunkers) == 0:
        break
print('Bunkers after laser:', len(game.bunkers))
