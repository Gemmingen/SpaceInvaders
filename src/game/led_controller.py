import asyncio
import threading
import json
import websockets
import time

class LedController:
    def __init__(self, url: str = "ws://localhost:8765"):
        self._url = url
        self._ws = None
        self._connected_event = threading.Event()
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

        # Cooldowns in Sekunden pro Effekttyp
        self._cooldowns = {
            "sparkle": 0.05,
            "pulse": 0.1,
            "wipe": 0.2,
            "blink": 0.05,
            "chase": 0.1,
            "fill": 0.5
        }
        self._last_sent = {}

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._main_logic())
        except Exception as e:
            print(f"[LED-Controller] Asynchroner Loop abgebrochen: {e}")

    async def _main_logic(self):
        while True:
            try:
                async with websockets.connect(self._url, ping_interval=5, ping_timeout=5) as ws:
                    self._ws = ws
                    self._connected_event.set()
                    print(f"[LED-Controller] Verbindung erfolgreich aufgebaut zu {self._url}")
                    await ws.wait_closed()
            except Exception as e:
                print(f"[LED-Controller] Verbindungsfehler: {e}. Versuche Reconnect in 2 Sekunden...")
                self._ws = None
                self._connected_event.clear()
                await asyncio.sleep(2)

    def send_effect(self, chain, effect_type, segment, r, g, b, speed=100, length=5, repeat=1, dir=1, priority=2, event_key=None):
        """Sendet einen Effekt mit verbessertem, event-basiertem Spam-Schutz."""
        current_time = time.time()
        
        cooldown_key = event_key if event_key else effect_type
        cd = self._cooldowns.get(effect_type, 0)
        
        if cd > 0 and (current_time - self._last_sent.get(cooldown_key, 0) < cd):
            return
            
        self._last_sent[cooldown_key] = current_time

        payload = {
            "cmd": "effect", 
            "chain": chain, 
            "type": effect_type,
            "segment": segment, 
            "color": {"r": r, "g": g, "b": b},
            "speed": speed, 
            "length": length, 
            "repeat": repeat, 
            "dir": dir,        
            "priority": priority,
        }
        self._safe_send(json.dumps(payload))

    def attract_pause(self):
        self._safe_send('{"cmd":"attract","state":"pause"}')

    def attract_resume(self):
        self._safe_send('{"cmd":"attract","state":"resume"}')

    def _safe_send(self, message):
        if self._ws and self._connected_event.is_set():
            try:
                async def silent_send():
                    try:
                        if self._ws:
                            await self._ws.send(message)
                    except Exception as e:
                        print(f"[LED-Controller] WebSocket Sende-Fehler: {e}")
                self._loop.call_soon_threadsafe(lambda: asyncio.create_task(silent_send()))
            except Exception as e:
                print(f"[LED-Controller] Threadsafe-Fehler beim Queueing: {e}")

    # ─── SPACE INVADERS EVENTS (Prioritäten auf 4+ erhöht) ───

    def effect_sys_start_si(self):
        self.send_effect(chain="A", effect_type="wipe", segment=99, r=0, g=255, b=0, speed=20, repeat=1, priority=4, event_key="sys_start")

    def effect_si_alien(self):
        self.send_effect(chain="A", effect_type="sparkle", segment=99, r=0, g=255, b=0, speed=50, repeat=5, priority=4, event_key="alien_hit")

    def effect_si_ufo_appear(self):
        self.send_effect(chain="A", effect_type="chase", segment=0, r=0, g=255, b=255, speed=30, length=6, repeat=3, priority=4, event_key="ufo_appear")

    def effect_si_ufo_hit(self):
        self.send_effect(chain="A", effect_type="sparkle", segment=0, r=0, g=255, b=255, speed=50, repeat=8, priority=4, event_key="ufo_hit")

    def effect_si_bunker(self):
        self.send_effect(chain="A", effect_type="pulse", segment=5, r=255, g=140, b=0, speed=40, repeat=2, priority=4, event_key="bunker_hit")

    def effect_si_wave(self):
        self.send_effect(chain="A", effect_type="wipe", segment=99, r=0, g=255, b=0, speed=30, repeat=1, priority=4, event_key="next_wave")

    def effect_si_death(self):
        self.send_effect(chain="A", effect_type="blink", segment=99, r=255, g=0, b=0, speed=150, repeat=2, priority=4, event_key="player_death")

    def effect_si_gameover(self):
        self.send_effect(chain="A", effect_type="fill", segment=99, r=255, g=0, b=0, speed=100, repeat=1, priority=5, event_key="game_over")

    def effect_si_powerup(self):
        self.send_effect(chain="A", effect_type="blink", segment=1, r=0, g=255, b=255, speed=10, repeat=5, priority=5, event_key="powerup_collect")

    def effect_si_bonusitem(self):  # FIX: Das angehängte 'a' wurde entfernt
        self.send_effect(chain="A", effect_type="blink", segment=1, r=255, g=255, b=0, speed=10, repeat=3, priority=5, event_key="bonus_collect")

    def effect_si_transition(self):
        self.send_effect(chain="A", effect_type="chase", segment=0, r=255, g=255, b=255, speed=22, repeat=13, priority=4, event_key="warp_transition")