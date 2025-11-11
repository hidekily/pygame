import pygame
import os
from config import SCREEN_WIDTH, BLACK, GREEN, DARK_GRAY, YELLOW, base_chars
from utils import btn, log, play_sfx
from unit import Unit

def draw(screen, player_team, selected, m_pos):
    """Draws selection screen"""
    f = pygame.font.Font(None, 44)
    t = f.render("SELECT YOUR TEAM (3 UNITS)", True, BLACK)
    screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 40))
    
    c = f.render(f"{len(player_team)}/3 Selected", True, GREEN if len(player_team)==3 else BLACK)
    screen.blit(c, (SCREEN_WIDTH//2 - c.get_width()//2, 100))
    
    # Draw characters with sprites===============================================================
    for i in range(6):
        col, row = i % 3, i // 3
        x_pos = 180 + col * 320
        y_pos = 180 + row * 260
        prof, name, spr = base_chars[i]
        
        # Load sprite =========================================================================
        sprite_rect = pygame.Rect(x_pos, y_pos, 120, 120)
        
        if os.path.exists(spr):
            try:
                temp_sprite = pygame.image.load(spr)
                temp_sprite = pygame.transform.scale(temp_sprite, (120, 120))
                screen.blit(temp_sprite, (x_pos, y_pos))
            except:
                color = (200,50,50) if prof=="Warrior" else (100,70,40)
                pygame.draw.rect(screen, color, sprite_rect)
        else:
            color = (200,50,50) if prof=="Warrior" else (100,70,40)
            pygame.draw.rect(screen, color, sprite_rect)
        
        pygame.draw.rect(screen, BLACK, sprite_rect, 3)
        
        # Hover and selection =================================================================================
        if sprite_rect.collidepoint(m_pos):
            pygame.draw.rect(screen, YELLOW, (x_pos-2, y_pos-2, 124, 124), 3)
        if selected[i]:
            pygame.draw.rect(screen, YELLOW, (x_pos-4, y_pos-4, 128, 128), 5)
        
        # Information BELOW the sprite ===========================================================================
        info_y = y_pos + 130
        
        f_name = pygame.font.Font(None, 24)
        name_text = f_name.render(name, True, BLACK)
        screen.blit(name_text, (x_pos + 60 - name_text.get_width()//2, info_y))
        
        f_prof = pygame.font.Font(None, 18)
        prof_text = f_prof.render(prof, True, DARK_GRAY)
        screen.blit(prof_text, (x_pos + 60 - prof_text.get_width()//2, info_y + 24))
        
        # Character base stats =======================================================================
        f_stats = pygame.font.Font(None, 16)
        if prof == "Warrior":
            stats_text = "Attack: 5-20 | Defense: 1-10"
        else:  # Tank ====================================================================================
            stats_text = "Attack: 1-10 | Defense: 5-15"
        stats_render = f_stats.render(stats_text, True, BLACK)
        screen.blit(stats_render, (x_pos + 60 - stats_render.get_width()//2, info_y + 46))
    
    if len(player_team) == 3:
        btn(screen, 540, 660, 200, 50, "START BATTLE", (50,100,200))

def handle_click(pos, player_team, selected):
    """Processes selection clicks"""
    for i in range(6):
        col, row = i % 3, i // 3
        x_pos = 180 + col * 320
        y_pos = 180 + row * 260
        if pygame.Rect(x_pos, y_pos, 120, 120).collidepoint(pos):
            if selected[i]:
                selected[i] = False
                prof, name, spr = base_chars[i]
                player_team[:] = [p for p in player_team if p.name != name]
                log(f"Deselected: {name}")
            elif len(player_team) < 3:
                selected[i] = True
                prof, name, spr = base_chars[i]
                player_team.append(Unit(name, prof, spr))
                
                # TC-42: Character select sound
                play_sfx('select')
                
                log(f"Selected: {name} ({prof})")
    
    return None