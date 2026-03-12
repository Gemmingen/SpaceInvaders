import os
import pygame

# Use dummy video driver for headless testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.display.init()

from src.game.game import Game
from src.game.laser_line import LaserLine
from src.game.bunker import Bunker
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT, BOSS2_ORB_Y_PERCENT


def _create_game():
    game = Game()
    # Initialise all groups and default state
    game._reset()
    return game


def test_laserline_destroys_all_bunkers():
    game = _create_game()
    # Place a bunker at the laser height
    laser_y = int(SCREEN_HEIGHT * BOSS2_ORB_Y_PERCENT)
    bunker = Bunker(250, laser_y, variant="satellite", angle=0)
    game.bunkers.add(bunker)
    # Create a LaserLine that spans the whole width and thus overlaps the bunker
    laser = LaserLine(
        laser_y,
        left_center_x=0,
        right_center_x=SCREEN_WIDTH,
        player_x=0,
        orb_half_width=0,
    )
    # Run the special bunker‑collision logic
    game.handle_bunker_collision(laser, game.bunkers)
    # All bunkers should be removed and the laser killed
    assert len(game.bunkers) == 0
    assert not laser.alive()


def test_laserline_hits_player_and_reduces_life():
    game = _create_game()
    initial_lives = game.lives
    # Position laser at player's vertical position to guarantee overlap
    laser_y = game.player.rect.centery
    laser = LaserLine(
        laser_y,
        left_center_x=0,
        right_center_x=SCREEN_WIDTH,
        player_x=0,
        orb_half_width=0,
    )
    # Add the laser to the enemy bullet group so _check_collisions sees it
    game.enemy_bullets.add(laser)
    # Run collision detection – should register a hit on the player
    game._check_collisions()
    assert game.lives == initial_lives - 1
    # Laser should be removed after hitting the player
    assert not laser.alive()
