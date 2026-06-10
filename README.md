# Space Invaders

A classic Space Invaders game completely rebuilt in **Python/Pygame** — expanded with multiple
game modes, dynamic boss fights, power-ups, and local multiplayer support.

Designed for standard PC play as well as **Arcade Cabinet integration**.

---

## Features

### Game Modes

| Mode | Players | Description |
|------|---------|-------------|
| **Story Mode** | 1–2 | 5 distinct levels, each ending with a unique mini-boss or the final EndBoss |
| **Endless Survival** | 1–2 | Infinite waves with scaling difficulty — survive as long as possible |
| **Versus Mode** | 2 | Split-screen competition — who can score the most? |

### Boss Fights

5 unique bosses, each with their own attack pattern:

- Charging fist attacks
- Laser grids with orbiting projectiles
- Poison puddle hazards with splitting projectiles
- Cloning / spawning mechanic
- Final EndBoss with complex multi-phase behavior

### Power-Ups

Comet Strike · Bunker Repair · Extra HP · Speed Boost · Double Shot · Triple Shot

### Further Highlights

- Destructible bunkers that degrade visually with damage
- Mystery UFOs that spawn periodically for bonus points
- Local highscore tracking for single-player and multiplayer
- Parallax scrolling backgrounds and cinematic level transitions
- Arcade LED integration via WebSockets (`ws://localhost:8765`)

---

## Controls

### Menu Navigation

| Key | Action |
|-----|--------|
| `W` / `S` or `↑` / `↓` | Navigate options |
| `SPACE` or `NUMPAD 0` | Confirm / Select |
| `R` | Back to menu |
| `Q` | Quit |

### In-Game

| | Player 1 | Player 2 |
|--|----------|----------|
| **Move** | `A` / `D` | `←` / `→` |
| **Shoot** | `SPACE` | `NUMPAD 0` |

---

## Installation

Requires **Python 3.12+**.

```bash
pip install -r requirements.txt
python main.py
```

Dependencies: `pygame==2.6.1`, `websockets==16.0`

---

## System Requirements

- Python 3.12 or newer
- Screen resolution: 1080×1080 (scales to fullscreen)
- Keyboard required (local co-op uses a shared keyboard or arcade controller mapping)

---

## Project Structure

```
SpaceInvaders/
├── main.py                  # Entry point
├── requirements.txt
├── src/
│   ├── config/
│   │   └── config.py        # Central game configuration
│   ├── game/                # All game modules
│   │   ├── game.py          # Main game loop & state management
│   │   ├── player.py
│   │   ├── enemy.py
│   │   ├── boss_*.py        # Mini-boss implementations
│   │   ├── endboss.py
│   │   ├── powerup.py
│   │   ├── led_controller.py
│   │   └── ...
│   └── utils/
│       └── helpers.py
├── assets/                  # Sprites, backgrounds, music (424 files)
├── tests/                   # Pytest test suite
└── .github/workflows/       # CI/CD pipeline
```

---

## Testing

```bash
pytest
```

Tests run headless (no display required) using SDL's dummy video driver. Coverage includes
bosses, bunkers, power-ups, UFO mechanics, multiplayer, and the main menu.

---

## Building

Multi-platform executables are built with **PyInstaller** via GitHub Actions on every push
to `main`. Releases are published automatically when a version tag is pushed.

| Platform | Runner |
|----------|--------|
| Windows | windows-latest |
| macOS (Apple Silicon) | macos-latest |
| macOS (Intel) | macos-13 |
| Linux | ubuntu-latest |

---

## Tech Stack

| Library | Purpose |
|---------|---------|
| [Pygame 2.6.1](https://www.pygame.org/) | Game engine & rendering |
| [websockets 16.0](https://websockets.readthedocs.io/) | Arcade LED integration |
| [pytest](https://pytest.org/) | Automated testing |
| [PyInstaller](https://pyinstaller.org/) | Cross-platform executable packaging |

---

Have fun defending the galaxy!
