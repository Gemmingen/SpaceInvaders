import pygame
from src.game.game import Game

# Initialize pygame (required for font etc.)
pygame.init()

game = Game()
# Simulate start
game.state = game.STATE_PLAYING
game._reset()
# Manually clear enemies to trigger level cleared state
game.enemies.empty()
# Run a single iteration of run loop logic manually (call part of run)
# We'll invoke the logic that checks for level progression
if not game.enemies and not game.mini_boss_spawned:
    game.state = game.STATE_LEVEL_CLEARED
    game.level_cleared_timer = 5 * 60
print('State after clearing enemies:', game.state, 'Timer:', game.level_cleared_timer)
# Simulate timer passing
while game.state == game.STATE_LEVEL_CLEARED:
    game.level_cleared_timer -= 1
    if game.level_cleared_timer <= 0:
        game._spawn_miniboss()
        game.mini_boss_spawned = True
        game.state = game.STATE_PLAYING
print('State after cooldown and miniboss spawn:', game.state, 'MiniBoss spawned?', len(game.miniboss_group))
# Simulate miniboss defeat
for boss in list(game.miniboss_group):
    boss.hit()
    boss.hit()
    boss.hit()  # health 3, should die
print('Miniboss group after hits:', len(game.miniboss_group))
# Advance level logic
if game.mini_boss_spawned and not game.miniboss_group:
    game.advance_level()
print('Level after advancing:', game.level, 'State:', game.state)
