"""
Tests für sammelbare Items und Powerups (Bewegungslogik).
"""
import pytest
from src.game.powerup import PowerUp
from src.game.bonus_points import BonusPointItem

def test_powerup_falls_down():
    """Prüft, ob sich ein normales Powerup pro Frame exakt um seine 'speed' nach unten (Y-Achse) bewegt."""
    # Arrange
    powerup = PowerUp(x=200, y=100, speed=5, powerup_type="hp")
    
    # Act
    powerup.update(screen_height=1000)
    
    # Assert
    # Startwert war 100 (centery). Nach einem Frame mit Speed 5 muss er bei 105 sein.
    assert powerup.rect.centery == 105, "Das PowerUp ist nicht korrekt nach unten gefallen."

def test_bonus_item_falls_down():
    """Prüft, ob sich das Punkte-Item (BonusPointItem) basierend auf Fließkommazahlen (exact_y) korrekt nach unten bewegt."""
    # Arrange
    item = BonusPointItem(x=200, y=100, speed=3, points=100)
    initial_y = item.exact_y
    
    # Act
    item.update()
    
    # Assert
    assert item.exact_y == initial_y + 3, "Die genaue Y-Position (Float) muss um den Speed-Wert gewachsen sein."
    assert item.rect.y == int(initial_y + 3), "Die Integer-Rect-Position muss sich entsprechend angepasst haben."