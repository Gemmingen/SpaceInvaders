# Game configuration settings

# Vollbild-Steuerung
FULLSCREEN_ENABLED = True 

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
TEST_AMOUNT = 3
TEST_START_LEVEL = 1
ENEMY_WAVE_SETTINGS = {
    1: dict(rows=TEST_AMOUNT, cols=TEST_AMOUNT, speed=ENEMY_SPEED, shoot_chance=ENEMY_SHOOT_CHANCE),
    2: dict(rows=TEST_AMOUNT, cols=TEST_AMOUNT, speed=ENEMY_SPEED, shoot_chance=ENEMY_SHOOT_CHANCE),
    3: dict(rows=TEST_AMOUNT, cols=TEST_AMOUNT, speed=ENEMY_SPEED, shoot_chance=ENEMY_SHOOT_CHANCE),
    4: dict(rows=TEST_AMOUNT, cols=TEST_AMOUNT, speed=ENEMY_SPEED, shoot_chance=ENEMY_SHOOT_CHANCE),
    5: dict(rows=TEST_AMOUNT, cols=TEST_AMOUNT, speed=ENEMY_SPEED, shoot_chance=ENEMY_SHOOT_CHANCE),
}

# Mini‑boss per level – health can be changed later

# BossSmall3 split settings
BOSS3_GLOB_SPLIT_ANGLE_DEGREES = 10          # degrees offset for side bullets (±10°)
BOSS3_GLOB_SPLIT_HEIGHT = SCREEN_HEIGHT // 2  # y‑position where the bullet splits
BOSS3_POISON_PUDDLE_FRAME_SKIP = 3
BOSS3_POISON_PUDDLE_ANIMATION_SPEED = 1
BOSS3_POISON_PUDDLE_SIZE = (1000, 1000)

FIST_SETTINGS = {
    "cooldown": 120,  # frames between fist launches
    "speed": 4,       # movement speed of launched fists
    "damage": 1,
}

# Additional fist visual‑cue settings (BOSS 1 only)
FIST_CHARGE_TIME = 30                     # frames the fist swings & flashes
FIST_FLASH_COLORS = [(255, 255, 255), (255, 0, 0)]  # white ↔ red
FIST_FLASH_INTERVAL = 5                  # frames per colour before toggling

MINIBOSS_SETTINGS = {
    1: dict(health=3, speed=2),
    2: dict(health=3, speed=2),
    3: dict(health=3, speed=2),
    4: dict(health=3, speed=2),
    5: dict(health=10, speed=3), # Gebuffter Endboss
}

# Background settings

# Planet assets – indexed by transition count (planet_0.png, planet_1.png, ...)
PLANET_PATTERN = "assets/planets/planet_{idx}.png"
# Scroll factor for planets (relative to background layer 0 scroll)
PLANET_SCROLL_FACTOR = 1  # slower planet scroll relative to background layer 0
# Global size scaling factor for all planets (1.0 = original size)
PLANET_SCALE = 1

# Parallax background configuration
# Naming pattern for per‑level layers (four layers per level)
LEVEL_BACKGROUND_PATTERN = "assets/background/background_level_1_layer_{layer}.png"

#LEVEL_BACKGROUND_PATTERN = "assets/background/background_level_{level}layer{layer}.png"
# Naming pattern for transition background (four layers)
TRANSITION_BACKGROUND_PATTERN = "assets/background/transition_layer_{layer}.png"
# Number of layers per background
PARALLAX_LAYERS = 4
# Speed multipliers for each layer (0 = foreground, highest speed)
PARALLAX_SPEED_FACTORS = [0, 0.05, 0.06, 0.07] #[Layer0, Layer1, ...]
# Initial vertical offset for scrolling
INITIAL_SCROLL = 0
# Base scroll speed – multiplied by each layer's factor
BASE_SCROLL_SPEED = 2
# Transition display duration (in frames) – 5 seconds at the game's FPS
TRANSITION_FRAMES = 8 * FPS
# New transition‑speed configuration
AMPLIFY_STEP = 0.4               # per‑frame increase while amplifying
DECEL_STEP = 0.2            # per‑frame decrease while decelerating
AMPLIFY_MAX_FACTOR = 50          # peak speed factor during amplify phase
THRESHOLD_FACTOR = 40            # speed factor used during the hold phase
TRANSITION_HOLD_FRAMES = 3 * FPS  # hold transition background for 3 seconds
# Keep legacy names for compatibility (if any other code still uses them)
SCROLL = INITIAL_SCROLL
BACKGROUND_SCROLL_SPEED = BASE_SCROLL_SPEED

