import pygame
from config import SCREEN_WIDTH, GREEN, RED, YELLOW, BLACK, WHITE
from utils import log, event_log

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
    log_w, log_h = 320, 420
    
    pygame.draw.rect(screen, (20, 20, 30), (log_x, log_y, log_w, log_h))
    pygame.draw.rect(screen, YELLOW, (log_x, log_y, log_w, log_h), 2)
    
    f_log_title = pygame.font.Font(None, 24)
    log_title = f_log_title.render("⚔️ EVENT LOG ⚔️", True, YELLOW)
    screen.blit(log_title, (log_x + log_w//2 - log_title.get_width()//2, log_y + 10))
    
    f_log = pygame.font.Font(None, 16)
    log_start_y = log_y + 40
    line_height = 22
    max_lines = (log_h - 50) // line_height
    
    battle_logs = [l for l in event_log if any(x in l for x in ["ATTACK:", "defeated!", "LEVEL UP!", "turn:", "Battle Started"])]
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
        else:
            color = (200, 200, 200)
        
        log_line = f_log.render(msg_text, True, color)
        screen.blit(log_line, (log_x + 10, log_start_y + i * line_height))
    
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

def handle_click(pos, player_team, ai_team, current, game_state):
    """Processes attacks in battle"""
    if current and current[0] == "player":
        for i, p in enumerate(ai_team):
            x_pos = 960
            y_pos = 150 + i * 200
            if pygame.Rect(x_pos, y_pos, 120, 120).collidepoint(pos) and p.alive:
                team, attacker = current
                dmg = attacker.attack(p)
                game_state['message'] = f"{attacker.name} dealt {dmg} damage to {p.name}!"
                if not p.alive: 
                    game_state['message'] += f" - {p.name} defeated!"
                return True
    return False

def create_turns(player_team, ai_team):
    """Creates turn order"""
    turn_order = []
    for i in range(3):
        turn_order.append(("player", player_team[i]))
        turn_order.append(("ai", ai_team[i]))
    log("Turn order: P1,AI1,P2,AI2,P3,AI3")
    return turn_order

def next_turn(turn_order, turn_idx, game_state):
    """Advances to next turn"""
    attempts = 0
    while attempts < len(turn_order):
        turn_idx = (turn_idx + 1) % len(turn_order)
        team, unit = turn_order[turn_idx]
        if unit.alive:
            current = (team, unit)
            if team == "player":
                game_state['message'] = f"Your turn: {unit.name}! Select a target"
                log(f"Player turn: {unit.name}")
            else:
                game_state['message'] = f"AI turn: {unit.name}"
                log(f"AI turn: {unit.name}")
                pygame.time.wait(400)
                ai_turn(current, game_state)
            return turn_idx, current
        attempts += 1
    return turn_idx, None

def ai_turn(current, game_state):
    """AI turn logic"""
    team, attacker = current
    targets = [p for p in game_state['player_team'] if p.alive]
    if not targets: 
        return
    
    target = min(targets, key=lambda x: x.hp)
    dmg = attacker.attack(target)
    game_state['message'] = f"{attacker.name} attacked {target.name}! ({dmg} damage)"
    if not target.alive: 
        game_state['message'] += f" - {target.name} defeated!"