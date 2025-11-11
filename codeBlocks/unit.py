import pygame
import random
import os
from utils import log
from config import WHITE, BLACK, GREEN, RED, YELLOW, GRAY

class Unit:
    def __init__(self, name, prof, sprite_path=None):
        self.name, self.prof, self.rank, self.exp = name, prof, 1, 0
        self.hp_max = self.hp = 100
        self.coins = 0  # TC-21: Coin system
        
        if prof == "Warrior":
            self.atk, self.defense = random.randint(5, 20), random.randint(1, 10)
        else:  # Tank ================================================================================
            self.atk, self.defense = random.randint(1, 10), random.randint(5, 15)
        
        self.alive = True
        self.sprite = None
        if sprite_path and os.path.exists(sprite_path):
            try:
                self.sprite = pygame.image.load(sprite_path)
                self.sprite = pygame.transform.scale(self.sprite, (120, 120))
            except: 
                print(f"Error loading sprite: {sprite_path}")
        
        self.hover = self.attacked = self.attacking = False
        self.effect_time = 0
        log(f"Unit created: {name} ({prof}) - HP:{self.hp} ATK:{self.atk} DEF:{self.defense}")
    
def attack(self, target):
    """Attacks another unit"""
    # Improved damage formula: guarantees meaningful damage
    # Base damage from attack stat
    base_damage = self.atk
    
    # Add random variance (30% of attack)
    variance = random.randint(0, max(1, self.atk // 3))
    
    # Defense reduces damage by 30% of defense value
    defense_reduction = target.defense * 0.3
    
    # Calculate final damage (minimum 3)
    dmg = max(3, int(base_damage + variance - defense_reduction))
    
    # APPLY DAMAGE TO TARGET
    target.hp = max(0, target.hp - dmg)
    target.alive = target.hp > 0
    
    # TC-21: Earn coins from damage (damage ÷ 2)
    coins_earned = dmg // 2
    self.coins += coins_earned
    if coins_earned > 0:
        log(f"{self.name} earned {coins_earned} coins! (Total: {self.coins})")
    
    self.gain_exp(dmg)
    target_exp = target.defense
    
    if dmg > 10:
        target_exp += int(target_exp * 0.2)
        log(f"{target.name} +20% bonus EXP (dmg > 10)")
    elif dmg <= 0:
        target_exp += int(target_exp * 0.5)
        log(f"{target.name} +50% bonus EXP (no dmg)")
    
    target.gain_exp(target_exp)
    
    self.attacking = target.attacked = True
    self.effect_time = target.effect_time = pygame.time.get_ticks()
    
    log(f"ATTACK: {self.name} -> {target.name} | Dmg: {dmg} | {target.name} HP: {target.hp}/{target.hp_max}")
    if not target.alive: 
        log(f"{target.name} defeated!")
    return dmg
    
    def gain_exp(self, exp):
        """Gains experience"""
        self.exp += exp
        log(f"{self.name} +{exp} EXP (Total: {self.exp})")
        
        # Handle multiple level ups (TC-52)
        while self.exp >= 100:
            self.rank += 1
            self.exp -= 100
            
            # TC-16: Level Up Stats - ATK +2, DEF +1, MaxHP +10, HP +20
            self.atk += 2
            self.defense += 1
            self.hp_max += 10
            self.hp = min(self.hp + 20, self.hp_max)  # TC-53: Cap at max HP
            
            # TC-39: Level up sound
            from utils import play_sfx
            play_sfx('levelup')
            
            log(f"LEVEL UP! {self.name} -> Rank {self.rank}!")
            log(f"Stats: ATK:{self.atk} DEF:{self.defense} MaxHP:{self.hp_max}")
    
    def draw(self, screen, x, y, show_hover=False, is_turn=False):
        """Draws the unit on screen"""
        if pygame.time.get_ticks() - self.effect_time > 300:
            self.attacking = self.attacked = False
        
        sprite_size = 120
        rect = pygame.Rect(x, y, sprite_size, sprite_size)
        
        # Turn effect (pulsing) ================================================================================
        if is_turn and self.alive:
            pulse = abs((pygame.time.get_ticks() % 800) / 400 - 1) * 4 + 2
            pygame.draw.rect(screen, YELLOW, (x-5, y-5, sprite_size+10, sprite_size+10), int(pulse))
        
        # Visual effects ================================================================================
        if show_hover and self.hover and self.alive:
            pygame.draw.rect(screen, YELLOW, (x-3, y-3, sprite_size+6, sprite_size+6), 3)
        if self.attacked: 
            pygame.draw.rect(screen, RED, (x-2, y-2, sprite_size+4, sprite_size+4), 5)
        if self.attacking: 
            pygame.draw.rect(screen, GREEN, (x-2, y-2, sprite_size+4, sprite_size+4), 5)
        
        # Draw sprite or rectangle================================================================================
        if self.sprite: 
            screen.blit(self.sprite, (x, y))
        else: 
            color = GRAY if not self.alive else (200,50,50) if self.prof=="Warrior" else (100,70,40)
            pygame.draw.rect(screen, color, rect)
        
        pygame.draw.rect(screen, BLACK, rect, 3)
        
        # Information BELOW the sprite ================================================================================
        info_y = y + sprite_size + 5
        
        f_name = pygame.font.Font(None, 22)
        name_text = f_name.render(self.name[:12], True, WHITE)
        screen.blit(name_text, (x + sprite_size//2 - name_text.get_width()//2, info_y))
        
        f_level = pygame.font.Font(None, 20)
        level_text = f_level.render(f"Level {self.rank}", True, YELLOW)
        screen.blit(level_text, (x + sprite_size//2 - level_text.get_width()//2, info_y + 22))
        
        # HP Bar ================================================================================
        hp_bar_y = info_y + 44
        hp_bar_width = sprite_size
        pygame.draw.rect(screen, RED, (x, hp_bar_y, hp_bar_width, 12))
        pygame.draw.rect(screen, GREEN, (x, hp_bar_y, int((self.hp/self.hp_max)*hp_bar_width), 12))
        pygame.draw.rect(screen, BLACK, (x, hp_bar_y, hp_bar_width, 12), 2)
        
        # Stats with labels ================================================================================
        f_stats = pygame.font.Font(None, 18)
        stats_y = hp_bar_y + 16
        stats = [
            f"Health: {self.hp}/{self.hp_max}",
            f"Attack: {self.atk} | Defense: {self.defense}",
            f"Experience: {self.exp}/100",
            f"💰 Coins: {self.coins}"  # TC-22: Display coins
        ]
        for i, stat in enumerate(stats):
            stat_text = f_stats.render(stat, True, WHITE if i < 3 else YELLOW)
            screen.blit(stat_text, (x + sprite_size//2 - stat_text.get_width()//2, stats_y + i*18))
        
        return rect
    
    def to_dict(self):
        """Serialize unit to dictionary for saving"""
        return {
            'name': self.name,
            'prof': self.prof,
            'rank': self.rank,
            'exp': self.exp,
            'hp': self.hp,
            'hp_max': self.hp_max,
            'atk': self.atk,
            'defense': self.defense,
            'coins': self.coins,
            'alive': self.alive
        }
    
    @staticmethod
    def from_dict(data, sprite_path=None):
        """Deserialize unit from dictionary"""
        unit = Unit(data['name'], data['prof'], sprite_path)
        unit.rank = data['rank']
        unit.exp = data['exp']
        unit.hp = data['hp']
        unit.hp_max = data['hp_max']
        unit.atk = data['atk']
        unit.defense = data['defense']
        unit.coins = data['coins']
        unit.alive = data['alive']
        return unit