# --- PowerUp & Comet Settings ---
# Gesamte Drop-Wahrscheinlichkeit liegt bei ca. 22% pro normalem Gegner
POWERUP_DROP_CHANCES = {
    "comet": 1,        # 5%
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

# BossSmall2 (Level 2) Attack Pattern Settings

BOSS2_LASER_SPRITE = "assets/laser-element.png"
BOSS2_LASER_SPRITE_WIDTH = 25
BOSS2_CHARGE_FRAMES = 60  # 1 second at 60 FPS

BOSS2_MOVE_DURATION = 5
BOSS2_FLASH_DURATION = 1
BOSS2_ORB_ARC_DURATION = 1
BOSS2_ORB_Y_PERCENT = 0.25
BOSS2_LASER_SPAWN_INTERVAL = 1.2
BOSS2_LASER_COUNT = 5
BOSS2_LASER_SPEED = 5

# Side‑laser configuration – these lasers sit on the centre of each orb
BOSS2_SIDE_LASER_SPRITE = "assets/downward-laser.png"
BOSS2_SIDE_LASER_SPEED = BOSS2_LASER_SPEED  # same downward speed as the main laser
BOSS2_SIDE_LASER_PAUSE_FRAMES = BOSS2_CHARGE_FRAMES  # pause before moving, same as main laser
BOSS2_SIDE_LASER_OFFSET = 0  # horizontal offset when centering on orb (0 = exact centre)
BOSS2_GAP_WIDTH_MULTIPLIER = 3.0
BOSS2_GAP_RANDOM_RANGE = 100
# Horizontal offset to shift the entire laser line to the right (positive moves right)
BOSS2_LASER_X_OFFSET = 50
# Optional extra margin between laser and orb edges (pixels). Adjust for visual spacing.
BOSS2_LASER_ORB_MARGIN = 4
# Laser build‑up and pause configuration for BossSmall2
BOSS2_LASER_BUILD_INTERVAL = 0.1  # seconds per growth step (adds one sprite width each step)
# Tiny pause after the laser is fully built before it starts moving downward
BOSS2_LASER_PAUSE_FRAMES = int(FPS * 0.05)  # ~3 frames at 60 FPS (≈0.05 s)

# --- EndBoss Settings ---
ENDBOSS_WIDTH = 160                # Bessere Proportionen (nicht mehr gestaucht)
ENDBOSS_HEIGHT = 130
ENDBOSS_PHASE_DURATION = 120       # Kürzere Phasen = Schnellere Patternwechsel (120 Frames = 2 Sek)
ENDBOSS_ATTACK_COOLDOWN = 30       # Sehr kurzes Delay ZWISCHEN den 4 Schüssen in der Mitte
ENDBOSS_PROJECTILE_SPEED = 6
ENDBOSS_PROJECTILE_SPLIT_ANGLE = 35 # Winkel der Teilung nach Abprallen
ENDBOSS_RANDOM_SHOOT_MIN = 60      # Min-Delay für Schüsse während des Fliegens
ENDBOSS_RANDOM_SHOOT_MAX = 150     # Max-Delay für Schüsse während des Fliegens

# EndBoss Animation & Projektile
ENDBOSS_PROJ_SIZE_LARGE = (24, 48)
ENDBOSS_PROJ_SIZE_SMALL = (12, 24)
ENDBOSS_EXPLOSION_SIZE = 48
ENDBOSS_SPAWNER_SIZE = 300
ENDBOSS_SPAWN_FRAMES = 60          # Frames pro Spawn-Phase (60 Warten, 60 Zoom)
ENDBOSS_SPAWNER_ROT_SPEED = 6      # Rotationsgeschwindigkeit des Spawner-Portals

# EndBoss Pattern / Bewegungsvariablen
ENDBOSS_BURSTS_PER_CYCLE = 4       # Anzahl der Salven im Zentrum
ENDBOSS_EASING_SPEED = 0.08        # Weichheit der Bewegungen (kleiner = weicher)
ENDBOSS_CENTER_Y = 250             # Y-Mittelpunkt für Kreise/Achten
ENDBOSS_TOP_Y = 150                # Y-Zielpunkt für das Pendel-Pattern und Zentrum
ENDBOSS_PATTERN_AMP_X = 250        # X-Amplitude für das Kreisen
ENDBOSS_PATTERN_AMP_Y = 100        # Y-Amplitude für das Kreisen
ENDBOSS_PATTERN_WIDE_X = 350       # X-Amplitude für weite Bewegungen (Pendeln, Welle)
ENDBOSS_FREQ_MULT_X = 0.8          # Frequenz-Faktor X für weite Bewegungen
ENDBOSS_FREQ_MULT_Y1 = 2.0         # Frequenz-Faktor Y für Wellen-Muster
ENDBOSS_FREQ_MULT_Y2 = 1.6         # Frequenz-Faktor Y für 8er-Muster
ENDBOSS_TIME_STEP = 0.05           # Geschwindigkeit der internen Pattern-Zeit
ENDBOSS_CENTER_TOLERANCE = 20      # Erlaubte Abweichung in Pixeln vom Zentrum

# EndBoss Rohre (Position und Schusswinkel)
ENDBOSS_PIPE_X_OFFSET_PCT = 0.2    # Eingerückt um 20% von den Rändern
ENDBOSS_PIPE_Y_OFFSET = 10         # Nach oben verschoben
ENDBOSS_PIPE_ANGLES = (90, 135, 45)# Unten Mitte, Diagonal Links, Diagonal Rechts

# --- BossSmall4 Settings ---
BOSS4_CLONE_SIZE = (40, 40)
BOSS4_CLONE_RADIUS = 80
BOSS4_CLONE_HEALTH = 2
BOSS4_CLONE_DAMAGE = 1
BOSS4_CLONE_SPEED = 8
BOSS4_CLONE_EXPLOSION_SIZE = 64
BOSS4_CLONE_CHARGE_TIME = 40
BOSS4_CLONE_FLASH_INTERVAL = 5
BOSS4_CLONE_ORBIT_SPEED = 0.05
BOSS4_FLASH_COLOR_1 = (255, 0, 0)
BOSS4_FLASH_COLOR_2 = (255, 255, 255)

BOSS4_START_Y = 200
BOSS4_CENTER_Y = 250
BOSS4_MAX_ROUTES = 2
BOSS4_CHILDREN_COUNT = 6
BOSS4_BASE_SPEED = 0.03
BOSS4_MIN_SPEED = 0.020
BOSS4_FLIGHT_AMP_X = 350
BOSS4_FLIGHT_AMP_Y = 100
BOSS4_FREQ_MULT_Y = 2
BOSS4_ORBIT_T_STEP = 0.05
BOSS4_LAUNCH_INITIAL_DELAY = 30
BOSS4_LAUNCH_DELAY = 15

# --- Player & Boost Settings ---
PLAYER_PATCH_COLOR = (40, 40, 40)
PLAYER_PATCH_RECT = (10, 10, 12, 12)
PLAYER_BOOST_NORMAL_SIZE = (16, 24)
PLAYER_HYPERBOOST_SIZE = (76, 56)
PLAYER_HYPERBOOST_ANIMATION_DELAY = 4
PLAYER_HYPERBOOST_PROGRESS_UP = 0.05
PLAYER_HYPERBOOST_PROGRESS_DOWN = 0.08
PLAYER_HYPERBOOST_OVERLAP_BASE = 5
PLAYER_HYPERBOOST_OVERLAP_MULT = 8

# --- Bunker Settings ---
BUNKER_SIZE = (96, 96)
BUNKER_MAX_HEALTH = 15
BUNKER_DMG1_THRESHOLD = 10
BUNKER_DMG2_THRESHOLD = 5
BUNKER_ALPHA_THRESHOLD = 128
BUNKER_SHAKE_FRAMES = 12
BUNKER_FLASH_FRAMES = 12
BUNKER_SHAKE_PIXELS = 4
BUNKER_FLASH_COLOR = (150, 0, 0)

# --- Transition Cinematic Settings ---
TRANSITION_PLAYER_SCALE_MAX = 1.8
TRANSITION_PLAYER_SCALE_NORMAL = 1.0
TRANSITION_PLAYER_SCALE_EASING = 0.05

TRANSITION_BUNKER_Y_DOWN = 250.0
TRANSITION_BUNKER_Y_UP = 0.0
TRANSITION_BUNKER_EASING = 0.05

TRANSITION_PLAYER_Y_AMPLIFY_PCT = 0.2
TRANSITION_PLAYER_Y_HOLD_PCT = 0.5
TRANSITION_PLAYER_Y_NORMAL_OFFSET = 46

TRANSITION_PLAYER_EASING_UP = 0.03
TRANSITION_PLAYER_EASING_DOWN = 0.02
TRANSITION_PLAYER_EASING_RETURN = 0.04
TRANSITION_PLAYER_EASING_PLAYING = 0.08

FIST_EXPLOSION_OFFSET_LARGE = 25
FIST_EXPLOSION_OFFSET_SMALL = 10
FIST_EXPLOSION_SIZE_LARGE = 64
FIST_EXPLOSION_SIZE_SMALL = 32