import pygame, sys, os
sys.path.append('src')
from src.game.game import Game
from src.game.fist import Fist
from src.game.bunker import Bunker

pygame.init()
pygame.display.set_mode((800,600))

game = Game()
# clear any existing bunkers and add a single one
game.bunkers.empty()
bunker = Bunker(400, 560)
game.bunkers.add(bunker)

# create a fist directly overlapping bunker
fake_rect = pygame.Rect(0,0,0,0)
fist = Fist('left', fake_rect, None, speed=0)
fist.rect.center = bunker.rect.center
# add to enemy_bullets group
game.enemy_bullets.add(fist)

print('enemy_bullets contains:', [type(s).__name__ for s in game.enemy_bullets])
print('bunkers contains:', [type(b).__name__ for b in game.bunkers])

# invoke collision handling
game.handle_bunker_collision(fist, game.bunkers)
print('Explosions after collision:', len(game.explosions))
