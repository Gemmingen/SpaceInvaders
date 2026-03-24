import asyncio
import threading
import json
import websockets

class LedController:
    def __init__(self, url: str = "ws://localhost:8765"):
        self._url = url
        self._ws = None
        # Event, um den Verbindungsstatus thread-sicher zu prüfen
        self._connected_event = threading.Event()
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self):
        """Startet den asyncio Loop in einem eigenen Thread."""
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._main_logic())
        except Exception:
            pass # Stilles Beenden des Loops bei Fehlern

    async def _main_logic(self):
        """Dauerschleife, die versucht die Verbindung stabil zu halten."""
        while True:
            try:
                # ping_interval hält die Verbindung aktiv (Heartbeat)
                async with websockets.connect(self._url, ping_interval=5, ping_timeout=5) as ws:
                    self._ws = ws
                    self._connected_event.set()
                    # Optional: print(f"LED Controller: Verbunden mit {self._url}")
                    
                    # Warte solange die Verbindung lebt
                    await ws.wait_closed()
            except Exception:
                # Verbindung verloren oder Server nicht erreichbar
                self._ws = None
                self._connected_event.clear()
                # Reconnect-Versuch nach 2 Sekunden
                await asyncio.sleep(2)

    def send_effect(self, chain, effect_type, segment, r, g, b, speed=50, repeat=1, priority=2):
        """Sendet einen LED-Effekt an den Server."""
        payload = {
            "cmd": "effect", 
            "chain": chain, 
            "type": effect_type,
            "segment": segment, 
            "color": {"r": r, "g": g, "b": b},
            "speed": speed, 
            "repeat": repeat, 
            "priority": priority,
        }
        self._safe_send(json.dumps(payload))

    def attract_pause(self):
        """Pausiert den Attract-Mode (Standard-Animation)."""
        self._safe_send('{"cmd":"attract","state":"pause"}')

    def attract_resume(self):
        """Setzt den Attract-Mode fort."""
        self._safe_send('{"cmd":"attract","state":"resume"}')

    def _safe_send(self, message):
        """
        Schiebt die Nachricht in den Async-Loop, ohne das Hauptspiel zu blockieren
        oder die Konsole mit Fehlern zu fluten.
        """
        if self._ws and self._connected_event.is_set():
            try:
                # Wir definieren eine interne Coroutine, die Fehler still abfängt
                async def silent_send():
                    try:
                        if self._ws:
                            await self._ws.send(message)
                    except Exception:
                        pass # Fehler beim Senden werden ignoriert (Silent)

                # Thread-sicherer Aufruf im asyncio-Loop
                self._loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(silent_send())
                )
            except Exception:
                pass # Falls der Loop gerade nicht bereit ist