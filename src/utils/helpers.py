import pygame

def load_image(path):
    return pygame.image.load(path)

def load_sound(path):
    return pygame.mixer.Sound(path)