"""BossSmall4 – player‑chasing drone with laser attack.

Appears on level 4. Continuously moves toward the player and fires a laser
(sprite ``boss-attack2.png``) toward the player every ``attack_cooldown``
frames.
"""
import pygame
import math
from src.config.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.game.miniboss_base import MiniBossBase
from src.game.explosion import Explosion

class BossClone(pygame.sprite.Sprite):
    """Die 'Kinder' des Bosses. Sie umkreisen ihn und greifen dann an."""
    def __init__(self, owner, angle_offset):
        super().__init__()
        img = pygame.image.load('assets/boss-small4.png').convert_alpha()
        self.image_base = pygame.transform.scale(img, (40, 40))
        self.image = self.image_base.copy()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        
        self.owner = owner
        self.angle = angle_offset
        self.radius = 80
        self.health = 2 # Anzahl der Schüsse, die ein Klon aushält
        self.damage = 1 # Schaden am Spieler oder Bunker
        
        # Status-Management
        self.state = "orbiting" # orbiting | charging | launched
        self.charge_timer = 0
        self.flash_timer = 0
        self.flash_index = 0
        self.velocity = pygame.math.Vector2(0, 0)
        self.exact_x = 0.0
        self.exact_y = 0.0
        self.speed = 8

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
                    exp = Explosion(self.rect.centerx, self.rect.centery, size=64)
                    self.explosions_group.add(exp)
                    
                    if getattr(self, 'all_sprites_group', None) is not None:
                        self.all_sprites_group.add(exp)
                        
        super().kill()

    def start_charge(self):
        self.state = "charging"
        self.charge_timer = 40 # Frames zum Blinken
        self.flash_timer = 5

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
        # Da der Klon sowohl in miniboss_group als auch in enemy_bullets ist, 
        # verhindern wir ein doppeltes Update pro Frame durch Überprüfen der kwargs
        if not kwargs: 
            return
            
        if 'explosions' in kwargs:
            self.explosions_group = kwargs['explosions']
        if 'all_sprites' in kwargs:
            self.all_sprites_group = kwargs['all_sprites']

        if self.state == "orbiting":
            self.angle += 0.05
            self.rect.centerx = self.owner.rect.centerx + math.cos(self.angle) * self.radius
            self.rect.centery = self.owner.rect.centery + math.sin(self.angle) * self.radius
            
        elif self.state == "charging":
            self.flash_timer -= 1
            if self.flash_timer <= 0:
                self.flash_timer = 5
                self.flash_index = (self.flash_index + 1) % 2
                color = (255, 0, 0) if self.flash_index == 0 else (255, 255, 255)
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
        self.rect.center = (SCREEN_WIDTH // 2, 200)
        
        self.center_pos = pygame.math.Vector2(SCREEN_WIDTH // 2, 250)
        self.t = 0.0
        self.max_routes = 2
        
        self.state = self.STATE_FLYING
        self.children = pygame.sprite.Group()
        self.attack_queue = []
        self.launch_delay = 0

    def spawn_children(self):
        for i in range(6):
            angle = (2 * math.pi / 6) * i
            child = BossClone(self, angle)
            self.children.add(child)
            # Kinder in die gleichen Gruppen pushen wie den Boss (macht sie für den Spieler abknallbar!)
            for group in self.groups():
                group.add(child)

    def update(self, player=None, *args, **kwargs):
        enemy_bullets = kwargs.get('enemy_bullets')

        if self.state == self.STATE_FLYING:
            target_t = 2 * math.pi * self.max_routes
            remaining = target_t - self.t
            
            # Halb so schnell wie vorher (Base Speed auf 0.04 gesetzt)
            base_speed = 0.03
            
            # Sehr weiches "Smooth Easing" im letzten Halbbogen (pi) vor dem Anhalten
            if remaining < math.pi:
                ratio = remaining / math.pi
                speed = max(0.020, base_speed * math.sin(ratio * math.pi / 2))
            else:
                speed = base_speed
            
            self.t += speed
            if self.t >= target_t:
                self.t = target_t
                self.state = self.STATE_SPAWNING

            self.rect.centerx = self.center_pos.x + 350 * math.sin(self.t)
            self.rect.centery = self.center_pos.y + 100 * math.sin(2 * self.t)
        
        elif self.state == self.STATE_SPAWNING:
            self.rect.center = self.center_pos
            self.spawn_children()
            self.state = self.STATE_ORBITING
            self.t = 0

        elif self.state == self.STATE_ORBITING:
            self.t += 0.05 
            if self.t >= 2 * math.pi:
                self.state = self.STATE_ATTACKING
                self.attack_queue = self.children.sprites()
                for child in self.attack_queue:
                    child.start_charge()
                self.launch_delay = 30

        elif self.state == self.STATE_ATTACKING:
            if self.attack_queue:
                self.launch_delay -= 1
                if self.launch_delay <= 0:
                    child = self.attack_queue.pop(0)
                    if child.alive() and player:
                        child.launch(player.rect.center, enemy_bullets)
                    self.launch_delay = 15
            
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