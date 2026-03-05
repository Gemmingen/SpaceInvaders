import pygame
from src.game.game import Game

def test_backgrounds_loaded():
    # Initialise pygame (required for image loading)
    pygame.init()
    game = Game()
    # Expect 5 levels (MAX_LEVEL is 5)
    assert len(game.level_backgrounds) == 5
    for level, layers in game.level_backgrounds.items():
        assert len(layers) == 4  # 4 layers per level
    assert len(game.transition_background) == 4
    # Ensure current background matches level 1 at start
    assert game.current_background_layers == game.level_backgrounds[1]
