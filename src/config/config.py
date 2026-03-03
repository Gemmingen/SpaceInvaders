
# Game configuration settings


SCREEN_WIDTH = 800                                  #800 Original size, not for Arcade Version
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
TEST_AMOUNT = 5

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
SCROLL = 1                                           # Initial scroll position for background
BACKGROUND_SCROLL_SPEED = 2                          # pixels per frame for background scrolling

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