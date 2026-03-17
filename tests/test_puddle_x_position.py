import os
import pygame

# Ensure headless mode for CI
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from src.game.boss_small_3 import PoisonGlob, PUDDLE_OFFSET
from src.game.player import Player
from src.config.config import SCREEN_HEIGHT
from src.game.boss_small_3 import GLOB_SPEED

def test_puddle_spawns_at_player_y_and_glob_x():
    # Create sprite groups
    puddle_group = pygame.sprite.Group()

    # Player positioned near the bottom with a distinct X coordinate
    player = Player(x=200, y=SCREEN_HEIGHT - 30)  # midbottom at (200, SCREEN_HEIGHT-30)

    # Store the X coordinate we expect the puddle to keep
    expected_x = 400

    # Create a PoisonGlob far above the player with a different X coordinate
    glob = PoisonGlob(
        x=expected_x,
        y=0,
        speed=GLOB_SPEED,
        puddle_group=puddle_group,
        player=player,
    )

    # Add the glob to a temporary sprite group so that .alive() works correctly
    temp_group = pygame.sprite.Group()
    temp_group.add(glob)
    # Run updates until the glob kills itself (reaches the floor)
    while glob.alive():
        glob.update()

    # At this point the glob should be dead and a puddle spawned
    assert len(puddle_group) == 1, "Puddle was not spawned"
    puddle = next(iter(puddle_group))

    # X should match the original projectile X (centerx of the puddle)
    assert puddle.rect.centerx == expected_x, "Puddle X does not match projectile X"

    # Y should be based on the player's foot level plus the offset
    expected_y = min(player.rect.bottom + PUDDLE_OFFSET, SCREEN_HEIGHT - 20)
    # The puddle's rect is positioned using its midtop, so its bottom should be
    # expected_y + puddle.rect.height (but we only need to verify the top aligns)
    assert puddle.rect.top == expected_y, "Puddle Y does not match player foot level"
