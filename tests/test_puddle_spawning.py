import os
import pygame

# Ensure pygame works in headless CI environments
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from src.game.game import Game
from src.game.boss_small_3 import BossSmall3

def test_poison_puddle_spawns():
    # Initialise a fresh game instance
    g = Game()
    g._reset()
    # Force level where miniboss 3 appears
    g.level = 3
    # Create the boss and add it to the miniboss group
    boss = BossSmall3()
    g.miniboss_group.add(boss)
    g.all_sprites.add(boss)

    # Run the update loop for a reasonable number of frames
    for _ in range(500):
        # Use the new positional signature for miniboss updates
        g.miniboss_group.update(
            g.player,
            g.all_sprites,
            g.enemy_bullets,
            g.explosions,
            g.SCREEN_WIDTH if hasattr(g, "SCREEN_WIDTH") else 800,
            g.SCREEN_HEIGHT if hasattr(g, "SCREEN_HEIGHT") else 600,
            g.puddle_group,
        )
        # Update puddles (they have their own timer)
        g.puddle_group.update()

    assert len(g.puddle_group) > 0, "No poison puddles were spawned after many frames"
