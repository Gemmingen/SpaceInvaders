======================================================================
SPACE INVADERS
A classic Space Invaders game completely rebuilt in Python/Pygame,
expanded with multiple game modes, boss fights, power-ups, and
local multiplayer support!

Designed for standard PC play as well as Arcade Cabinet integration.

[ GAME FEATURES ]
Multiple Game Modes:

Story Mode (1-2 Players): Fight through 5 distinct levels, each
ending with a unique mini-boss or the final EndBoss.

Endless Survival (1-2 Players): Waves scale infinitely in
difficulty. Try to survive as long as possible!

Versus Mode (2 Players): Compete against a friend on a split
screen to see who can survive the longest and score the most.

Dynamic Boss Fights:

5 Unique Bosses featuring complex mechanics like poison puddles,
laser grids, charging fists, and cloning abilities.

Power-Ups & Bonuses:

Drops include: Comet Strikes, Bunker Repairs, Extra HP, Speed
Boosts, Double Shot, and Triple Shot.

Mystery UFOs spawn periodically for massive bonus points!

Modern Retro Enhancements:

Destructible bunkers that deteriorate as they take damage.

Local Highscore tracking for both single-player and multiplayer.

Parallax scrolling backgrounds and cinematic level transitions.

Arcade LED integration via WebSockets (ws://localhost:8765).

[ CONTROLS ]
Menu Navigation:
[W] / [S] or [UP] / [DOWN]     -- Navigate Options
[SPACE] or [NUMPAD 0]          -- Select Option
[R]                            -- Reset / Back to Menu
[Q]                            -- Quit Game

Player 1 (Left Side):
[A] / [D]                      -- Move Left / Right
[SPACE]                        -- Shoot

Player 2 (Right Side):
[LEFT ARROW] / [RIGHT ARROW]   -- Move Left / Right
[NUMPAD 0]                     -- Shoot

[ INSTALLATION & SETUP ]
Ensure you have Python 3 installed on your system.

Install the required dependencies:
$ pip install -r requirements.txt

(Note: This will install pygame==2.6.1 and websockets==16.0)

Run the game:
$ python main.py

[ SYSTEM REQUIREMENTS ]
Python 3.12+ (Recommended based on project structure)

Keyboard required (Local Co-op requires a shared keyboard or
arcade controller mapping)

Screen Resolution: Runs natively at 1080x1080 (Arcade format)
and scales to fit full screen.

======================================================================
Have fun defending the galaxy!
