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

        # --- FIX: Event-basierte Cooldowns (in Sekunden) ---
        # Gibt den Animationen genug Zeit, ihre Frames zu zeigen, ohne unterbrochen zu werden
        self._cooldowns = {
            "boss_hit": 0.08,
            "alien_hit": 0.18,   
            "bunker_hit": 0.15,  
            "ufo_appear": 0.5,
            "ufo_hit": 0.3,
            "menu_nav": 0.05,
            "warp_transition": 4.0,
            # Fallbacks für rohe Effekttypen
            "sparkle": 0.05,
            "pulse": 0.05,
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

    def send_effect(self, chain, effect_type, segment, r, g, b, speed=100, length=5, repeat=1, dir=1, priority=2, event_key=None, auto_clear_duration=0.0):
        """Sendet einen Effekt mit intelligentem, Event-spezifischem Spam-Schutz."""
        current_time = time.time()
        
        cooldown_key = event_key if event_key else effect_type
        
        # Erst nach Event-Key-Spezifischem Cooldown suchen, sonst Fallback auf Effect-Type
        cd = self._cooldowns.get(cooldown_key, self._cooldowns.get(effect_type, 0))
        
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

        # Nach Ablauf der Animation ein "Clear" (Schwarz) senden
        if auto_clear_duration > 0.0 and cooldown_key:
            self._loop.call_soon_threadsafe(
                lambda: asyncio.create_task(
                    self._async_delayed_clear(cooldown_key, auto_clear_duration, chain, segment, priority)
                )
            )

    async def _async_delayed_clear(self, event_key, duration, chain, segment, priority):
        """Wartet, bis die Animation sicher vorbei ist, und schaltet ab (falls kein neuer Hit kam)."""
        trigger_time = self._last_sent.get(event_key, 0)
        await asyncio.sleep(duration)
        
        # Nur abschalten, wenn in der Zwischenzeit kein neuerer Hit registriert wurde
        if self._last_sent.get(event_key, 0) == trigger_time:
            clear_payload = {
                "cmd": "effect", 
                "chain": chain, 
                "type": "fill",
                "segment": segment, 
                "color": {"r": 0, "g": 0, "b": 0}, # AUS (Schwarz)
                "speed": 100, 
                "length": 1, 
                "repeat": 1, 
                "dir": 1,        
                "priority": priority,
            }
            try:
                if self._ws:
                    await self._ws.send(json.dumps(clear_payload))
            except Exception:
                pass

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

    # ─── SPACE INVADERS EVENTS MIT INTELLIGENTEN AUTO-CLEAR TIMINGS ───

    def effect_sys_start_si(self):
        self.send_effect(chain="A", effect_type="wipe", segment=99, r=0, g=255, b=0, speed=20, repeat=1, priority=4, event_key="sys_start", auto_clear_duration=0.5)

    def effect_si_alien(self):
        # 5 Repeats brauchen Zeit. Wir geben dem Effekt 0.45s zum Auslaufen.
        # Wenn du wild rumballerst, schaltet es sich erst 0.45s nach dem LETZTEN getöteten Alien aus.
        self.send_effect(chain="A", effect_type="sparkle", segment=99, r=0, g=255, b=0, speed=50, repeat=5, priority=4, event_key="alien_hit", auto_clear_duration=0.45)

    def effect_si_ufo_appear(self):
        self.send_effect(chain="A", effect_type="chase", segment=0, r=0, g=255, b=255, speed=30, length=6, repeat=3, priority=4, event_key="ufo_appear", auto_clear_duration=0.8)

    def effect_si_ufo_hit(self):
        self.send_effect(chain="A", effect_type="sparkle", segment=0, r=0, g=255, b=255, speed=50, repeat=8, priority=4, event_key="ufo_hit", auto_clear_duration=0.4)

    def effect_si_bunker(self):
        # Erhöhte Dauer (0.32s), damit der Pulse-Effekt komplett beendet ist, bevor Schwarz gesendet wird.
        self.send_effect(chain="A", effect_type="pulse", segment=5, r=255, g=140, b=0, speed=70, repeat=1, priority=4, event_key="bunker_hit", auto_clear_duration=0.32)

    def effect_si_wave(self):
        self.send_effect(chain="A", effect_type="wipe", segment=99, r=0, g=255, b=0, speed=30, repeat=1, priority=4, event_key="next_wave", auto_clear_duration=0.5)

    def effect_si_death(self):
        self.send_effect(chain="A", effect_type="blink", segment=99, r=255, g=0, b=0, speed=150, repeat=2, priority=4, event_key="player_death", auto_clear_duration=0.5)


    def effect_si_powerup(self):
        self.send_effect(chain="A", effect_type="blink", segment=1, r=0, g=255, b=255, speed=10, repeat=5, priority=5, event_key="powerup_collect", auto_clear_duration=0.4)

    def effect_si_bonusitem(self):  
        self.send_effect(chain="A", effect_type="blink", segment=1, r=255, g=255, b=0, speed=10, repeat=3, priority=5, event_key="bonus_collect", auto_clear_duration=0.4)

    def effect_menu_nav(self):
        self.send_effect(chain="A", effect_type="pulse", segment=1, r=255, g=215, b=0, speed=150, repeat=1,priority=3, event_key="menu_nav", auto_clear_duration=0.1)

    # --- 2. Als neue Methode in die LedController-Klasse einfügen: ---
    def effect_si_boss_hit(self, level):
        boss_colors = {
            1: {"r": 255, "g": 110, "b": 0},   # Boss 1: Orange
            2: {"r": 130, "g": 130, "b": 130}, # Boss 2: Grau
            3: {"r": 0,   "g": 100, "b": 0},   # Boss 3: Dunkelgrün
            4: {"r": 0,   "g": 255, "b": 50},  # Boss 4: Hellgrün
            5: {"r": 160, "g": 0,   "b": 255}  # Boss 5: Lila
        }
        color = boss_colors.get(level, {"r": 255, "g": 255, "b": 255})
    
        self.send_effect(chain="A", effect_type="blink", segment=99, r=color["r"], g=color["g"], b=color["b"],speed=130,repeat=1, priority=4, event_key="boss_hit", auto_clear_duration=0.15)
    def effect_si_gameover(self):
            self.send_effect(chain="A", effect_type="wipe", segment=99, r=255, g=0, b=0, speed=30, repeat=1, priority=4, event_key="player_death", auto_clear_duration=0.8)

    def effect_si_transition(self):
        self.send_effect(chain="A", effect_type="pulse", segment=99, r=150, g=230, b=255, speed=5, repeat=20, priority=4, event_key="warp_transition",auto_clear_duration=2.5)