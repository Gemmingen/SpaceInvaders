"""
Tests für die Spieler-Klasse (Player), insbesondere für die Timer von Effekten und Buffs.
"""
import pytest
from src.game.player import Player

def test_player_initialization():
    """Prüft, ob der Spieler an der richtigen Koordinate mit der Standardwaffe gespawnt wird."""
    # Act
    player = Player(x=400, y=500, player_id=1)
    
    # Assert
    assert player.rect.centerx == 400, "Der Spieler sollte auf der X-Koordinate 400 starten."
    assert player.player_id == 1, "Dem Spieler sollte die ID 1 zugewiesen worden sein."
    assert player.weapon_type == "single", "Die Startwaffe sollte 'single' sein."
    assert player.speed == player.base_speed, "Die Startgeschwindigkeit sollte der Basis-Geschwindigkeit entsprechen."

def test_player_weapon_buff_expires():
    """Simuliert das Aufsammeln eines Doubleshots und prüft, ob er nach Ablauf der Zeit wieder verschwindet."""
    # Arrange
    player = Player(x=400, y=500, player_id=1)
    player.weapon_type = "double"
    player.weapon_timer = 2  # Timer auf 2 Frames (Spiel-Ticks) setzen
    
    # Act & Assert - Frame 1
    player.update_buffs()
    assert player.weapon_type == "double", "Nach 1 Frame sollte der Buff noch aktiv sein."
    
    # Act & Assert - Frame 2
    player.update_buffs()
    assert player.weapon_type == "single", "Wenn der Timer 0 erreicht, muss die Waffe wieder 'single' sein."

def test_player_poison_debuff_reduces_speed():
    """Prüft, ob ein durch Gift modifizierter Speed nach Ablauf des Debuff-Timers wieder normalisiert wird."""
    # Arrange
    player = Player(x=400, y=500, player_id=1)
    
    # Gift-Effekt simulieren: Geschwindigkeit halbieren und Timer setzen
    player.speed = int(player.base_speed * 0.5) 
    player.poison_debuff_timer = 2 
    
    assert player.speed < player.base_speed, "Die Geschwindigkeit muss aktuell reduziert sein."
    
    # Act: Spiel-Ticks simulieren
    player.update_buffs() # Frame 1
    player.update_buffs() # Frame 2: Timer läuft ab!
    
    # Assert
    assert player.speed == player.base_speed, "Nach Ablauf des Gift-Timers muss die Basis-Geschwindigkeit wiederhergestellt sein."