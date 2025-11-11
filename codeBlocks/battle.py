import pygame
import random
from config import SCREEN_WIDTH, GREEN, RED, YELLOW, BLACK, WHITE, GRAY, DARK_GRAY, base_chars
from utils import log, event_log, btn, play_sfx
from unit import Unit
from save_load import save_game # Import save_game function

# Unit layout settings
UNIT_SPACING = 250 # Spacing to fit 3 units on screen
START_Y = 20 # Start drawing units near the top

def draw(screen, player_team, ai_team, current, message, m_pos):
    """Draws battle screen"""
    f = pygame.font.Font(None, 44)
    t = f.render("⚔️ BATTLE ⚔️", True, YELLOW)
    screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 15))
    
    # --- Vertical Column Layout ---
    
    # OUR TEAM (Player Team - Single Vertical Column)
    f2 = pygame.font.Font(None, 28)
    screen.blit(f2.render("YOUR TEAM", True, GREEN), (80, 80))
    for i, p in enumerate(player_team[:6]): # Iterate over max 6 units
        x = 100 # Fixed X position
        y = START_Y + i * UNIT_SPACING # Y position grows linearly
        is_turn = current and current[0]=="player" and current[1]==p
        p.draw(screen, x, y, False, is_turn)
    
    # AI TEAM (AI Team - Single Vertical Column)
    screen.blit(f2.render("AI TEAM", True, RED), (1050, 80))
    p_turn = current and current[0]=="player"
    for i, p in enumerate(ai_team[:6]):
        x_ai = 960
        y_ai = START_Y + i * UNIT_SPACING # Y position also uses the new spacing
        
        p.hover = False
        # Use the new Y position for collision check as well
        if pygame.Rect(x_ai, y_ai, 120, 120).collidepoint(m_pos) and p_turn and p.alive:
            p.hover = True
        p.draw(screen, x_ai, y_ai, p_turn)
    
    # BATTLE SHOP PANEL (centered, bigger)
    shop_x, shop_y = SCREEN_WIDTH//2 - 500//2, 150
    shop_w, shop_h = 500, 500
    pygame.draw.rect(screen, (50, 50, 80), (shop_x, shop_y, shop_w, shop_h))
    pygame.draw.rect(screen, (80, 80, 120), (shop_x, shop_y, shop_w, 30))
    
    shop_f = pygame.font.Font(None, 30)
    shop_t = shop_f.render("BATTLE SHOP (placeholder)", True, YELLOW)
    screen.blit(shop_t, (shop_x + shop_w//2 - shop_t.get_width()//2, shop_y + 5))
    
    # Event Log (smaller, at bottom)
    log_x, log_y = 450, 670
    log_w, log_h = 380, 90
    
    pygame.draw.rect(screen, (20, 20, 30), (log_x, log_y, log_w, log_h))
    
    log_f = pygame.font.Font(None, 20)
    
    # Display last 3 log messages
    for i, msg in enumerate(event_log[-3:]):
        log_t = log_f.render(msg, True, GRAY)
        screen.blit(log_t, (log_x + 10, log_y + 10 + i * 25))
    
    # Message Box (bottom center)
    msg_x, msg_y = SCREEN_WIDTH//2 - 400//2, 730
    msg_w, msg_h = 400, 40
    pygame.draw.rect(screen, DARK_GRAY, (msg_x, msg_y, msg_w, msg_h))
    
    msg_f = pygame.font.Font(None, 24)
    msg_t = msg_f.render(message, True, WHITE)
    screen.blit(msg_t, (msg_x + msg_w//2 - msg_t.get_width()//2, msg_y + msg_h//2 - msg_t.get_height()//2))
    
    # Next Turn button (TC-15)
    # FIX for AttributeError: Assumes btn() returns a tuple, gets the Rect at index 0
    next_rect_data = btn(screen, SCREEN_WIDTH//2 - 120//2, 50, 120, 30, "NEXT", YELLOW, current and current[0]=="player")
    next_rect = next_rect_data[0] if isinstance(next_rect_data, tuple) else next_rect_data
    
    # SAVE GAME BUTTON (Re-implemented)
    save_btn_data = btn(screen, shop_x + 100, shop_y + 400, 300, 50, "SAVE GAME", (0, 150, 0), True)
    save_btn_rect = save_btn_data[0] if isinstance(save_btn_data, tuple) else save_btn_data

    # Return only the clickable rects
    return next_rect, save_btn_rect

def handle_click(pos, game, screen):
    """Processes battle clicks"""
    # Pass the screen object to draw
    next_rect, save_btn_rect = draw(screen, game.player_team, game.ai_team, game.current, game.message, pos)
    
    new_state = None
    new_message = ""
    
    # Next turn
    if next_rect.collidepoint(pos) and game.current and game.current[0]=="player":
        from battle import next_turn
        game.turn_idx, game.current = next_turn(game.turn_order, game.turn_idx, game)
        game.check_end()
        play_sfx("next")
    
    # Save Game button
    elif save_btn_rect.collidepoint(pos):
        success, msg = save_game(game)
        game.message = msg # Show "Game Saved!" or error
        play_sfx("click") # (Or "save" if you have it)
        
    # Target selection (Handles all clicks on the battlefield if it's the player's turn)
    elif game.current and game.current[0]=="player":
        team, attacker = game.current
        
        # Check if enemy was clicked
        target_clicked = False
        for i, p in enumerate(game.ai_team):
            x_ai = 960
            y_ai = START_Y + i * UNIT_SPACING # Use vertical spacing
            if pygame.Rect(x_ai, y_ai, 120, 120).collidepoint(pos) and p.alive:
                attacker.attack(p)
                game.message = f"{attacker.name} attacked {p.name}!"
                
                # Experience gain (simplified)
                attacker.gain_exp(random.randint(7, 12))
                p.gain_exp(random.randint(5, 10)) # Defender also gains exp
                
                # Advance turn
                from battle import next_turn
                game.turn_idx, game.current = next_turn(game.turn_order, game.turn_idx, game)
                game.check_end()
                target_clicked = True
                break
        
        # Only show error message if the click was NOT on a target
        if not target_clicked:
            game.message = f"Your turn: {attacker.name}! Select a target or skip turn."
            play_sfx("error")
        
    return new_state, new_message # Return state for main.py


def create_turns(player_team, ai_team):
    """Creates initial turn order"""
    turn_order = []
    max_len = max(len(player_team), len(ai_team))
    for i in range(max_len):
        if i < len(player_team):
            turn_order.append(("player", player_team[i]))
        if i < len(ai_team):
            turn_order.append(("ai", ai_team[i]))
    
    log(f"Turn order created with {len(player_team)} players and {len(ai_team)} AI")
    return turn_order

def next_turn(turn_order, turn_idx, game):
    """Advances to next turn"""
    attempts = 0
    while attempts < len(turn_order):
        turn_idx = (turn_idx + 1) % len(turn_order)
        team, unit = turn_order[turn_idx]
        if unit.alive:
            current = (team, unit)
            if team == "player":
                game.message = f"Your turn: {unit.name}! Select a target or skip turn."
                log(f"Player turn: {unit.name}")
            else:
                game.message = f"AI turn: {unit.name}"
                log(f"AI turn: {unit.name}")
                ai_turn(current, game) # AI logic runs here
            return turn_idx, current
        attempts += 1
    return turn_idx, None

def ai_turn(current, game):
    """AI turn logic"""
    team, attacker = current
    targets = [p for p in game.player_team if p.alive]
    if not targets: 
        return
    
    target = min(targets, key=lambda p: p.hp) # Target unit with lowest HP
    
    # AI attack logic (TC-16)
    attacker.attack(target)
    game.message = f"AI turn: {attacker.name} attacked {target.name}!"
    
    # Experience gain (simplified)
    attacker.gain_exp(random.randint(7, 12))
    target.gain_exp(random.randint(5, 10)) # Defender also gains exp
    
    # DO NOT ADVANCE TURN HERE. The main.py loop handles the advance.