import pygame, sys, traceback
sys.path.append('src')
from src.game.game import Game

pygame.init()
pygame.display.set_mode((800,600))

try:
    game = Game()
    print('Game initialized, attributes present:')
    print('has bunkers?', hasattr(game, 'bunkers'))
except Exception as e:
    print('Exception during Game init:')
    traceback.print_exc()
