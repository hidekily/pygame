import pygame
import sys

# Import game modules
from config import *
from utils import log, save_log, load_bg, play_music
from game_manager import GameManager
import menu
import selection
import battle
import end

# Initialization ================================================================================
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Turn-Based Battle Game")
clock = pygame.time.Clock()

# Sound initialization =================================================================
pygame.mixer.init()
pygame.mixer.music.set_volume(0.5)

# Load backgrounds ==========================================
menu_bg = load_bg(MENU_BG, SCREEN_WIDTH, SCREEN_HEIGHT)
battle_bg = load_bg(BATTLE_BG, SCREEN_WIDTH, SCREEN_HEIGHT)
selection_bg = load_bg(SELECTION_BG, SCREEN_WIDTH, SCREEN_HEIGHT)

# Game state manager
game = GameManager()

play_music(Menu_music)
log("Game Started")

# Main game loop ================================================================================
running = True

while running:
    screen.fill(BLACK)
    
    # Draw backgrounds ==========================================
    if game.state == MENU and menu_bg: 
        screen.blit(menu_bg, (0, 0))
    elif game.state == SELECTION and selection_bg: 
        screen.blit(selection_bg, (0, 0))
    elif game.state == BATTLE and battle_bg: 
        screen.blit(battle_bg, (0, 0))
    
    m_pos = pygame.mouse.get_pos()
    
    # Event handling ================================================================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_log()
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            
            # MENU ================================================================================
            if game.state == MENU:
                new_state = menu.handle_click(pos)
                if new_state == SELECTION:
                    game.state = SELECTION
            
            # SELECTION ================================================================================
            elif game.state == SELECTION:
                selection.handle_click(pos, game.player_team, game.selected)
                
                if len(game.player_team) == 3 and pygame.Rect(540, 660, 200, 50).collidepoint(pos):
                    game.start_battle()
                    game.turn_idx, game.current = battle.next_turn(game.turn_order, game.turn_idx, game.get_game_state())
            
            # BATTLE ================================================================================
            elif game.state == BATTLE:
                attacked = battle.handle_click(pos, game.player_team, game.ai_team, game.current, game.get_game_state())
                if attacked:
                    game.check_end()
                    if game.state == BATTLE:
                        pygame.time.wait(400)
                        game.turn_idx, game.current = battle.next_turn(game.turn_order, game.turn_idx, game.get_game_state())
            
            # END ================================================================================
            elif game.state == END:
                new_state = end.handle_click(pos)
                if new_state == MENU:
                    game.reset()
                    play_music(Menu_music)
                elif new_state == SELECTION:
                    game.reset()
                    game.state = SELECTION
                    play_music(Selection_music)
    
    # DRAW ================================================================================
    if game.state == MENU:
        menu.draw(screen)
    
    elif game.state == SELECTION:
        selection.draw(screen, game.player_team, game.selected, m_pos)
    
    elif game.state == BATTLE:
        battle.draw(screen, game.player_team, game.ai_team, game.current, game.message, m_pos)
    
    elif game.state == END:
        end.draw(screen, game.message, game.player_team, game.ai_team)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()