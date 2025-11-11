import pygame
from config import SCREEN_WIDTH, BLACK, GREEN, SELECTION, MENU, Selection_music
from utils import btn, log, play_music

def draw(screen):
    """Draws the menu screen"""
    f1 = pygame.font.Font(None, 80)
    t = f1.render("TURN-BASED BATTLE", True, BLACK)
    screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 200))
    
    f2 = pygame.font.Font(None, 28)
    t2 = f2.render("ITGP2008 Assignment", True, BLACK)
    screen.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, 290))
    
    btn(screen, 540, 400, 200, 60, "START GAME", GREEN)

def handle_click(pos):
    """Processes menu clicks"""
    if pygame.Rect(540, 400, 200, 60).collidepoint(pos):
        log("Entered selection")
        play_music(Selection_music)
        return SELECTION
    return MENU