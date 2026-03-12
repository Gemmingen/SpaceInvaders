import os, pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
pygame.display.set_mode((1, 1))

from src.game.game import Game
from src.game.laser_line import LaserLine
from src.game.bunker import Bunker
from src.game.boss_small_2 import BossSmall2

game = Game()
# Initialize game (sets up groups, player, bunkers, etc.)
game._reset()
# create a bunker at known position (override one for test)
bunker = Bunker(100, 100)
game.bunkers.add(bunker)

# ---- Test player hit by LaserLine ----
# Create a miniboss and attach to game
boss = BossSmall2()
# Set references used by boss
boss._player = game.player
boss._all_sprites = game.all_sprites
boss._enemy_bullets = game.enemy_bullets
boss._explosions = game.explosions
# Add boss to miniboss group
game.miniboss_group.add(boss)
# Spawn a laser that will intersect the player
# Position player at center (default) and spawn laser overlapping
player_x = game.player.rect.centerx
# Use orb positions to ensure laser passes through player
# For simplicity, directly create LaserLine centered on player
laser = LaserLine(y_pos=game.player.rect.centery, left_center_x=player_x-100, right_center_x=player_x+100, player_x=player_x)
# Add laser to boss's laser_lines and to groups
boss.laser_lines.add(laser)
game.all_sprites.add(laser)
game.enemy_bullets.add(laser)
# Record lives before collision
print('Player lives before laser:', game.lives)
# Run collision check
game._check_collisions()
print('Player lives after laser:', game.lives)
print('Laser still alive?', laser.alive())
# create laser that will intersect bunker horizontally
laser = LaserLine(y_pos=100, left_center_x=50, right_center_x=200, player_x=150)
print('Before collision: bunkers', len(game.bunkers), 'explosions', len(game.explosions))
# Debug: show laser hitboxes and bunker rect
hitboxes = laser.get_hitboxes()
print('Laser hitboxes count:', len(hitboxes))
for i, hb in enumerate(hitboxes[:5]):
    print('Hitbox', i, hb)
print('Bunker rect:', bunker.rect)
# Check collision manually
collision = any(hb.colliderect(bunker.rect) for hb in hitboxes)
print('Manual collision detection:', collision)

game.handle_bunker_collision(laser, game.bunkers)
print('After collision: bunkers', len(game.bunkers), 'explosions', len(game.explosions))
