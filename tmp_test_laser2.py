import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.display.init()
from src.game.game import Game
from src.game.laser_line import LaserLine
from src.game.bunker import Bunker
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT, BOSS2_ORB_Y_PERCENT

def _create_game():
    game = Game()
    game._reset()
    return game

game = _create_game()
laser_y = int(SCREEN_HEIGHT * BOSS2_ORB_Y_PERCENT)
bunker = Bunker(250, laser_y, variant="satellite", angle=0)
game.bunkers.add(bunker)
laser = LaserLine(laser_y, left_center_x=0, right_center_x=SCREEN_WIDTH, player_x=0, orb_half_width=0)
# Run collision handling
game.handle_bunker_collision(laser, game.bunkers)
print('bunkers left', len(game.bunkers))
print('laser alive', laser.alive())
