# Game configuration settings

# Vollbild-Steuerung
FULLSCREEN_ENABLED = True 

# Interne Auflösung des Spielfelds
SCREEN_WIDTH = 1080                                  
SCREEN_HEIGHT = 1080 

FPS = 60

# Bonus UFO (Mystery Ship) configuration
UFO_SPAWN_HEIGHT_OPTIONS = [80, 300, 800]           # possible vertical spawn positions for the UFO
UFO_SPEED_OPTIONS = [3, 7, 10]                      # possible speeds for the UFO
UFO_SPAWN_TIME = 15                                 # seconds before a UFO may appear
UFO_SCORE_OPTIONS = [1200, 1312, 1500, 1600, 1800]  # possible bonus points
UFO_SHOT_THRESHOLD = 30                             # number of player shots trigger

# Player Settings
PLAYER_SPEED = 5

# Enemy Settings
ENEMY_SPEED = 3
ENEMY_SHOOT_CHANCE = 0.001                           
BULLET_SPEED = 10

# Enemy wave per level
TEST_AMOUNT = 1
TEST_START_LEVEL = 3
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
FIST_SETTINGS = {
    "cooldown": 120,  
    "speed": 4,       
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
    5: dict(health=3, speed=2),
}

# Background settings
PLANET_PATTERN = "assets/planets/planet_{idx}.png"
PLANET_SCROLL_FACTOR = 1  
PLANET_SCALE = 1

# Parallax background
LEVEL_BACKGROUND_PATTERN = "assets/background/background_level_1_layer_{layer}.png"
TRANSITION_BACKGROUND_PATTERN = "assets/background/transition_layer_{layer}.png"
PARALLAX_LAYERS = 4
PARALLAX_SPEED_FACTORS = [0, 0.05, 0.06, 0.07] 
INITIAL_SCROLL = 0
BASE_SCROLL_SPEED = 2
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
    "comet": 0.02,        
    "bunker": 0.02,       
    "hp": 0.01,           
    "speed": 0.03,        
    "doubleshot": 0.03,   
    "trippleshot": 0.03   
}
POWERUP_FALL_SPEED = 4

COMET_SPEED = 8
COMET_ROTATION_SPEED = 2
TIE_FIGHTER_SPEED = 14
TIE_FIGHTER_ROTATION_SPEED = 0.5
TIE_FIGHTER_SIZE = 128

POWERUP_SPEED_MULTIPLIER = 1.5   
POWERUP_SPEED_DURATION = 5       
POWERUP_DOUBLESHOT_DURATION = 5  
POWERUP_TRIPLESHOT_DURATION = 5  

# BossSmall2 Settings
BOSS2_LASER_SPRITE = "assets/laser-element.png"
BOSS2_LASER_SPRITE_WIDTH = 25
BOSS2_CHARGE_FRAMES = 60  

BOSS2_MOVE_DURATION = 5
BOSS2_FLASH_DURATION = 1
BOSS2_ORB_ARC_DURATION = 1
BOSS2_ORB_Y_PERCENT = 0.25
BOSS2_LASER_SPAWN_INTERVAL = 1.2
BOSS2_LASER_COUNT = 5
BOSS2_LASER_SPEED = 5

BOSS2_SIDE_LASER_SPRITE = "assets/downward-laser.png"
BOSS2_SIDE_LASER_SPEED = BOSS2_LASER_SPEED  
BOSS2_SIDE_LASER_PAUSE_FRAMES = BOSS2_CHARGE_FRAMES  
BOSS2_SIDE_LASER_OFFSET = 0  
BOSS2_GAP_WIDTH_MULTIPLIER = 3.0
BOSS2_GAP_RANDOM_RANGE = 100
BOSS2_LASER_X_OFFSET = 50
BOSS2_LASER_ORB_MARGIN = 4
BOSS2_LASER_BUILD_INTERVAL = 0.1  
BOSS2_LASER_PAUSE_FRAMES = int(60 * 0.05)