import pygame
import json
import os

class MainMenu:
    """
    Klasse zur Darstellung und Verwaltung des Hauptmenüs.
    Steuert die verschiedenen Menüzustände (Main, Singleplayer, Multiplayer)
    sowie das Rendern von Buttons, Titeln und plattformübergreifenden Highscore-Listen.
    """
    def __init__(self, font):
        # Basis-Schriftart, die potenziell von außen übergeben wird
        self.font = font
        
        # Initialisierung der spezifischen Schriftarten für verschiedene UI-Elemente
        # Nutzt den Retro-Font "PressStart2P-Regular"
        self.title_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 65)
        self.button_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 24)
        self.sub_title_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 35)
        
        self.credits_title_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 24)
        self.credits_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 18)
        
        # Farbkonstanten für den Credits-Bereich
        self.COLOR_GOLD = (255, 215, 0)
        self.COLOR_SILVER = (192, 192, 192)
        
        # Startzustand und initiale Button-Auswahl
        self.state = "MAIN"
        self.selection = 0

        # Erstellung eines halbtransparenten Overlays, um den Hintergrund abzudunkeln
        self.overlay = pygame.Surface((1920, 1080), pygame.SRCALPHA) 
        self.overlay_alpha = 150 

    def _get_raw_scores(self, filename):
        """
        Liest die Highscore-Daten aus einer JSON-Datei ein.
        Sucht die Datei zwei Verzeichnisebenen über dem aktuellen Skript.
        """
        # Pfadkonstruktion relativ zur Position dieses Skripts
        base_path = os.path.dirname(os.path.abspath(__file__))
        root_path = os.path.dirname(os.path.dirname(base_path))
        filepath = os.path.join(root_path, filename)
        
        # Fehlerresistentes Laden der JSON-Daten
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                try: return json.load(f)
                except: return {} # Fallback bei ungültigem JSON
        return {} # Fallback bei fehlender Datei

    def draw(self, surface, selected_index=0):
        """
        Hauptzeichenfunktion, die in jedem Frame aufgerufen wird.
        Rendert die UI-Elemente basierend auf dem aktuellen Zustand (self.state).
        """
        self.selection = selected_index
        sw = surface.get_width()
        sh = surface.get_height()

        # Overlay zeichnen (verdunkelt das eigentliche Spielgeschehen im Hintergrund)
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.overlay_alpha)) 
        surface.blit(overlay, (0, 0))

        # --- HAUPTTITEL ---
        # Wird in jedem Zustand oben mittig angezeigt
        title_surf = self.title_font.render("SPACE INVADERS", True, (0, 255, 0))
        surface.blit(title_surf, title_surf.get_rect(center=(sw // 2, 120)))

        # --- ZUSTANDS-LOGIK (State Machine) ---
        if self.state == "MAIN":
            # Hauptmenü: Zeigt alle Leaderboards und die Hauptkategorien
            self._draw_main_leaderboards(surface, sw)
            self._draw_pure_buttons(surface, ["SINGLEPLAYER", "MULTIPLAYER"], 400, sw, width=450, height=75)
            
        elif self.state == "SINGLEPLAYER":
            # Untermenü: Singleplayer (Story, Endless, Zurück)
            sub_title = self.sub_title_font.render("SINGLEPLAYER", True, (255, 255, 0))
            surface.blit(sub_title, sub_title.get_rect(center=(sw // 2, 220)))
            self._draw_pure_buttons(surface, ["STORY MODE", "ENDLESS MODE", "BACK"], 350, sw, width=450, height=65)
            # Leaderboards flankieren links und rechts die Buttons
            self._draw_side_leaderboards(surface, "sp_story", "sp_endless", "STORY", "ENDLESS", "highscores_sp.json", (255, 255, 0), sw)

        elif self.state == "MULTIPLAYER":
            # Untermenü: Multiplayer (Co-Op, Versus, Zurück)
            sub_title = self.sub_title_font.render("MULTIPLAYER", True, (0, 191, 255))
            surface.blit(sub_title, sub_title.get_rect(center=(sw // 2, 220)))
            self._draw_pure_buttons(surface, ["STORY (CO-OP)", "ENDLESS (CO-OP)", "VERSUS", "BACK"], 320, sw, width=500, height=65)
            self._draw_mp_leaderboards(surface, sw)

        # Credits werden immer ganz unten angezeigt, unabhängig vom Status
        self._draw_credits(surface, sw, sh)

    def _draw_main_leaderboards(self, surface, sw):
        """Zeichnet eine Übersicht aller Highscore-Listen auf dem Hauptbildschirm."""
        small_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 16)
        
        # Fest definierte Säulen bei 20% und 80% der Bildschirmbreite
        left_x = sw // 5
        right_x = (sw * 4) // 5
        
        # Linke Spalte: Singleplayer
        self._render_leaderboard(surface, "SP STORY", "highscores_sp.json", "sp_story", 280, left_x, small_font, (255, 255, 0))
        self._render_leaderboard(surface, "SP ENDLESS", "highscores_sp.json", "sp_endless", 560, left_x, small_font, (255, 255, 0))
        
        # Rechte Spalte: Multiplayer (Co-Op)
        self._render_leaderboard(surface, "MP STORY", "highscores_mp.json", "mp_story", 280, right_x, small_font, (0, 191, 255))
        self._render_leaderboard(surface, "MP ENDLESS", "highscores_mp.json", "mp_endless", 560, right_x, small_font, (0, 191, 255))
        
        # Untere Mitte: Versus-Modus
        self._render_leaderboard(surface, "VERSUS", "highscores_mp.json", "mp_versus", 700, sw // 2, small_font, (255, 50, 50))

    def _draw_pure_buttons(self, surface, options, start_y, sw, width, height):
        """
        Zeichnet die auswählbaren Buttons in der Mitte des Bildschirms.
        Hebt den aktuell ausgewählten Button farblich und mit Pfeilen hervor.
        """
        for i, text in enumerate(options):
            is_selected = (i == self.selection)
            # Basis-Rechteck für den Button
            rect = pygame.Rect(0, 0, width, height)
            rect.center = (sw // 2, start_y + (i * (height + 30)))

            # Schwarzer Hintergrund für den Button
            pygame.draw.rect(surface, (0, 0, 0), rect)

            # Visuelles Feedback basierend auf der Auswahl
            if is_selected:
                # Dicker, grüner Rand und Pfeile (Indikatoren) für den fokussierten Button
                pygame.draw.rect(surface, (0, 255, 0), rect, 6)
                display_text = f"> {text} <"
                txt_color = (0, 255, 0)
            else:
                # Schlichter grauer Rand für nicht ausgewählte Buttons
                pygame.draw.rect(surface, (100, 100, 100), rect, 2)
                display_text = text
                txt_color = (255, 255, 255)

            # Text rendern und mittig im Button-Rechteck platzieren
            txt_surf = self.button_font.render(display_text, True, txt_color)
            txt_rect = txt_surf.get_rect(center=rect.center)
            surface.blit(txt_surf, txt_rect)

    def _draw_side_leaderboards(self, surface, key1, key2, label1, label2, file, color, sw):
        """Zeichnet zwei Highscore-Listen, flankierend links und rechts im Singleplayer-Menü."""
        small_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 16)
        
        # Positionierung bei 20% und 80% der Bildschirmbreite
        left_x = sw // 5
        right_x = (sw * 4) // 5
        
        # Auf Y=480 gesetzt, damit sie zentrierter und höher liegen (angepasst an die Button-Höhe)
        self._render_leaderboard(surface, f"TOP 5 {label1}", file, key1, 480, left_x, small_font, color)
        self._render_leaderboard(surface, f"TOP 5 {label2}", file, key2, 480, right_x, small_font, color)

    def _draw_mp_leaderboards(self, surface, sw):
        """Zeichnet die Highscore-Listen speziell für das Multiplayer-Menü."""
        small_font = pygame.font.Font("assets/headerbar/PressStart2P-Regular.ttf", 16)
        
        left_x = sw // 5
        right_x = (sw * 4) // 5
        mid_x = sw // 2
        
        y_sides = 480  # Gleiche Höhe wie im Singleplayer für visuelle Konsistenz
        y_bottom = 710 # Das Versus-Board sitzt tiefer unten in der Mitte
        
        self._render_leaderboard(surface, "TOP 5 STORY", "highscores_mp.json", "mp_story", 
                                 y_sides, left_x, small_font, (0, 191, 255))
        self._render_leaderboard(surface, "TOP 5 ENDLESS", "highscores_mp.json", "mp_endless", 
                                 y_sides, right_x, small_font, (0, 191, 255))
        self._render_leaderboard(surface, "TOP 5 VERSUS", "highscores_mp.json", "mp_versus", 
                                 y_bottom, mid_x, small_font, (255, 50, 50))

    def _render_leaderboard(self, surface, title, filename, mode_key, y_start, x_pos, font, color):
        """
        Allgemeine Funktion zum Rendern einer einzelnen Highscore-Liste (Titel + Top 5).
        """
        # Titel der Highscore-Liste rendern
        header = font.render(title, True, color)
        surface.blit(header, header.get_rect(center=(x_pos, y_start)))
        
        # Lade die Top 5 für diesen spezifischen Spielmodus
        scores = self.load_top_scores(filename, mode_key)
        
        if not scores:
            # Fallback-Anzeige, falls noch keine Scores existieren
            txt = font.render("EMPTY", True, (100, 100, 100))
            surface.blit(txt, txt.get_rect(center=(x_pos, y_start + 45)))
        else:
            # Iteriere durch die Einträge und rendere sie als Liste (z.B. "1.NAME-1000")
            for i, entry in enumerate(scores):
                name = entry.get('name', '???')[:8] # Name auf maximal 8 Zeichen begrenzen
                points = entry.get('score', 0)
                txt = f"{i+1}.{name}-{points}"
                s_surf = font.render(txt, True, (255, 255, 255))
                # Vertikaler Offset von 30 Pixeln pro Listeneintrag
                surface.blit(s_surf, s_surf.get_rect(center=(x_pos, y_start + 45 + (i * 30))))

    def load_top_scores(self, filename, mode_key):
        """
        Lädt die rohen Highscore-Daten, filtert den entsprechenden Spielmodus,
        sortiert absteigend nach Punktzahl und gibt die Top 5 zurück.
        """
        data = self._get_raw_scores(filename)
        res = data.get(mode_key, [])
        # Sortiere das Array anhand des "score"-Wertes (höchste zuerst) und schneide ab Index 5 ab
        return sorted(res, key=lambda x: x.get("score", 0), reverse=True)[:5]

    def _draw_credits(self, surface, sw, sh):
        """Rendert den Entwickler-Schriftzug am unteren Rand des Bildschirms."""
        y = sh - 90
        credits_title = self.credits_title_font.render("DEVELOPED BY SCHWARZ DIGITS", True, self.COLOR_GOLD)
        surface.blit(credits_title, credits_title.get_rect(center=(sw // 2, y)))
        
        names = "Macid Askar - Santino Brauch - Louis Edwell"
        name_surf = self.credits_font.render(names, True, self.COLOR_SILVER)
        surface.blit(name_surf, name_surf.get_rect(center=(sw // 2, y + 40)))