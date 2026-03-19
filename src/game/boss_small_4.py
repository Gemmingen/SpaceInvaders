"""BossSmall4 – player‑chasing drone with laser attack.

Appears on level 4. Continuously moves toward the player and fires a laser
(sprite ``boss-attack2.png``) toward the player every ``attack_cooldown``
frames.
"""
import pygame
import math
from src.config.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BOSS4_CLONE_SIZE, BOSS4_CLONE_RADIUS, BOSS4_CLONE_HEALTH,
    BOSS4_CLONE_DAMAGE, BOSS4_CLONE_SPEED, BOSS4_CLONE_EXPLOSION_SIZE,
    BOSS4_CLONE_CHARGE_TIME, BOSS4_CLONE_FLASH_INTERVAL, BOSS4_CLONE_ORBIT_SPEED,
    BOSS4_FLASH_COLOR_1, BOSS4_FLASH_COLOR_2,
    BOSS4_START_Y, BOSS4_CENTER_Y, BOSS4_MAX_ROUTES, BOSS4_CHILDREN_COUNT,
    BOSS4_BASE_SPEED, BOSS4_MIN_SPEED, BOSS4_FLIGHT_AMP_X, BOSS4_FLIGHT_AMP_Y,
    BOSS4_FREQ_MULT_Y, BOSS4_ORBIT_T_STEP, BOSS4_LAUNCH_INITIAL_DELAY, BOSS4_LAUNCH_DELAY
)
from src.game.miniboss_base import MiniBossBase
from src.game.explosion import Explosion

class BossClone(pygame.sprite.Sprite):
    """Die 'Kinder' des Bosses. Sie umkreisen ihn und greifen dann an."""
    def __init__(self, owner, angle_offset):
        super().__init__()
        img = pygame.image.load('assets/boss-small4.png').convert_alpha()
        self.image_base = pygame.transform.scale(img, BOSS4_CLONE_SIZE)
        self.image = self.image_base.copy()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        
        self.owner = owner
        self.angle = angle_offset
        self.radius = BOSS4_CLONE_RADIUS
        self.health = BOSS4_CLONE_HEALTH # Anzahl der Schüsse, die ein Klon aushält
        self.damage = BOSS4_CLONE_DAMAGE # Schaden am Spieler oder Bunker
        
        # Status-Management
        self.state = "orbiting" # orbiting | charging | launched
        self.charge_timer = 0
        self.flash_timer = 0
        self.flash_index = 0
        self.velocity = pygame.math.Vector2(0, 0)
        self.exact_x = 0.0
        self.exact_y = 0.0
        self.speed = BOSS4_CLONE_SPEED

        self.explosions_group = None
        self.all_sprites_group = None
        self.silent_kill = False
        self._killed = False

    def hit(self):
        # Wird getriggert, wenn der Spieler auf den Klon schießt
        self.health -= 1
        if self.health <= 0:
            self.kill()

    def kill(self):
        # Override: Wenn die Engine kill() ruft, spawnt hier garantiert die Explosion!
        if not getattr(self, '_killed', False):
            self._killed = True
            
            if not getattr(self, 'silent_kill', False):
                if getattr(self, 'explosions_group', None) is not None:
                    exp = Explosion(self.rect.centerx, self.rect.centery, size=BOSS4_CLONE_EXPLOSION_SIZE)
                    self.explosions_group.add(exp)
                    
                    if getattr(self, 'all_sprites_group', None) is not None:
                        self.all_sprites_group.add(exp)
                        
        super().kill()

    def start_charge(self):
        self.state = "charging"
        self.charge_timer = BOSS4_CLONE_CHARGE_TIME # Frames zum Blinken
        self.flash_timer = BOSS4_CLONE_FLASH_INTERVAL

    def launch(self, target_pos, enemy_bullets_group):
        self.state = "launched"
        # Normales Bild ohne Rand laden
        self.image = self.image_base.copy()
        self.mask = pygame.mask.from_surface(self.image)
        
        self.exact_x = float(self.rect.centerx)
        self.exact_y = float(self.rect.centery)
        
        # Flugvektor einmalig berechnen
        direction = pygame.math.Vector2(target_pos) - pygame.math.Vector2(self.rect.center)
        if direction.length() > 0:
            self.velocity = direction.normalize() * self.speed
        else:
            self.velocity = pygame.math.Vector2(0, self.speed)
            
        # Klon in die globalen Gegnerkugeln aufnehmen -> Main-Loop regelt ab jetzt den Schaden!
        if enemy_bullets_group is not None:
            enemy_bullets_group.add(self)

    def update(self, player=None, *args, **kwargs):
        # Verhindert doppelten Aufruf durch all_sprites.update()
        if player is None and not args and not kwargs:
            return
            
        # Akzeptiert Keywords ODER die unbenannten Argumente aus deinem Merge!
        if 'explosions' in kwargs:
            self.explosions_group = kwargs['explosions']
        elif len(args) >= 3:
            self.explosions_group = args[2]

        if 'all_sprites' in kwargs:
            self.all_sprites_group = kwargs['all_sprites']
        elif len(args) >= 1:
            self.all_sprites_group = args[0]

        if self.state == "orbiting":
            self.angle += BOSS4_CLONE_ORBIT_SPEED
            self.rect.centerx = round(self.owner.rect.centerx + math.cos(self.angle) * self.radius)
            self.rect.centery = round(self.owner.rect.centery + math.sin(self.angle) * self.radius)
            
        elif self.state == "charging":
            self.flash_timer -= 1
            if self.flash_timer <= 0:
                self.flash_timer = BOSS4_CLONE_FLASH_INTERVAL
                self.flash_index = (self.flash_index + 1) % 2
                color = BOSS4_FLASH_COLOR_1 if self.flash_index == 0 else BOSS4_FLASH_COLOR_2
                new_img = self.image_base.copy()
                pygame.draw.rect(new_img, color, new_img.get_rect(), 2)
                self.image = new_img
                self.mask = pygame.mask.from_surface(self.image)
            
            self.charge_timer -= 1

        elif self.state == "launched":
            # Float-Präzision für sauberen Diagonalflug
            self.exact_x += self.velocity.x
            self.exact_y += self.velocity.y
            self.rect.centerx = int(self.exact_x)
            self.rect.centery = int(self.exact_y)
            
            # Außerhalb des Screens lautlos löschen (ohne Explosion)
            if not pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).colliderect(self.rect):
                self.silent_kill = True
                self.kill()


