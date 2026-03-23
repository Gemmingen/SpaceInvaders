"""
Tests für das Hauptmenü und das Highscore-System.
Prüft, ob das Spiel die JSON-Dateien korrekt verarbeitet und vor Abstürzen geschützt ist.
"""
import pytest
import pygame
from src.game.mainmenue import MainMenu

@pytest.fixture
def main_menu(mocker):
    """
    Erstellt ein MainMenu-Objekt für die Tests. 
    Wir mocken pygame.font.Font, damit er nicht versucht, die echten Schriftarten-Dateien 
    (PressStart2P) zu laden, falls diese auf dem Test-Server fehlen.
    """
    mocker.patch("pygame.font.Font")
    return MainMenu(font="dummy_font")

def test_load_top_scores_sorts_and_limits(main_menu, mocker):
    """Prüft, ob die Highscores korrekt nach Punkten sortiert und auf 5 Plätze limitiert werden."""
    # Arrange
    mocker.patch('os.path.exists', return_value=True) # Wir tun so, als ob die Datei existiert
    
    # Eine simulierte, unsortierte Highscore-Liste mit 6 Einträgen
    fake_json_data = {
        "sp_story": [
            {"name": "Anton", "score": 100},
            {"name": "Berta", "score": 500},
            {"name": "Caesar", "score": 200},
            {"name": "Dora", "score": 600},
            {"name": "Emil", "score": 50},
            {"name": "Friedrich", "score": 1000}
        ]
    }
    
    # Wir blockieren "open" (Datei öffnen) und "json.load" und geben unsere Fake-Daten zurück
    mocker.patch('builtins.open', mocker.mock_open())
    mocker.patch('json.load', return_value=fake_json_data)
    
    # Act
    scores = main_menu.load_top_scores("dummy_pfad.json", "sp_story")
    
    # Assert
    assert len(scores) == 5, "Die Highscore-Liste muss auf maximal 5 Einträge gekürzt werden."
    assert scores[0]["name"] == "Friedrich", "Der Spieler mit den meisten Punkten muss auf Platz 1 sein."
    assert scores[0]["score"] == 1000, "Der höchste Score muss ganz oben stehen."
    assert scores[-1]["name"] == "Anton", "Der niedrigste der Top 5 muss auf dem letzten Platz stehen."

def test_load_top_scores_file_not_found(main_menu, mocker):
    """Prüft, ob das Spiel absturzfrei bleibt, wenn die Highscore-Datei (noch) nicht existiert."""
    # Arrange
    mocker.patch('os.path.exists', return_value=False)
    
    # Act
    scores = main_menu.load_top_scores("gibt_es_nicht.json", "sp_story")
    
    # Assert
    assert scores == [], "Wenn keine Datei existiert, muss eine leere Liste zurückgegeben werden."

def test_load_top_scores_corrupt_json(main_menu, mocker):
    """Prüft, ob ein Fehler beim Laden (z.B. kaputte JSON) abgefangen wird."""
    # Arrange
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open())
    
    # Wir zwingen json.load dazu, einen Error zu werfen (Simulation einer defekten Datei)
    mocker.patch('json.load', side_effect=Exception("Kaputte Datei!"))
    
    # Act
    scores = main_menu.load_top_scores("kaputt.json", "sp_story")
    
    # Assert
    assert scores == [], "Bei einer korrupten JSON muss das Spiel das sicher abfangen und eine leere Liste liefern."