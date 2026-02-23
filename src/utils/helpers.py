import pygame

# Wir speichern das Spritesheet hier, damit es nicht für jeden Gegner neu geladen wird
_spritesheet = None

def get_spritesheet():
    global _spritesheet
    if _spritesheet is None:
        _spritesheet = pygame.image.load("assets/pico8_invaders_sprites_LARGE.png").convert_alpha()
    return _spritesheet

# Die neue Funktion, die deine Klassen aufrufen werden
def get_sprite(x, y, width, height, scale_to=None):
    sheet = get_spritesheet()
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    image.blit(sheet, (0, 0), (x, y, width, height))
    
    if scale_to:
        image = pygame.transform.scale(image, scale_to)
        
    return image

def load_image(path):
    return pygame.image.load(path)

def load_sound(path):
    return pygame.mixer.Sound(path)