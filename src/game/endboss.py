"""EndBoss – final level boss (level 5).

Durchläuft nacheinander die Flugmuster der ersten 4 Bosse mit extrem
weichen Übergängen (Easing). Besitzt eine aufwendige Intro-Animation
und schießt abprallende, sich teilende Projektile.
"""
import pygame
import math
import random
from src.config.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ENDBOSS_WIDTH, ENDBOSS_HEIGHT,
    ENDBOSS_PHASE_DURATION, ENDBOSS_ATTACK_COOLDOWN,
    ENDBOSS_PROJECTILE_SPEED, ENDBOSS_PROJECTILE_SPLIT_ANGLE,
    ENDBOSS_RANDOM_SHOOT_MIN, ENDBOSS_RANDOM_SHOOT_MAX
)
from src.game.miniboss_base import MiniBossBase
from src.game.explosion import Explosion
from src.utils.helpers import load_image

class EndBossProjectile(pygame.sprite.Sprite):
    """Projectile fired by the EndBoss that splits and bounces."""
    def __init__(self, start_pos, angle, split_level, explosions_group, all_sprites_group, enemy_bullets_group, boss_projectiles):
        super().__init__()
        self.split_level = split_level
        self.explosions_group = explosions_group
        self.all_sprites_group = all_sprites_group
        self.enemy_bullets_group = enemy_bullets_group
        self.boss_projectiles = boss_projectiles

        img = load_image('assets/endboss-attack.png').convert_alpha()
        
        # Größenskalierung je nach Teilungs-Level
        if self.split_level == 0:
            self.image_base = pygame.transform.scale(img, (24, 48))
        else:
            self.image_base = pygame.transform.scale(img, (12, 24))
            
        # Rotiert das Sprite visuell in die korrekte Flugrichtung
        self.image = pygame.transform.rotate(self.image_base, -angle + 90)
        self.rect = self.image.get_rect(center=start_pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.speed = ENDBOSS_PROJECTILE_SPEED
        rad = math.radians(angle)
        self.vel_x = math.cos(rad) * self.speed
        self.vel_y = math.sin(rad) * self.speed

        # Float-Präzision für saubere Diagonalen
        self.exact_x = float(self.rect.centerx)
        self.exact_y = float(self.rect.centery)

        self.silent_kill = False
        self._killed = False
        self.damage = 1

    def update(self, *args, **kwargs):
        self.exact_x += self.vel_x
        self.exact_y += self.vel_y
        self.rect.centerx = round(self.exact_x)
        self.rect.centery = round(self.exact_y)

        bounced = False
        
        # Abprallen an den Wänden (Links/Rechts)
        if self.rect.left < 0:
            self.rect.left = 0
            self.exact_x = float(self.rect.centerx)
            self.vel_x *= -1
            bounced = True
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.exact_x = float(self.rect.centerx)
            self.vel_x *= -1
            bounced = True

        # Abprallen an der Decke
        if self.rect.top < 0:
            self.rect.top = 0
            self.exact_y = float(self.rect.centery)
            self.vel_y *= -1
            bounced = True
            
        # Wenn es den unteren Bildschirmrand verlässt -> spurlos löschen
        elif self.rect.top > SCREEN_HEIGHT:
            self.silent_kill = True
            self.kill()

        # Wenn er an einer Wand abgeprallt ist -> teilen!
        if bounced:
            self.bounce_and_split()

    def bounce_and_split(self):
        if self.split_level == 0:
            self._do_split()
            # Bei Wand-Abprall keine Explosion zeichnen, nur lautlos killen (teilt sich ja schon)
            self.silent_kill = True
            self.kill()
        else:
            # 2. Aufprall an einer Wand -> spurlos verschwinden
            self.silent_kill = True
            self.kill()

    def kill(self):
        # Wird gerufen bei Treffer (Spieler/Bunker) oder beim off-screen gehen
        if not getattr(self, '_killed', False):
            self._killed = True
            
            if not getattr(self, 'silent_kill', False):
                # Explosion spawnen, weil er getroffen hat
                if self.explosions_group is not None:
                    exp = Explosion(self.rect.centerx, self.rect.centery, size=48)
                    self.explosions_group.add(exp)
                    if self.all_sprites_group is not None:
                        self.all_sprites_group.add(exp)

                # Beim Treffer auf Spieler/Bunker teilt er sich ebenfalls (falls groß)
                if self.split_level == 0:
                    self._do_split()

        super().kill()

    def _do_split(self):
        # Berechne aktuellen Winkel
        current_angle = math.degrees(math.atan2(self.vel_y, self.vel_x))
        a1 = current_angle + ENDBOSS_PROJECTILE_SPLIT_ANGLE
        a2 = current_angle - ENDBOSS_PROJECTILE_SPLIT_ANGLE

        p1 = EndBossProjectile(self.rect.center, a1, 1, self.explosions_group, self.all_sprites_group, self.enemy_bullets_group, self.boss_projectiles)
        p2 = EndBossProjectile(self.rect.center, a2, 1, self.explosions_group, self.all_sprites_group, self.enemy_bullets_group, self.boss_projectiles)

        # Winziger Push, damit sie nach dem Aufspalten nicht sofort wieder in der selben Wand kleben
        for p in (p1, p2):
            p.exact_x += p.vel_x * 2
            p.exact_y += p.vel_y * 2
            p.rect.centerx = round(p.exact_x)
            p.rect.centery = round(p.exact_y)

            if self.boss_projectiles is not None:
                self.boss_projectiles.add(p)
            if self.all_sprites_group is not None:
                self.all_sprites_group.add(p)
            if self.enemy_bullets_group is not None:
                self.enemy_bullets_group.add(p)


class EndBoss(MiniBossBase):
    STATE_SPAWNING = "spawning"
    STATE_FLYING = "flying"

    def __init__(self, health=50, speed=3):
        super().__init__('assets/endboss.png', health, speed)
        
        # Lade Originalbilder für die Intro-Animation
        self.boss_base = load_image('assets/endboss.png').convert_alpha()
        self.spawner_base = load_image('assets/endboss-spawner.png').convert_alpha()
        
        # Start-Setup (Mitte oben)
        self.center_pos = pygame.math.Vector2(SCREEN_WIDTH // 2, 250)
        self.exact_x = float(self.center_pos.x)
        self.exact_y = float(150)
        
        self.state = self.STATE_SPAWNING
        self.spawn_timer = 0
        
        self.t = 0.0
        self.phase = 1
        self.phase_timer = ENDBOSS_PHASE_DURATION
        
        # Schuss-Logik in Phase 5
        self.bursts_fired = 0
        self.attack_timer = ENDBOSS_ATTACK_COOLDOWN
        
        # Schuss-Logik während der Flug-Runden (Phase 1-4)
        self.random_shoot_timer = random.randint(ENDBOSS_RANDOM_SHOOT_MIN, ENDBOSS_RANDOM_SHOOT_MAX)
        
        self.projectiles = pygame.sprite.Group()

    def update(self, player=None, *args, **kwargs):
        # Absicherung gegen fehlende Parameter
        if player is None and not args and not kwargs:
            return

        enemy_bullets = kwargs.get('enemy_bullets')
        if enemy_bullets is None and len(args) >= 2:
            enemy_bullets = args[1]

        explosions = kwargs.get('explosions')
        if explosions is None and len(args) >= 3:
            explosions = args[2]

        all_sprites = kwargs.get('all_sprites')
        if all_sprites is None and len(args) >= 1:
            all_sprites = args[0]

        # ========================================================
        # 1. INTRO / SPAWN ANIMATION
        # ========================================================
        if self.state == self.STATE_SPAWNING:
            self.spawn_timer += 1
            
            # Erstelle eine durchsichtige Arbeitsfläche (Canvas) für die Animation
            surf = pygame.Surface((400, 400), pygame.SRCALPHA)
            center = (200, 200)
            
            # --- Spawner Logik (0 bis 60 Frames) ---
            # Wächst von 0 auf 100% (300px), rotiert rasend schnell
            spawner_scale = min(1.0, self.spawn_timer / 60.0)
            if spawner_scale > 0:
                spawner_size = int(300 * spawner_scale)
                if spawner_size > 0:
                    spawner_scaled = pygame.transform.scale(self.spawner_base, (spawner_size, spawner_size))
                    # Rotiert anhand der Zeit
                    spawner_rot = pygame.transform.rotate(spawner_scaled, self.spawn_timer * 6)
                    sp_rect = spawner_rot.get_rect(center=center)
                    surf.blit(spawner_rot, sp_rect)
            
            # --- Boss Zoom Logik (60 bis 120 Frames) ---
            # Boss kommt aus der Mitte extrem schnell nach vorne geschossen
            if self.spawn_timer > 60:
                boss_scale = min(1.0, (self.spawn_timer - 60) / 60.0)
                bw = int(ENDBOSS_WIDTH * boss_scale)
                bh = int(ENDBOSS_HEIGHT * boss_scale)
                if bw > 0 and bh > 0:
                    boss_scaled = pygame.transform.scale(self.boss_base, (bw, bh))
                    b_rect = boss_scaled.get_rect(center=center)
                    surf.blit(boss_scaled, b_rect)
            
            self.image = surf
            self.rect = self.image.get_rect(center=(round(self.exact_x), round(self.exact_y)))
            
            # Animation beendet
            if self.spawn_timer >= 120:
                self.state = self.STATE_FLYING
                # Finales, sauberes Boss-Bild ohne Spawner
                self.image = pygame.transform.scale(self.boss_base, (ENDBOSS_WIDTH, ENDBOSS_HEIGHT))
                self.rect = self.image.get_rect(center=(round(self.exact_x), round(self.exact_y)))
                self.mask = pygame.mask.from_surface(self.image)
                
            return # Blockiert alle anderen Aktionen während dem Spawnen!

        # ========================================================
        # 2. NORMALES FLIEGEN & KÄMPFEN
        # ========================================================
        if self.state == self.STATE_FLYING:
            self.t += 0.05 
            
            # Start/Ziel-Koordinaten
            target_x = self.center_pos.x
            target_y = self.center_pos.y

            # --- Flugmuster Phasen (Berechnen nur das MATHEMATISCHE Ziel) ---
            if self.phase == 1:
                # Pattern: Boss 1 (Kreisen)
                target_x = self.center_pos.x + 250 * math.cos(self.t)
                target_y = self.center_pos.y + 100 * math.sin(self.t)
                
            elif self.phase == 2:
                # Pattern: Boss 2 (Pendeln oben)
                target_x = self.center_pos.x + 350 * math.sin(self.t * 0.8)
                target_y = 150
                    
            elif self.phase == 3:
                # Pattern: Boss 3 (Welle)
                target_x = self.center_pos.x + 350 * math.sin(self.t * 0.8)
                target_y = self.center_pos.y - 50 + 100 * math.cos(self.t * 2)
                    
            elif self.phase == 4:
                # Pattern: Boss 4 (8er Bewegung)
                target_x = self.center_pos.x + 350 * math.sin(self.t * 0.8)
                target_y = self.center_pos.y + 100 * math.sin(self.t * 1.6)
                
            elif self.phase == 5:
                # Finales Pattern: Genau im Zentrum stehen
                target_x = self.center_pos.x
                target_y = 150

            # --- SMOOTH EASING ---
            # Der Boss lenkt sanft zu seinem Ziel-Pattern, ohne zu Ruckeln/Zucken!
            easing_speed = 0.08
            self.exact_x += (target_x - self.exact_x) * easing_speed
            self.exact_y += (target_y - self.exact_y) * easing_speed
            
            self.rect.centerx = round(self.exact_x)
            self.rect.centery = round(self.exact_y)

            # --- Schusslogik ---
            if self.phase < 5:
                # Gelegentliche, zufällige Schüsse in Phase 1-4 (1-2 mal pro Pattern)
                self.random_shoot_timer -= 1
                if self.random_shoot_timer <= 0:
                    self.shoot(enemy_bullets, explosions, all_sprites)
                    self.random_shoot_timer = random.randint(ENDBOSS_RANDOM_SHOOT_MIN, ENDBOSS_RANDOM_SHOOT_MAX)
                
                # Timer runterzählen für Phasenwechsel
                self.phase_timer -= 1
                if self.phase_timer <= 0:
                    self.phase += 1
                    self.phase_timer = ENDBOSS_PHASE_DURATION
                    self.t = 0.0 # Reset für saubere Kurvenberechnung
                    
            elif self.phase == 5:
                # Dauerfeuer-Pattern! (Erst wenn er in der Mitte ruht)
                if abs(self.exact_x - target_x) < 20 and abs(self.exact_y - target_y) < 20:
                    self.attack_timer -= 1
                    if self.attack_timer <= 0:
                        self.shoot(enemy_bullets, explosions, all_sprites)
                        self.bursts_fired += 1
                        self.attack_timer = ENDBOSS_ATTACK_COOLDOWN
                        
                        # Nach 4 Salven wieder bei Phase 1 anfangen
                        if self.bursts_fired >= 4:
                            self.phase = 1
                            self.phase_timer = ENDBOSS_PHASE_DURATION
                            self.bursts_fired = 0

    def shoot(self, enemy_bullets, explosions, all_sprites):
        # Exakte Positionen der "Rohre" berechnen
        center_pipe = self.rect.midbottom
        
        # 20% Eingerückt von den Seiten, leicht über dem Boden
        left_pipe = (self.rect.left + self.rect.width * 0.2, self.rect.bottom - 10)
        right_pipe = (self.rect.right - self.rect.width * 0.2, self.rect.bottom - 10)

        # 90° = Unten Mitte, 135° = Diagonal Unten Links, 45° = Diagonal Unten Rechts
        p1 = EndBossProjectile(center_pipe, 90, 0, explosions, all_sprites, enemy_bullets, self.projectiles)
        p2 = EndBossProjectile(left_pipe, 135, 0, explosions, all_sprites, enemy_bullets, self.projectiles)
        p3 = EndBossProjectile(right_pipe, 45, 0, explosions, all_sprites, enemy_bullets, self.projectiles)

        for p in (p1, p2, p3):
            self.projectiles.add(p)
            if enemy_bullets is not None:
                enemy_bullets.add(p)
            if all_sprites is not None:
                all_sprites.add(p)

    def hit(self):
        # Boss ist UNVERWUNDBAR, solange er seine krasse Intro-Animation ausführt
        if self.state == self.STATE_SPAWNING:
            return 
            
        self.health -= 1
        if self.health <= 0:
            # Wenn der Boss stirbt, verschwinden seine Kugeln sofort lautlos
            for proj in self.projectiles:
                proj.silent_kill = True
                proj.kill()
            self.kill()