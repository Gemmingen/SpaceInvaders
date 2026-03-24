"""
Tests für die Bunker (Satelliten), die den Spieler vor Schüssen schützen.
"""
import pytest
import pygame
from src.game.bunker import Bunker

def test_bunker_initialization():
    """Prüft, ob der Bunker mit den korrekten Basiswerten spawnt und im Spiel existiert."""
    # Arrange (Vorbereiten)
    bunker = Bunker(x=100, y=100, variant="satellite")
    test_group = pygame.sprite.Group()
    
    # Act (Ausführen)
    test_group.add(bunker)
    
    # Assert (Prüfen)
    assert bunker.health == 15, "Der Bunker sollte mit 15 Lebenspunkten starten."
    assert bunker.alive() is True, "Der Bunker muss nach dem Erstellen als 'lebendig' gelten (in einer Gruppe sein)."

def test_bunker_takes_damage():
    """Prüft, ob die Funktion take_damage() exakt 1 Lebenspunkt abzieht."""
    # Arrange
    bunker = Bunker(x=100, y=100, variant="satellite")
    initial_health = bunker.health
    
    # Act
    bunker.take_damage()
    
    # Assert
    assert bunker.health == initial_health - 1, "Die HP des Bunkers sollten um 1 gesunken sein."

def test_bunker_dies_at_zero_health():
    """Prüft, ob sich der Bunker bei 0 HP selbst zerstört (aus allen Sprite-Gruppen entfernt)."""
    # Arrange
    bunker = Bunker(x=100, y=100, variant="satellite")
    test_group = pygame.sprite.Group()
    test_group.add(bunker)
    
    # Act: Leben manuell auf 1 setzen und dann den tödlichen Treffer simulieren
    bunker.health = 1 
    bunker.take_damage() 
    
    # Assert
    assert bunker.health == 0, "Die HP sollten auf 0 gesunken sein."
    assert bunker.alive() is False, "Der Bunker sollte sich durch .kill() aus der test_group entfernt haben."