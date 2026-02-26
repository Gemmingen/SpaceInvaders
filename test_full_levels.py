import pygame
from src.game.game import Game

pygame.init()

game = Game()
game.state = game.STATE_PLAYING
game._reset()

for target in range(1, 6):
    # clear enemies
    game.enemies.empty()
    # trigger level cleared -> cooldown
    if not game.enemies and not game.mini_boss_spawned:
        game.state = game.STATE_LEVEL_CLEARED
        game.level_cleared_timer = 5 * 60
    # fast forward timer
    while game.state == game.STATE_LEVEL_CLEARED:
        game.level_cleared_timer -= 1
        if game.level_cleared_timer <= 0:
            game._spawn_miniboss()
            game.mini_boss_spawned = True
            game.state = game.STATE_PLAYING
    # defeat miniboss
    for boss in list(game.miniboss_group):
        while boss.health > 0:
            boss.hit()
    # advance level if appropriate
    if game.mini_boss_spawned and not game.miniboss_group:
        game.advance_level()
    print(f"After level {target}, game.level={game.level}, state={game.state}")

print('Final state:', game.state, 'Level:', game.level)
