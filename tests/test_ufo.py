"""
Tests für das UFO (Bonus-Schiff).
Überprüft das korrekte Spawnen (Zufallsrichtung), die Bewegung und das Despawnen.
"""
import pytest
import pygame
from src.game.ufo import UFO
from src.config.config import SCREEN_WIDTH

def test_ufo_initialization_and_direction():
    """
    Prüft, ob das UFO basierend auf seiner Zufallsrichtung (links/rechts) 
    korrekt *außerhalb* des Bildschirms gespawnt wird.
    """
    # Arrange & Act
    ufo = UFO()
    
    # Assert
    # Wenn direction 1 ist (fliegt nach rechts), MUSS es links vom Bildschirm starten
    if ufo.direction == 1:
        assert ufo.rect.left < 0, "UFO (fliegt rechts) muss links außerhalb des Bildschirms starten."
    # Wenn direction -1 ist (fliegt nach links), MUSS es rechts vom Bildschirm starten
    else:
        assert ufo.rect.right > SCREEN_WIDTH, "UFO (fliegt links) muss rechts außerhalb des Bildschirms starten."

def test_ufo_movement():
    """Prüft, ob sich das UFO pro Frame exakt um seine Geschwindigkeit in die richtige Richtung bewegt."""
    # Arrange
    ufo = UFO()
    initial_x = ufo.rect.x
    
    # Act
    ufo.update()
    
    # Assert
    expected_x = initial_x + (ufo.speed * ufo.direction)
    assert ufo.rect.x == expected_x, "Das UFO hat sich nicht um (Speed * Direction) bewegt."

def test_ufo_dies_when_offscreen():
    """Prüft, ob sich das UFO selbst zerstört (kill), wenn es den Bildschirm auf der anderen Seite verlässt."""
    # Arrange
    ufo = UFO()
    test_group = pygame.sprite.Group()
    test_group.add(ufo)
    
    # Wir teleportieren das UFO manuell gaaaaanz weit aus dem Bildschirm heraus
    # in die Richtung, in die es ohnehin fliegt.
    if ufo.direction == 1:
        ufo.rect.left = SCREEN_WIDTH + 1000
    else:
        ufo.rect.right = -1000
        
    # Act
    ufo.update()
    
    # Assert
    assert ufo.alive() is False, "Das UFO muss despawnen (sich killen), wenn es den Bildschirm verlässt."