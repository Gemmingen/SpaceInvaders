import pygame
from src.utils.helpers import load_image
from src.config.config import (
    BOSS_HEALTHBAR_WIDTH, BOSS_HEALTHBAR_HEIGHT, 
    BOSS_HEALTHBAR_OFFSET_Y, BOSS_HEALTHBAR_INNER_OFFSET_X, 
    BOSS_HEALTHBAR_INNER_OFFSET_Y
)

class BossHealthBar:
    def __init__(self, boss):
        self.boss = boss
        # Speichere die maximalen HP zum Zeitpunkt des Spawns
        self.max_health = float(boss.health)
        
        # Der Endboss bekommt eine doppelt so große Healthbar für mehr Epik!
        if type(boss).__name__ == "EndBoss":
            self.width = BOSS_HEALTHBAR_WIDTH * 2
            self.height = int(BOSS_HEALTHBAR_HEIGHT * 1.5)
        else:
            self.width = BOSS_HEALTHBAR_WIDTH
            self.height = BOSS_HEALTHBAR_HEIGHT
            
        # Lade den Rahmen (boss-healthbar.png)
        try:
            raw_frame = load_image('assets/boss-healthbar.png').convert_alpha()
            self.frame_img = pygame.transform.scale(raw_frame, (self.width, self.height))
        except Exception:
            self.frame_img = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(self.frame_img, (255, 255, 255), self.frame_img.get_rect(), 2)
            
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Skaliere die inneren Abstände
        scale_x = self.width / BOSS_HEALTHBAR_WIDTH
        scale_y = self.height / BOSS_HEALTHBAR_HEIGHT
        self.inner_x = int(BOSS_HEALTHBAR_INNER_OFFSET_X * scale_x)
        self.inner_y = int(BOSS_HEALTHBAR_INNER_OFFSET_Y * scale_y)
        
        self.inner_max_w = self.width - (2 * self.inner_x)
        self.inner_h = self.height - (2 * self.inner_y)

    def draw(self, screen):
        # 1. Verstecke den Balken im Intro oder Todeskampf
        state = getattr(self.boss, 'state', None)
        if state in ['intro', 'spawning', 'dying'] or self.boss.health <= 0:
            return
            
        self.surface.fill((0, 0, 0, 0)) 
        
        # 2. Berechne aktuelles Leben in Prozent
        pct = max(0.0, self.boss.health / self.max_health)
        current_w = int(self.inner_max_w * pct)
        
        # 3. Zeichne rotes Rechteck (Ganz normales, hartes Rechteck!)
        if current_w > 0:
            fill_rect = pygame.Rect(self.inner_x, self.inner_y, current_w, self.inner_h)
            pygame.draw.rect(self.surface, (220, 20, 20), fill_rect)
            
        # 4. "Stemple" deinen PNG-Rahmen exakt darüber
        self.surface.blit(self.frame_img, (0, 0))
        
        # 5. Positioniere über dem Boss
        draw_x = self.boss.rect.centerx - (self.width // 2)
        draw_y = self.boss.rect.top - BOSS_HEALTHBAR_OFFSET_Y - self.height
        
        screen.blit(self.surface, (draw_x, draw_y))