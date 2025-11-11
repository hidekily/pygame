import pygame
from config import SCREEN_WIDTH, BLACK, GREEN, SELECTION, MENU, Selection_music
from utils import btn, log, play_music

def draw(screen, has_save=False):
    """Draws the menu screen"""
    f1 = pygame.font.Font(None, 80)
    t = f1.render("TURN-BASED BATTLE", True, BLACK)
    screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 200))
    
    f2 = pygame.font.Font(None, 28)
    t2 = f2.render("ITGP2008 Assignment", True, BLACK)
    screen.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, 290))
    
    # Start button
    btn(screen, 540, 400, 200, 60, "START GAME", GREEN)
    
    # TC-29, TC-30: Load button (enabled if save exists)
    load_color = GREEN if has_save else (80, 80, 80)
    btn(screen, 540, 480, 200, 60, "LOAD GAME", load_color, has_save)
    
    # Controls info
    f3 = pygame.font.Font(None, 20)
    controls = [
        "Controls:",
        "M - Toggle Music",
        "N - Toggle SFX",
        "+ - Volume Up",
        "- - Volume Down"
    ]
    for i, ctrl in enumerate(controls):
        t3 = f3.render(ctrl, True, BLACK)
        screen.blit(t3, (50, 600 + i * 25))

def handle_click(pos):
    """Processes menu clicks"""
    if pygame.Rect(540, 400, 200, 60).collidepoint(pos):
        log("Entered selection")
        play_music(Selection_music)
        return SELECTION
    return MENU

def handle_load_click(pos):
    """Check if load button was clicked"""
    if pygame.Rect(540, 480, 200, 60).collidepoint(pos):
        return True
    return False