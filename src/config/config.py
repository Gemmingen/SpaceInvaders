
# Game configuration settings


SCREEN_WIDTH = 1080                                  #800 Original size, not for Arcade Version
SCREEN_HEIGHT = 1080 #1080                           #600 Original size, not for Arcade Version
FPS = 60
# Bonus UFO (Mystery Ship) configuration
UFO_SPAWN_HEIGHT_OPTIONS = [80, 300, 800]           # possible vertical spawn positions for the UFO (in pixels from top)
UFO_SPEED_OPTIONS = [3, 7, 10]                      # possible speeds for the UFO (pixels per frame)
UFO_SPAWN_TIME = 15                                 # seconds before a UFO may appear
UFO_SCORE_OPTIONS = [1200, 1312, 1500, 1600, 1800]  # possible bonus points
UFO_SHOT_THRESHOLD = 30                             # number of player shots that can also trigger a UFO

# Player Settings
PLAYER_SPEED = 5

# Enemy Settings
ENEMY_SPEED = 3
ENEMY_SHOOT_CHANCE = 0.001                           # Chance per frame that an enemy will shoot (adjust for difficulty)
BULLET_SPEED = 10

# Enemy wave per level – can be tweaked later
TEST_AMOUNT = 1

ENEMY_WAVE_SETTINGS = {
    1: dict(rows=TEST_AMOUNT, cols=TEST_AMOUNT, speed=ENEMY_SPEED, shoot_chance=ENEMY_SHOOT_CHANCE),
    2: dict(rows=TEST_AMOUNT, cols=TEST_AMOUNT, speed=ENEMY_SPEED, shoot_chance=ENEMY_SHOOT_CHANCE),
    3: dict(rows=TEST_AMOUNT, cols=TEST_AMOUNT, speed=ENEMY_SPEED, shoot_chance=ENEMY_SHOOT_CHANCE),
    4: dict(rows=TEST_AMOUNT, cols=TEST_AMOUNT, speed=ENEMY_SPEED, shoot_chance=ENEMY_SHOOT_CHANCE),
    5: dict(rows=TEST_AMOUNT, cols=TEST_AMOUNT, speed=ENEMY_SPEED, shoot_chance=ENEMY_SHOOT_CHANCE),
}

# Mini‑boss per level – health can be changed later
FIST_SETTINGS = {
    "cooldown": 120,  # frames between fist launches
    "speed": 4,       # movement speed of launched fists
    "damage": 1,
}

# Additional fist visual‑cue settings
FIST_CHARGE_TIME = 30                     # frames the fist swings & flashes
FIST_FLASH_COLORS = [(255, 255, 255), (255, 0, 0)]  # white ↔ red
FIST_FLASH_INTERVAL = 5                  # frames per colour before toggling

MINIBOSS_SETTINGS = {
    1: dict(health=3, speed=2),
    2: dict(health=3, speed=2),
    3: dict(health=3, speed=2),
    4: dict(health=3, speed=2),
    5: dict(health=3, speed=2),
}

# Background settings

# Planet assets – indexed by transition count (planet_0.png, planet_1.png, ...)
PLANET_PATTERN = "assets/planets/planet_{idx}.png"
# Scroll factor for planets (relative to background layer 0 scroll)
PLANET_SCROLL_FACTOR = 0.05  # slower planet scroll relative to background layer 0
# Global size scaling factor for all planets (1.0 = original size)
PLANET_SCALE = 2

# Parallax background configuration
# Naming pattern for per‑level layers (four layers per level)
LEVEL_BACKGROUND_PATTERN = "assets/background/background_level_1_layer_{layer}.png"

#LEVEL_BACKGROUND_PATTERN = "assets/background/background_level_{level}_layer_{layer}.png"
# Naming pattern for transition background (four layers)
TRANSITION_BACKGROUND_PATTERN = "assets/background/transition_layer_{layer}.png"
# Number of layers per background
PARALLAX_LAYERS = 4
# Speed multipliers for each layer (0 = foreground, highest speed)
PARALLAX_SPEED_FACTORS = [0, 0.05, 0.06, 0.07]
# Initial vertical offset for scrolling
INITIAL_SCROLL = 0
# Base scroll speed – multiplied by each layer's factor
BASE_SCROLL_SPEED = 2
# Transition display duration (in frames) – 5 seconds at the game's FPS
TRANSITION_FRAMES = 8 * FPS
# New transition‑speed configuration
AMPLIFY_STEP = 0.4               # per‑frame increase while amplifying
DECEL_STEP = 0.1             # per‑frame decrease while decelerating
AMPLIFY_MAX_FACTOR = 50          # peak speed factor during amplify phase
THRESHOLD_FACTOR = 40            # speed factor used during the hold phase
TRANSITION_HOLD_FRAMES = 3 * FPS  # hold transition background for 3 seconds
# Keep legacy names for compatibility (if any other code still uses them)
SCROLL = INITIAL_SCROLL
BACKGROUND_SCROLL_SPEED = BASE_SCROLL_SPEED

# --- PowerUp & Comet Settings ---
# Gesamte Drop-Wahrscheinlichkeit liegt bei ca. 22% pro normalem Gegner
POWERUP_DROP_CHANCES = {
    "comet": 0.02,        # 5%
    "bunker": 0.02,       # 2%
    "hp": 0.01,           # 2%
    "speed": 0.03,        # 5%
    "doubleshot": 0.03,   # 5%
    "trippleshot": 0.03   # 3%
}
POWERUP_FALL_SPEED = 4

COMET_SPEED = 8
COMET_ROTATION_SPEED = 2
TIE_FIGHTER_SPEED = 14
TIE_FIGHTER_ROTATION_SPEED = 0.5
TIE_FIGHTER_SIZE = 128

# Dauer und Stärke der Spieler-Buffs
POWERUP_SPEED_MULTIPLIER = 1.5   # 50% schneller
POWERUP_SPEED_DURATION = 5       # in Sekunden
POWERUP_DOUBLESHOT_DURATION = 5  # in Sekunden
POWERUP_TRIPLESHOT_DURATION = 5  # in Sekunden