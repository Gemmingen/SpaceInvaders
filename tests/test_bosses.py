"""
Tests für die Bosse, um sicherzustellen, dass sie in bestimmten Animations- 
oder Spawn-Phasen keinen ungerechtfertigten Schaden nehmen.
"""
import pytest
from src.game.Boss_small_1 import BossSmall1
from src.game.endboss import EndBoss

def test_boss_small_1_invulnerable_during_intro():
    """Prüft, ob der erste Boss während seiner Intro-Animation immun gegen Beschuss ist."""
    # Arrange
    boss = BossSmall1(health=5, speed=2)
    boss.state = "intro" # Boss künstlich in den Intro-Zustand versetzen
    
    # Act
    boss.hit() 
    
    # Assert
    assert boss.health == 5, "Im Intro darf der Boss keine HP durch Treffer verlieren."

def test_boss_small_1_takes_damage_when_active():
    """Prüft, ob der Boss im regulären Kampfzustand normal Schaden nimmt."""
    # Arrange
    boss = BossSmall1(health=5, speed=2)
    boss.state = "active" 
    
    # Act
    boss.hit()
    
    # Assert
    assert boss.health == 4, "Im aktiven Zustand muss ein Treffer 1 HP abziehen."

def test_endboss_invulnerable_during_spawn():
    """Prüft, ob der finale Boss während der Spawning-Sequenz vor Schaden geschützt ist."""
    # Arrange
    boss = EndBoss(health=100)
    boss.state = boss.STATE_SPAWNING
    
    # Act
    boss.hit()
    
    # Assert
    assert boss.health == 100, "Der Endboss darf beim Spawnen keine HP verlieren."