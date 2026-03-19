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
    ENDBOSS_RANDOM_SHOOT_MIN, ENDBOSS_RANDOM_SHOOT_MAX,
    ENDBOSS_PROJ_SIZE_LARGE, ENDBOSS_PROJ_SIZE_SMALL,
    ENDBOSS_EXPLOSION_SIZE, ENDBOSS_SPAWNER_SIZE,
    ENDBOSS_SPAWN_FRAMES, ENDBOSS_SPAWNER_ROT_SPEED,
    ENDBOSS_BURSTS_PER_CYCLE, ENDBOSS_EASING_SPEED,
    ENDBOSS_CENTER_Y, ENDBOSS_TOP_Y, ENDBOSS_PATTERN_AMP_X,
    ENDBOSS_PATTERN_AMP_Y, ENDBOSS_PATTERN_WIDE_X,
    ENDBOSS_FREQ_MULT_X, ENDBOSS_FREQ_MULT_Y1, ENDBOSS_FREQ_MULT_Y2,
    ENDBOSS_TIME_STEP, ENDBOSS_CENTER_TOLERANCE,
    ENDBOSS_PIPE_X_OFFSET_PCT, ENDBOSS_PIPE_Y_OFFSET, ENDBOSS_PIPE_ANGLES,
    ENDBOSS_DEATH_SHAKE_FRAMES, ENDBOSS_DEATH_SHAKE_PIXELS,
    ENDBOSS_DEATH_EXPLOSION_SIZE, ENDBOSS_DEATH_EXPLOSION_DELAY,
    ENDBOSS_DEATH_EASING_SPEED, ENDBOSS_DEATH_MINI_EXP_INTERVAL
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
            self.image_base = pygame.transform.scale(img, ENDBOSS_PROJ_SIZE_LARGE)
        else:
            self.image_base = pygame.transform.scale(img, ENDBOSS_PROJ_SIZE_SMALL)
            
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
                    exp = Explosion(self.rect.centerx, self.rect.centery, size=ENDBOSS_EXPLOSION_SIZE)
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
    STATE_DYING = "dying"

    def __init__(self, health=50, speed=3):
        super().__init__('assets/endboss.png', health, speed)
        
        # Lade Originalbilder für die Intro-Animation
        self.boss_base = load_image('assets/endboss.png').convert_alpha()
        self.spawner_base = load_image('assets/endboss-spawner.png').convert_alpha()
        
        # Start-Setup (Mitte oben)
        self.center_pos = pygame.math.Vector2(SCREEN_WIDTH // 2, ENDBOSS_CENTER_Y)
        self.exact_x = float(self.center_pos.x)
        self.exact_y = float(ENDBOSS_TOP_Y)
        
        # FIX: Behebt den 1-Millisekunde-Glitch oben links! 
        # Macht das Sprite für den allerersten Frame komplett unsichtbar
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(round(self.exact_x), round(self.exact_y)))
        
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
        
        # Todes-Logik
        self.death_timer = 0
        self.base_x = 0
        self.base_y = 0

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
        # 0. TODES-ANIMATION (In die Mitte driften & Mini-Explosionen)
        # ========================================================
        if self.state == self.STATE_DYING:
            self.death_timer -= 1
            
            if self.death_timer > 0:
                # 1. Easing in Richtung Bildschirmmitte
                target_x = SCREEN_WIDTH // 2
                target_y = SCREEN_HEIGHT // 2
                self.base_x += (target_x - self.base_x) * ENDBOSS_DEATH_EASING_SPEED
                self.base_y += (target_y - self.base_y) * ENDBOSS_DEATH_EASING_SPEED
                
                # 2. Heftiges Wackeln
                offset_x = random.randint(-ENDBOSS_DEATH_SHAKE_PIXELS, ENDBOSS_DEATH_SHAKE_PIXELS)
                offset_y = random.randint(-ENDBOSS_DEATH_SHAKE_PIXELS, ENDBOSS_DEATH_SHAKE_PIXELS)
                self.rect.centerx = round(self.base_x) + offset_x
                self.rect.centery = round(self.base_y) + offset_y
                
                # 3. Random kleine Explosionen spawnen (immer im Rhythmus)
                if self.death_timer % ENDBOSS_DEATH_MINI_EXP_INTERVAL == 0:
                    if explosions is not None:
                        mini_x = self.rect.centerx + random.randint(-ENDBOSS_WIDTH // 2, ENDBOSS_WIDTH // 2)
                        mini_y = self.rect.centery + random.randint(-ENDBOSS_HEIGHT // 2, ENDBOSS_HEIGHT // 2)
                        mini_exp = Explosion(mini_x, mini_y, size=64)
                        explosions.add(mini_exp)
                        if all_sprites is not None:
                            all_sprites.add(mini_exp)
            else:
                # 4. Am Ende die gigantische Explosion spawnen
                if explosions is not None:
                    exp = Explosion(
                        round(self.base_x), round(self.base_y), 
                        size=ENDBOSS_DEATH_EXPLOSION_SIZE, 
                        anim_delay=ENDBOSS_DEATH_EXPLOSION_DELAY
                    )
                    explosions.add(exp)
                    if all_sprites is not None:
                        all_sprites.add(exp)
                
                # Boss endgültig entfernen
                self.kill() 
                
            return # Blockiert das Fliegen & Schießen!

        # ========================================================
        # 1. INTRO / SPAWN ANIMATION
        # ========================================================
        if self.state == self.STATE_SPAWNING:
            self.spawn_timer += 1
            
            # Erstelle eine durchsichtige Arbeitsfläche (Canvas) für die Animation
            canvas_size = ENDBOSS_SPAWNER_SIZE + 100
            surf = pygame.Surface((canvas_size, canvas_size), pygame.SRCALPHA)
            center = (canvas_size // 2, canvas_size // 2)
            
            # --- Spawner Logik ---
            spawner_scale = min(1.0, self.spawn_timer / float(ENDBOSS_SPAWN_FRAMES))
            if spawner_scale > 0:
                spawner_size = int(ENDBOSS_SPAWNER_SIZE * spawner_scale)
                if spawner_size > 0:
                    spawner_scaled = pygame.transform.scale(self.spawner_base, (spawner_size, spawner_size))
                    # Rotiert anhand der Zeit
                    spawner_rot = pygame.transform.rotate(spawner_scaled, self.spawn_timer * ENDBOSS_SPAWNER_ROT_SPEED)
                    sp_rect = spawner_rot.get_rect(center=center)
                    surf.blit(spawner_rot, sp_rect)
            
            # --- Boss Zoom Logik ---
            if self.spawn_timer > ENDBOSS_SPAWN_FRAMES:
                boss_scale = min(1.0, (self.spawn_timer - ENDBOSS_SPAWN_FRAMES) / float(ENDBOSS_SPAWN_FRAMES))
                bw = int(ENDBOSS_WIDTH * boss_scale)
                bh = int(ENDBOSS_HEIGHT * boss_scale)
                if bw > 0 and bh > 0:
                    boss_scaled = pygame.transform.scale(self.boss_base, (bw, bh))
                    b_rect = boss_scaled.get_rect(center=center)
                    surf.blit(boss_scaled, b_rect)
            
            self.image = surf
            self.rect = self.image.get_rect(center=(round(self.exact_x), round(self.exact_y)))
            
            # Animation beendet
            if self.spawn_timer >= ENDBOSS_SPAWN_FRAMES * 2:
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
            self.t += ENDBOSS_TIME_STEP 
            
            # Start/Ziel-Koordinaten
            target_x = self.center_pos.x
            target_y = self.center_pos.y

            # --- Flugmuster Phasen (Berechnen nur das MATHEMATISCHE Ziel) ---
            if self.phase == 1:
                # Pattern: Boss 1 (Kreisen)
                target_x = self.center_pos.x + ENDBOSS_PATTERN_AMP_X * math.cos(self.t)
                target_y = self.center_pos.y + ENDBOSS_PATTERN_AMP_Y * math.sin(self.t)
                
            elif self.phase == 2:
                # Pattern: Boss 2 (Pendeln oben)
                target_x = self.center_pos.x + ENDBOSS_PATTERN_WIDE_X * math.sin(self.t * ENDBOSS_FREQ_MULT_X)
                target_y = ENDBOSS_TOP_Y
                    
            elif self.phase == 3:
                # Pattern: Boss 3 (Welle)
                target_x = self.center_pos.x + ENDBOSS_PATTERN_WIDE_X * math.sin(self.t * ENDBOSS_FREQ_MULT_X)
                target_y = self.center_pos.y - 50 + ENDBOSS_PATTERN_AMP_Y * math.cos(self.t * ENDBOSS_FREQ_MULT_Y1)
                    
            elif self.phase == 4:
                # Pattern: Boss 4 (8er Bewegung)
                target_x = self.center_pos.x + ENDBOSS_PATTERN_WIDE_X * math.sin(self.t * ENDBOSS_FREQ_MULT_X)
                target_y = self.center_pos.y + ENDBOSS_PATTERN_AMP_Y * math.sin(self.t * ENDBOSS_FREQ_MULT_Y2)
                
            elif self.phase == 5:
                # Finales Pattern: Genau im Zentrum stehen
                target_x = self.center_pos.x
                target_y = ENDBOSS_TOP_Y

            # --- SMOOTH EASING ---
            # Der Boss lenkt sanft zu seinem Ziel-Pattern, ohne zu Ruckeln/Zucken!
            self.exact_x += (target_x - self.exact_x) * ENDBOSS_EASING_SPEED
            self.exact_y += (target_y - self.exact_y) * ENDBOSS_EASING_SPEED
            
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
                if abs(self.exact_x - target_x) < ENDBOSS_CENTER_TOLERANCE and abs(self.exact_y - target_y) < ENDBOSS_CENTER_TOLERANCE:
                    self.attack_timer -= 1
                    if self.attack_timer <= 0:
                        self.shoot(enemy_bullets, explosions, all_sprites)
                        self.bursts_fired += 1
                        self.attack_timer = ENDBOSS_ATTACK_COOLDOWN
                        
                        # Nach 4 Salven wieder bei Phase 1 anfangen
                        if self.bursts_fired >= ENDBOSS_BURSTS_PER_CYCLE:
                            self.phase = 1
                            self.phase_timer = ENDBOSS_PHASE_DURATION
                            self.bursts_fired = 0

    def shoot(self, enemy_bullets, explosions, all_sprites):
        # Exakte Positionen der "Rohre" berechnen
        center_pipe = self.rect.midbottom
        
        # 20% Eingerückt von den Seiten, leicht über dem Boden
        left_pipe = (self.rect.left + self.rect.width * ENDBOSS_PIPE_X_OFFSET_PCT, self.rect.bottom - ENDBOSS_PIPE_Y_OFFSET)
        right_pipe = (self.rect.right - self.rect.width * ENDBOSS_PIPE_X_OFFSET_PCT, self.rect.bottom - ENDBOSS_PIPE_Y_OFFSET)

        # 90° = Unten Mitte, 135° = Diagonal Unten Links, 45° = Diagonal Unten Rechts
        p1 = EndBossProjectile(center_pipe, ENDBOSS_PIPE_ANGLES[0], 0, explosions, all_sprites, enemy_bullets, self.projectiles)
        p2 = EndBossProjectile(left_pipe, ENDBOSS_PIPE_ANGLES[1], 0, explosions, all_sprites, enemy_bullets, self.projectiles)
        p3 = EndBossProjectile(right_pipe, ENDBOSS_PIPE_ANGLES[2], 0, explosions, all_sprites, enemy_bullets, self.projectiles)

        for p in (p1, p2, p3):
            self.projectiles.add(p)
            if enemy_bullets is not None:
                enemy_bullets.add(p)
            if all_sprites is not None:
                all_sprites.add(p)

    def hit(self):
        # Unverwundbar im Spawning UND im Sterben
        if self.state in (self.STATE_SPAWNING, self.STATE_DYING):
            return 
            
        self.health -= 1
        if self.health <= 0:
            # Projektile lautlos zerstören
            for proj in self.projectiles:
                proj.silent_kill = True
                proj.kill()
                
            # Statt self.kill() leiten wir jetzt die Todesphase ein!
            self.state = self.STATE_DYING
            self.death_timer = ENDBOSS_DEATH_SHAKE_FRAMES
            self.base_x = self.exact_x
            self.base_y = self.exact_y