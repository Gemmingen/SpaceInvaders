SCREEN_WIDTH = 800 #800
SCREEN_HEIGHT = 1080 #600 
FPS = 60
# Bonus UFO (Mystery Ship) configuration
UFO_SPAWN_HEIGHT_OPTIONS = [80, 300, 800] # possible vertical spawn positions for the UFO (in pixels from top)
UFO_SPEED_OPTIONS = [3, 7, 10]  # possible speeds for the UFO (pixels per frame)
UFO_SPAWN_TIME = 15  # seconds before a UFO may appear
#UFO_SPEED = 3        # horizontal speed of the UFO (pixels per frame)
UFO_SCORE_OPTIONS = [1200, 1312, 1500, 1600, 1800]  # possible bonus points
UFO_SHOT_THRESHOLD = 30  # number of player shots that can also trigger a UFO
PLAYER_SPEED = 5
ENEMY_SPEED = 3
ENEMY_SHOOT_CHANCE = 0.001  # Chance per frame that an enemy will shoot (adjust for difficulty)
BULLET_SPEED = 10

SCROLL = 1 # Initial scroll position for background
BACKGROUND_SCROLL_SPEED = 2 # pixels per frame for background scrolling