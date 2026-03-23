"""
Tests für die Multiplayer- und Versus-Logik der Haupt-Spielklasse.
Stellt sicher, dass Spieler korrekt erstellt und Spielfelder sauber getrennt werden.
"""
import pytest
import pygame
from src.game.game import Game

def test_coop_mode_spawns_two_players():
    """Prüft, ob im Story-Modus mit 2 Spielern auch wirklich zwei Player-Objekte existieren."""
    # Arrange
    game = Game()
    game.game_mode = "story"
    game.num_players = 2
    
    # Act
    game._reset() # _reset baut das Spielfeld basierend auf den Einstellungen neu auf
    
    # Assert
    assert game.player1 is not None, "Player 1 muss existieren."
    assert game.player2 is not None, "Player 2 muss existieren."
    assert len(game.active_players) == 2, "Es müssen exakt 2 aktive Spieler in der Liste sein."
    assert game.player1.player_id == 1, "Player 1 muss ID 1 haben."
    assert game.player2.player_id == 2, "Player 2 muss ID 2 haben."

def test_versus_mode_creates_split_boards():
    """Prüft, ob der Versus-Modus die Variablen für zwei getrennte Spielfelder (Boards) anlegt."""
    # Arrange
    game = Game()
    game.game_mode = "versus"
    game.num_players = 2
    
    # Act
    game._reset()
    
    # Assert
    assert game.boards is not None, "Im Versus-Modus muss das boards-Dictionary existieren."
    assert 1 in game.boards, "Es muss ein Board-State für Spieler 1 existieren."
    assert 2 in game.boards, "Es muss ein Board-State für Spieler 2 existieren."
    
    # Prüfen, ob die Start-Scores auf beiden Boards unabhängig voneinander 0 sind
    assert game.boards[1]['score'] == 0
    assert game.boards[2]['score'] == 0

def test_singleplayer_does_not_spawn_player2():
    """Stellt sicher, dass im Singleplayer kein zweiter Spieler als 'Geist' mitläuft."""
    # Arrange
    game = Game()
    game.game_mode = "story"
    game.num_players = 1
    
    # Act
    game._reset()
    
    # Assert
    assert game.player1 is not None, "Player 1 muss existieren."
    assert game.player2 is None, "Player 2 darf im Singleplayer nicht existieren."
    assert len(game.active_players) == 1, "Es darf nur 1 aktiver Spieler in der Liste sein."