import pygame, sys, traceback
sys.path.append('src')
from src.game.game import Game
from src.game.fist import Fist
from src.game.bunker import Bunker

pygame.init()
pygame.display.set_mode((800,600))

try:
    game = Game()
    game._reset()  # initialize sprite groups and bunkers
    print('Bunkers after reset:', len(game.bunkers))
    # create a single bunker
    game.bunkers.empty()
    bunker = Bunker(400, 560)
    game.bunkers.add(bunker)
    # create a fist overlapping bunker
    fake_rect = pygame.Rect(0,0,0,0)
    fist = Fist('left', fake_rect, None, speed=0)
    fist.rect.center = bunker.rect.center
    game.enemy_bullets.add(fist)
    print('enemy_bullets contains:', [type(s).__name__ for s in game.enemy_bullets])
    # call collision handling
    game.handle_bunker_collision(fist, game.bunkers)
    print('Explosions after collision:', len(game.explosions))
except Exception as e:
    print('Exception:')
    traceback.print_exc()
