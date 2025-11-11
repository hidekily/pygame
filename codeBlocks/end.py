import pygame
from config import SCREEN_WIDTH, GREEN, RED, WHITE, GRAY, MENU, SELECTION
from utils import btn

def draw(screen, message, player_team, ai_team):
    """Draws last bg"""
    f = pygame.font.Font(None, 70)
    col = GREEN if "PLAYER" in message else RED
    t = f.render(message, True, col)
    screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 280))
    
    f2 = pygame.font.Font(None, 28)
    p_alive = sum(1 for p in player_team if p.alive)
    ai_alive = sum(1 for p in ai_team if p.alive)
    
    t2 = f2.render(f"Final Score: Your Team {p_alive} x {ai_alive} AI Team", True, WHITE)
    screen.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, 380))
    
    t3 = f2.render("Log saved: game_event_log.txt", True, GRAY)
    screen.blit(t3, (SCREEN_WIDTH//2 - t3.get_width()//2, 420))
    
    btn(screen, 400, 480, 180, 50, "MAIN MENU", (50,100,200))
    btn(screen, 700, 480, 180, 50, "PLAY AGAIN", GREEN)

def handle_click(pos):
    """Processa cliques na tela final"""
    if pygame.Rect(400, 480, 180, 50).collidepoint(pos):
        return MENU
    elif pygame.Rect(700, 480, 180, 50).collidepoint(pos):
        return SELECTION
    return None