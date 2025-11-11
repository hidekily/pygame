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
    
    # OUR TEAM (supports 6 units now)
    f2 = pygame.font.Font(None, 28)
    screen.blit(f2.render("YOUR TEAM", True, GREEN), (80, 80))
    for i, p in enumerate(player_team):
        row = i // 3  # 3 per row
        col = i % 3
        x = 80 + col * 250
        y = 150 + row * 200
        is_turn = current and current[0]=="player" and current[1]==p
        p.draw(screen, x, y, False, is_turn)
    
    # AI TEAM
    screen.blit(f2.render("AI TEAM", True, RED), (1050, 80))
    p_turn = current and current[0]=="player"
    for i, p in enumerate(ai_team):
        p.hover = False
        if pygame.Rect(960, 150 + i*200, 120, 120).collidepoint(m_pos) and p_turn and p.alive:
            p.hover = True
        p.draw(screen, 960, 150 + i * 200, p_turn)
    
    # BATTLE SHOP PANEL (centered, bigger)
    shop_x, shop_y = 450, 150
    shop_w, shop_h = 380, 500
    
    pygame.draw.rect(screen, (20, 20, 40), (shop_x, shop_y, shop_w, shop_h))
    pygame.draw.rect(screen, YELLOW, (shop_x, shop_y, shop_w, shop_h), 3)
    
    f_shop_title = pygame.font.Font(None, 32)
    shop_title = f_shop_title.render("🏪 BATTLE SHOP 🏪", True, YELLOW)
    screen.blit(shop_title, (shop_x + shop_w//2 - shop_title.get_width()//2, shop_y + 10))
    
    # Show total coins
    total_coins = sum(u.coins for u in player_team)
    f_coins = pygame.font.Font(None, 28)
    coins_text = f_coins.render(f"💰 Team Coins: {total_coins}", True, (255, 215, 0))
    screen.blit(coins_text, (shop_x + shop_w//2 - coins_text.get_width()//2, shop_y + 45))
    
    # Shop Items
    item_y = shop_y + 85
    item_height = 65
    
    # Item 1: Healing Potion
    can_heal = total_coins >= 30
    heal_color = GREEN if can_heal else (80, 80, 80)
    btn(screen, shop_x + 10, item_y, shop_w - 20, item_height, 
        "❤️ HEALING POTION (30💰)", heal_color, can_heal)
    f_desc = pygame.font.Font(None, 18)
    desc = f_desc.render("Restore 40 HP to selected unit", True, WHITE if can_heal else (100, 100, 100))
    screen.blit(desc, (shop_x + shop_w//2 - desc.get_width()//2, item_y + item_height - 18))
    
    # Item 2: Attack Buff
    item_y += item_height + 10
    can_atk = total_coins >= 40
    atk_color = (255, 100, 100) if can_atk else (80, 80, 80)
    btn(screen, shop_x + 10, item_y, shop_w - 20, item_height, 
        "⚔️ ATTACK BOOST (40💰)", atk_color, can_atk)
    desc = f_desc.render("Permanently +5 ATK to selected unit", True, WHITE if can_atk else (100, 100, 100))
    screen.blit(desc, (shop_x + shop_w//2 - desc.get_width()//2, item_y + item_height - 18))
    
    # Item 3: Defense Buff
    item_y += item_height + 10
    can_def = total_coins >= 40
    def_color = (100, 150, 255) if can_def else (80, 80, 80)
    btn(screen, shop_x + 10, item_y, shop_w - 20, item_height, 
        "🛡️ DEFENSE BOOST (40💰)", def_color, can_def)
    desc = f_desc.render("Permanently +3 DEF to selected unit", True, WHITE if can_def else (100, 100, 100))
    screen.blit(desc, (shop_x + shop_w//2 - desc.get_width()//2, item_y + item_height - 18))
    
    # Item 4: Recruit
    item_y += item_height + 10
    can_recruit = total_coins >= 50 and len(player_team) < 6
    recruit_color = (150, 255, 150) if can_recruit else (80, 80, 80)
    btn(screen, shop_x + 10, item_y, shop_w - 20, item_height, 
        "👤 RECRUIT UNIT (50💰)", recruit_color, can_recruit)
    desc = f_desc.render("Add new unit to battle immediately!", True, WHITE if can_recruit else (100, 100, 100))
    screen.blit(desc, (shop_x + shop_w//2 - desc.get_width()//2, item_y + item_height - 18))
    
    # Item 5: Save Game
    item_y += item_height + 10
    btn(screen, shop_x + 10, item_y, shop_w - 20, 50, "💾 SAVE GAME", (50, 100, 200))
    
    # Event Log (smaller, at bottom)
    log_x, log_y = 450, 670
    log_w, log_h = 380, 90
    
    pygame.draw.rect(screen, (20, 20, 30), (log_x, log_y, log_w, log_h))
    pygame.draw.rect(screen, YELLOW, (log_x, log_y, log_w, log_h), 2)
    
    f_log = pygame.font.Font(None, 14)
    battle_logs = [l for l in event_log if any(x in l for x in 
        ["ATTACK:", "defeated!", "LEVEL UP!", "Healing", "Boost", "recruited", "CRITICAL"])]
    recent_logs = battle_logs[-4:]  # Last 4 messages
    
    for i, log_entry in enumerate(recent_logs):
        if "] " in log_entry:
            msg_text = log_entry.split("] ", 1)[1][:50]
        else:
            msg_text = log_entry[:50]
        
        if "ATTACK:" in msg_text or "CRITICAL" in msg_text:
            color = (255, 150, 150)
        elif "defeated!" in msg_text:
            color = RED
        elif "LEVEL UP!" in msg_text:
            color = YELLOW
        elif "Healing" in msg_text or "Boost" in msg_text:
            color = (150, 255, 150)
        else:
            color = (200, 200, 200)
        
        log_line = f_log.render(msg_text, True, color)
        screen.blit(log_line, (log_x + 10, log_y + 10 + i * 18))
    
    # Message box
    f3 = pygame.font.Font(None, 24)
    msg = f3.render(message[:80], True, WHITE)
    mr = msg.get_rect(center=(SCREEN_WIDTH//2, 730))
    pygame.draw.rect(screen, BLACK, (mr.x-10, mr.y-5, mr.width+20, mr.height+10))
    pygame.draw.rect(screen, YELLOW, (mr.x-10, mr.y-5, mr.width+20, mr.height+10), 2)
    screen.blit(msg, mr)
    
    # Turn indicator
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
                
                play_sfx('attack')
                dmg = attacker.attack(p)
                game.message = f"{attacker.name} dealt {dmg} damage to {p.name}!"
                
                if dmg > 0:
                    play_sfx('hit', 200)
                
                if not p.alive:
                    game.message += f" - {p.name} defeated!"
                    play_sfx('defeat')
                
                if dmg > 0:
                    play_sfx('coin')
                
                return True
    return False

def handle_button_click(pos, game):
    """Handle shop button clicks"""
    shop_x, shop_y = 450, 150
    shop_w = 380
    item_y = shop_y + 85
    item_height = 65
    
    total_coins = sum(u.coins for u in game.player_team)
    
    # Healing Potion (30 coins)
    if pygame.Rect(shop_x + 10, item_y, shop_w - 20, item_height).collidepoint(pos):
        return buy_healing(game, total_coins)
    
    # Attack Boost (40 coins)
    item_y += item_height + 10
    if pygame.Rect(shop_x + 10, item_y, shop_w - 20, item_height).collidepoint(pos):
        return buy_attack_boost(game, total_coins)
    
    # Defense Boost (40 coins)
    item_y += item_height + 10
    if pygame.Rect(shop_x + 10, item_y, shop_w - 20, item_height).collidepoint(pos):
        return buy_defense_boost(game, total_coins)
    
    # Recruit (50 coins)
    item_y += item_height + 10
    if pygame.Rect(shop_x + 10, item_y, shop_w - 20, item_height).collidepoint(pos):
        return try_recruit(game, total_coins)
    
    # Save Game
    item_y += item_height + 10
    if pygame.Rect(shop_x + 10, item_y, shop_w - 20, 50).collidepoint(pos):
        from save_load import save_game
        success, msg = save_game(game)
        game.message = msg
        return False
    
    return False

def deduct_coins(player_team, amount):
    """Deduct coins from team (richest first)"""
    remaining = amount
    for unit in sorted(player_team, key=lambda u: u.coins, reverse=True):
        if remaining <= 0:
            break
        deduct = min(unit.coins, remaining)
        unit.coins -= deduct
        remaining -= deduct

def buy_healing(game, total_coins):
    """Buy healing potion - heals current unit"""
    if total_coins < 30:
        game.message = f"Need 30 coins! (Have {total_coins})"
        return False
    
    if not game.current or game.current[0] != "player":
        game.message = "Wait for your turn to use items!"
        return False
    
    unit = game.current[1]
    
    if unit.hp >= unit.hp_max:
        game.message = f"{unit.name} already at full HP!"
        return False
    
    deduct_coins(game.player_team, 30)
    heal_amount = 40
    old_hp = unit.hp
    unit.hp = min(unit.hp_max, unit.hp + heal_amount)
    actual_heal = unit.hp - old_hp
    
    play_sfx('levelup')  # Use levelup sound for healing
    game.message = f"❤️ {unit.name} healed {actual_heal} HP! ({old_hp}→{unit.hp})"
    log(f"Healing Potion used on {unit.name}: +{actual_heal} HP")
    
    return False

def buy_attack_boost(game, total_coins):
    """Buy attack boost - permanent +5 ATK"""
    if total_coins < 40:
        game.message = f"Need 40 coins! (Have {total_coins})"
        return False
    
    if not game.current or game.current[0] != "player":
        game.message = "Wait for your turn to use items!"
        return False
    
    unit = game.current[1]
    
    deduct_coins(game.player_team, 40)
    unit.atk += 5
    
    play_sfx('levelup')
    game.message = f"⚔️ {unit.name} Attack Boost! ATK: {unit.atk-5}→{unit.atk}"
    log(f"Attack Boost applied to {unit.name}: ATK +5 (Now: {unit.atk})")
    
    return False

def buy_defense_boost(game, total_coins):
    """Buy defense boost - permanent +3 DEF"""
    if total_coins < 40:
        game.message = f"Need 40 coins! (Have {total_coins})"
        return False
    
    if not game.current or game.current[0] != "player":
        game.message = "Wait for your turn to use items!"
        return False
    
    unit = game.current[1]
    
    deduct_coins(game.player_team, 40)
    unit.defense += 3
    
    play_sfx('levelup')
    game.message = f"🛡️ {unit.name} Defense Boost! DEF: {unit.defense-3}→{unit.defense}"
    log(f"Defense Boost applied to {unit.name}: DEF +3 (Now: {unit.defense})")
    
    return False

def try_recruit(game, total_coins):
    """Recruit new unit - NOW JOINS BATTLE IMMEDIATELY"""
    if len(game.player_team) >= 6:
        game.message = "Team is full! (Max 6 units)"
        return False
    
    if total_coins < 50:
        game.message = f"Need 50 coins! (Have {total_coins})"
        return False
    
    deduct_coins(game.player_team, 50)
    
    # Create new unit
    prof = random.choice(["Warrior", "Tank"])
    char = random.choice(base_chars)
    new_unit = Unit(f"Recruit{len(game.player_team)+1}", prof, char[2])
    game.player_team.append(new_unit)
    
    # ADD TO BATTLE IMMEDIATELY!
    game.turn_order.append(("player", new_unit))
    
    play_sfx('recruit')
    game.message = f"👤 {new_unit.name} ({prof}) joined the battle!"
    log(f"Unit recruited and joined battle: {new_unit.name} ({prof})")
    
    return False

def create_turns(player_team, ai_team):
    """Creates turn order"""
    turn_order = []
    for i in range(min(len(player_team), len(ai_team))):
        if i < len(player_team):
            turn_order.append(("player", player_team[i]))
        if i < len(ai_team):
            turn_order.append(("ai", ai_team[i]))
    
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
                game.message = f"Your turn: {unit.name}! Attack enemy or use shop"
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
    
    target = min(targets, key=lambda x: x.hp)
    
    play_sfx('attack')
    dmg = attacker.attack(target)
    game.message = f"{attacker.name} attacked {target.name}! ({dmg} damage)"
    
    if dmg > 0:
        play_sfx('hit', 200)
    
    if not target.alive:
        game.message += f" - {target.name} defeated!"
        play_sfx('defeat')