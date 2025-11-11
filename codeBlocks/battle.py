import pygame
import random
from config import SCREEN_WIDTH, GREEN, RED, YELLOW, BLACK, WHITE, base_chars
from utils import log, event_log, btn, play_sfx
from unit import Unit

def draw(screen, player_team, ai_team, current, message, m_pos):
    """Draws battle screen"""
    f = pygame.font.Font(None, 44)
    t = f.render("⚔️ BATTLE ⚔️", True, YELLOW)
    screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 15))
    
    # OUR TEAM ===============================================================================
    f2 = pygame.font.Font(None, 28)
    screen.blit(f2.render("YOUR TEAM", True, GREEN), (80, 80))
    for i, p in enumerate(player_team):
        is_turn = current and current[0]=="player" and current[1]==p
        p.draw(screen, 80, 150 + i * 200, False, is_turn)
    
    # AI TEAM =======================================================================================
    screen.blit(f2.render("AI TEAM", True, RED), (1050, 80))
    p_turn = current and current[0]=="player"
    for i, p in enumerate(ai_team):
        p.hover = False
        if pygame.Rect(960, 150 + i*200, 120, 120).collidepoint(m_pos) and p_turn and p.alive:
            p.hover = True
        p.draw(screen, 960, 150 + i * 200, p_turn)
    
    # Event Log Panel (centered)======================================================================
    log_x, log_y = 480, 180
    log_w, log_h = 320, 320  # Reduced height to make room for buttons
    
    pygame.draw.rect(screen, (20, 20, 30), (log_x, log_y, log_w, log_h))
    pygame.draw.rect(screen, YELLOW, (log_x, log_y, log_w, log_h), 2)
    
    f_log_title = pygame.font.Font(None, 24)
    log_title = f_log_title.render("⚔️ EVENT LOG ⚔️", True, YELLOW)
    screen.blit(log_title, (log_x + log_w//2 - log_title.get_width()//2, log_y + 10))
    
    f_log = pygame.font.Font(None, 16)
    log_start_y = log_y + 40
    line_height = 22
    max_lines = (log_h - 50) // line_height
    
    battle_logs = [l for l in event_log if any(x in l for x in ["ATTACK:", "defeated!", "LEVEL UP!", "turn:", "Battle Started", "earned", "recruited"])]
    recent_logs = battle_logs[-max_lines:]
    
    for i, log_entry in enumerate(recent_logs):
        if "] " in log_entry:
            msg_text = log_entry.split("] ", 1)[1][:45]
        else:
            msg_text = log_entry[:45]
        
        if "ATTACK:" in msg_text:
            color = (255, 150, 150)
        elif "defeated!" in msg_text:
            color = RED
        elif "LEVEL UP!" in msg_text:
            color = YELLOW
        elif "Player turn" in msg_text:
            color = GREEN
        elif "AI turn" in msg_text:
            color = (255, 100, 100)
        elif "earned" in msg_text or "coins" in msg_text:
            color = (255, 215, 0)  # Gold
        else:
            color = (200, 200, 200)
        
        log_line = f_log.render(msg_text, True, color)
        screen.blit(log_line, (log_x + 10, log_start_y + i * line_height))
    
    # Buttons below log ================================================================================
    button_y = log_y + log_h + 10
    
    # TC-23 to TC-26: RECRUIT button
    total_coins = sum(u.coins for u in player_team)
    can_recruit = total_coins >= 50 and len(player_team) < 6
    recruit_color = GREEN if can_recruit else (80, 80, 80)
    
    btn(screen, log_x, button_y, 150, 40, f"RECRUIT (50💰)", recruit_color, can_recruit)
    
    # Show total coins
    f_coins = pygame.font.Font(None, 20)
    coins_text = f_coins.render(f"Team Coins: {total_coins}💰", True, YELLOW)
    screen.blit(coins_text, (log_x + 160, button_y + 10))
    
    # SAVE button (TC-27)
    btn(screen, log_x, button_y + 50, 150, 40, "SAVE GAME", (50, 100, 200))
    
    # Message box ================================================================================
    f3 = pygame.font.Font(None, 24)
    msg = f3.render(message[:80], True, WHITE)
    mr = msg.get_rect(center=(SCREEN_WIDTH//2, 700))
    pygame.draw.rect(screen, BLACK, (mr.x-10, mr.y-5, mr.width+20, mr.height+10))
    pygame.draw.rect(screen, YELLOW, (mr.x-10, mr.y-5, mr.width+20, mr.height+10), 2)
    screen.blit(msg, mr)
    
    # Turn indicator ================================================================================
    if current:
        t, c = current
        col = GREEN if t=="player" else RED
        txt = f.render(f"TURN: {c.name}", True, col)
        tr = txt.get_rect(center=(SCREEN_WIDTH//2, 60))
        pygame.draw.rect(screen, BLACK, (tr.x-12, tr.y-6, tr.width+24, tr.height+12))
        pygame.draw.rect(screen, col, (tr.x-12, tr.y-6, tr.width+24, tr.height+12), 3)
        screen.blit(txt, tr)

def handle_click(pos, player_team, ai_team, current, game):
    """Processes attacks in battle"""
    # TC-58: Rapid clicking protection
    if hasattr(game, '_last_click_time'):
        if pygame.time.get_ticks() - game._last_click_time < 300:
            return False
    game._last_click_time = pygame.time.get_ticks()
    
    if current and current[0] == "player":
        for i, p in enumerate(ai_team):
            x_pos = 960
            y_pos = 150 + i * 200
            if pygame.Rect(x_pos, y_pos, 120, 120).collidepoint(pos) and p.alive:
                team, attacker = current
                
                # TC-36: Attack sound
                play_sfx('attack')
                
                dmg = attacker.attack(p)
                game.message = f"{attacker.name} dealt {dmg} damage to {p.name}!"
                
                # TC-37: Hit sound with delay
                if dmg > 0:
                    play_sfx('hit', 200)
                
                # TC-38: Defeat sound
                if not p.alive:
                    game.message += f" - {p.name} defeated!"
                    play_sfx('defeat')
                
                # TC-40: Coin sound
                if dmg > 0:
                    play_sfx('coin')
                
                return True
    return False

def handle_button_click(pos, game):
    """Handle button clicks (recruit, save)"""
    log_x, log_y = 480, 180
    log_h = 320
    button_y = log_y + log_h + 10
    
    # RECRUIT button
    recruit_rect = pygame.Rect(log_x, button_y, 150, 40)
    if recruit_rect.collidepoint(pos):
        return try_recruit(game)
    
    # SAVE button
    save_rect = pygame.Rect(log_x, button_y + 50, 150, 40)
    if save_rect.collidepoint(pos):
        from save_load import save_game
        success, msg = save_game(game)
        game.message = msg
        return False
    
    return False

def try_recruit(game):
    """TC-24 to TC-26: Try to recruit new unit"""
    total_coins = sum(u.coins for u in game.player_team)
    
    # TC-26: Check team limit
    if len(game.player_team) >= 6:
        game.message = "Team is full! (Max 6 units)"
        log("Recruit failed: Team full")
        return False
    
    # TC-25: Check coins
    if total_coins < 50:
        game.message = f"Not enough coins! Need 50, have {total_coins}"
        log("Recruit failed: Not enough coins")
        return False
    
    # TC-24: Recruit success
    # Deduct coins from team (distribute from richest first)
    remaining = 50
    for unit in sorted(game.player_team, key=lambda u: u.coins, reverse=True):
        if remaining <= 0:
            break
        deduct = min(unit.coins, remaining)
        unit.coins -= deduct
        remaining -= deduct
    
    # Create new unit
    prof = random.choice(["Warrior", "Tank"])
    char = random.choice(base_chars)
    new_unit = Unit(f"Recruit{len(game.player_team)+1}", prof, char[2])
    game.player_team.append(new_unit)
    
    # TC-43: Recruit sound
    play_sfx('recruit')
    
    game.message = f"Recruited {new_unit.name} ({prof}) for 50 coins!"
    log(f"Unit recruited: {new_unit.name} ({prof})")
    
    return False  # Don't count as attack

def create_turns(player_team, ai_team):
    """Creates turn order"""
    turn_order = []
    for i in range(min(len(player_team), len(ai_team))):
        if i < len(player_team):
            turn_order.append(("player", player_team[i]))
        if i < len(ai_team):
            turn_order.append(("ai", ai_team[i]))
    
    # Add remaining units
    for i in range(min(len(player_team), len(ai_team)), max(len(player_team), len(ai_team))):
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
                game.message = f"Your turn: {unit.name}! Select a target"
                log(f"Player turn: {unit.name}")
            else:
                game.message = f"AI turn: {unit.name}"
                log(f"AI turn: {unit.name}")
                pygame.time.wait(400)
                ai_turn(current, game)
            return turn_idx, current
        attempts += 1
    return turn_idx, None

def ai_turn(current, game):
    """AI turn logic"""
    team, attacker = current
    targets = [p for p in game.player_team if p.alive]
    if not targets: 
        return
    
    # TC-18: AI targets lowest HP
    target = min(targets, key=lambda x: x.hp)
    
    # TC-36: Attack sound
    play_sfx('attack')
    
    dmg = attacker.attack(target)
    game.message = f"{attacker.name} attacked {target.name}! ({dmg} damage)"
    
    # TC-37: Hit sound
    if dmg > 0:
        play_sfx('hit', 200)
    
    # TC-38: Defeat sound
    if not target.alive:
        game.message += f" - {target.name} defeated!"
        play_sfx('defeat')