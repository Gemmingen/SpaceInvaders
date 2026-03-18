import asyncio
import threading
import json
import websockets
import time

class LedController:
    def __init__(self, url: str = "ws://localhost:8765"):
        self._url = url
        self._ws = None
        # Wir brauchen ein Event, um zu wissen, wann die Verbindung steht
        self._connected_event = threading.Event()
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._main_logic())

    async def _main_logic(self):
        """Dauerschleife, die versucht die Verbindung zu halten."""
        while True:
            try:
                # ping_interval sorgt dafür, dass die Verbindung aktiv bleibt (Heartbeat)
                async with websockets.connect(self._url, ping_interval=5, ping_timeout=5) as ws:
                    self._ws = ws
                    self._connected_event.set()
                    print(f"LED Controller: Verbunden mit {self._url}")
                    
                    # Warte solange die Verbindung lebt
                    await ws.wait_closed()
            except Exception as e:
                self._ws = None
                self._connected_event.clear()
                #print(f"LED Controller: Verbindung verloren ({e}). Reconnect in 2s...")
                await asyncio.sleep(2) # Kurz warten vor dem nächsten Versuch

    def send_effect(self, chain, effect_type, segment, r, g, b, speed=50, repeat=1, priority=2):
        payload = {
            "cmd": "effect", "chain": chain, "type": effect_type,
            "segment": segment, "color": {"r": r, "g": g, "b": b},
            "speed": speed, "repeat": repeat, "priority": priority,
        }
        self._safe_send(json.dumps(payload))

    def attract_pause(self):
        self._safe_send('{"cmd":"attract","state":"pause"}')

    def attract_resume(self):
        self._safe_send('{"cmd":"attract","state":"resume"}')

    def _safe_send(self, message):
        """Hilfsmethode, um Nachrichten sicher in den Async-Loop zu schieben."""
        if self._ws and self._connected_event.is_set():
            try:
                self._loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(self._ws.send(message))
                )
            except Exception:
                pass

    async def _send(self, message):
        # Diese Methode wird durch _safe_send (call_soon_threadsafe) ersetzt
        if self._ws:
            await self._ws.send(message)