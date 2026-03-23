"""
Zentrale Konfigurationsdatei für Pytest (conftest.py).

Diese Datei wird von Pytest automatisch erkannt und VOR allen anderen Tests ausgeführt.
Sie dient dazu, die Testumgebung global vorzubereiten. Da wir ein Videospiel testen,
müssen wir verhindern, dass Pygame bei den automatisierten Tests echte Fenster öffnet,
Sounds abspielt oder auf die Festplatte zugreift.
"""
import os
import pytest
import pygame

# Pygame versucht standardmäßig, mit der Grafikkarte zu kommunizieren.
# Das führt beim Starten der Tests oft zu einem kurzen schwarzen Flackern.
# Indem wir den Videotreiber auf "dummy" setzen, zwingen wir Pygame in einen reinen 
# Hintergrund-Modus (Headless). 
# WICHTIG: Das muss zwingend VOR pygame.init() aufgerufen werden!
os.environ["SDL_VIDEODRIVER"] = "dummy"

@pytest.fixture(autouse=True)
def mock_pygame_env(mocker):
    """
    Simuliert (mockt) die Laufzeitumgebung für das Spiel.
    Durch 'autouse=True' wird dieser Block automatisch vor JEDEM einzelnen Test ausgeführt.
    """
    # Kernmodule von Pygame initialisieren (läuft jetzt unsichtbar im Dummy-Modus)
    pygame.init()
    
    # Ein Alibi-Display erstellen (1x1 Pixel).
    # Warum? Viele Pygame-Funktionen (wie .convert_alpha() beim Laden von Grafiken) 
    # werfen sofort einen Fatal Error, wenn kein Display-Modus gesetzt wurde.
    pygame.display.set_mode((1, 1))
    
    # Eine winzige Fake-Grafik (32x32 Pixel) als Platzhalter erstellen.
    # Wir wollen in den Tests keine echten PNG-Dateien laden, da das langsam ist
    # und auf Test-Servern (CI/CD) oft die Dateipfade nicht exakt stimmen.
    fake_surface = pygame.Surface((32, 32))
    
    # --- GRAFIKEN MOCKEN ---
    # Immer wenn das Spiel versucht, ein Bild zu laden, fangen wir den Aufruf ab
    # und geben sofort unsere leere fake_surface zurück.
    mocker.patch('pygame.image.load', return_value=fake_surface)
    mocker.patch('src.utils.helpers.load_image', return_value=fake_surface)
    
    # --- KOLLISIONSMASKEN MOCKEN ---
    # Masken berechnen pixelgenaue Kollisionen aus Grafiken. Da wir jetzt nur noch
    # leere Dummy-Grafiken haben, schalten wir die Masken-Generierung ab, damit sie 
    # nicht ins Leere läuft oder abstürzt.
    mocker.patch('pygame.mask.from_surface')
    mocker.patch('pygame.mask.from_threshold')
    
    # --- AUDIO MOCKEN ---
    # Schaltet die komplette Audio-Engine stumm. Verhindert, dass beim Ausführen 
    # der automatisierten Tests plötzlich Laserschüsse oder Boss-Musik abspielen 
    # oder das Spiel crasht, weil eine MP3 nicht gefunden wird.
    mocker.patch('pygame.mixer.Sound')
    mocker.patch('pygame.mixer.music.load')
    mocker.patch('pygame.mixer.music.play')