class BossSmall4(MiniBossBase):
    STATE_FLYING = "flying"
    STATE_SPAWNING = "spawning"
    STATE_ORBITING = "orbiting"
    STATE_ATTACKING = "attacking"

    def __init__(self, health=15, speed=2):
        super().__init__('assets/boss-small4.png', health, speed)
        self.rect.center = (SCREEN_WIDTH // 2, BOSS4_START_Y)
        
        self.center_pos = pygame.math.Vector2(SCREEN_WIDTH // 2, BOSS4_CENTER_Y)
        self.t = 0.0
        self.max_routes = BOSS4_MAX_ROUTES
        
        self.state = self.STATE_FLYING
        self.children = pygame.sprite.Group()
        self.attack_queue = []
        self.launch_delay = 0

    def spawn_children(self):
        for i in range(BOSS4_CHILDREN_COUNT):
            angle = (2 * math.pi / BOSS4_CHILDREN_COUNT) * i
            child = BossClone(self, angle)
            self.children.add(child)
            # Kinder in die gleichen Gruppen pushen wie den Boss (macht sie für den Spieler abknallbar!)
            for group in self.groups():
                group.add(child)

    def update(self, player=None, *args, **kwargs):
        # WICHTIG: Verhindert doppeltes Update durch den Call aus `all_sprites.update()`!
        if player is None and not args and not kwargs:
            return
            
        # Akzeptiert Keywords ODER die unbenannten Argumente aus deinem Merge!
        enemy_bullets = kwargs.get('enemy_bullets')
        if enemy_bullets is None and len(args) >= 2:
            enemy_bullets = args[1]

        if self.state == self.STATE_FLYING:
            target_t = 2 * math.pi * self.max_routes
            remaining = target_t - self.t
            
            # Basisgeschwindigkeit
            base_speed = BOSS4_BASE_SPEED
            
            # Sehr weiches "Smooth Easing" im letzten Halbbogen (pi) vor dem Anhalten
            if remaining < math.pi:
                ratio = remaining / math.pi
                speed = max(BOSS4_MIN_SPEED, base_speed * math.sin(ratio * math.pi / 2))
            else:
                speed = base_speed
            
            self.t += speed
            if self.t >= target_t:
                self.t = target_t
                self.state = self.STATE_SPAWNING

            self.rect.centerx = self.center_pos.x + BOSS4_FLIGHT_AMP_X * math.sin(self.t)
            self.rect.centery = self.center_pos.y + BOSS4_FLIGHT_AMP_Y * math.sin(BOSS4_FREQ_MULT_Y * self.t)
        
        elif self.state == self.STATE_SPAWNING:
            self.rect.center = self.center_pos
            self.spawn_children()
            self.state = self.STATE_ORBITING
            self.t = 0

        elif self.state == self.STATE_ORBITING:
            self.t += BOSS4_ORBIT_T_STEP 
            if self.t >= 2 * math.pi:
                self.state = self.STATE_ATTACKING
                self.attack_queue = self.children.sprites()
                for child in self.attack_queue:
                    child.start_charge()
                self.launch_delay = BOSS4_LAUNCH_INITIAL_DELAY

        elif self.state == self.STATE_ATTACKING:
            if self.attack_queue:
                self.launch_delay -= 1
                if self.launch_delay <= 0:
                    child = self.attack_queue.pop(0)
                    if child.alive() and player:
                        child.launch(player.rect.center, enemy_bullets)
                    self.launch_delay = BOSS4_LAUNCH_DELAY
            
            if len(self.children) == 0:
                self.state = self.STATE_FLYING
                self.t = 0

    def hit(self):
        # Boss ist UNVERWUNDBAR, solange er Kinder spawnt oder diese existieren
        if self.state != self.STATE_FLYING:
            return 
            
        # Normaler Schaden, wenn im Flugmodus
        self.health -= 1
        if self.health <= 0:
            for child in self.children:
                child.silent_kill = True # Beim Tod des Bosses verschwinden noch kreisende Kinder lautlos
                child.kill()
            self.kill()