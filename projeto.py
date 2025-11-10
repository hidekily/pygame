import pygame
import sys
import random
import os
from datetime import datetime

# Screen dimensions ================================================================================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 780

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Turn-Based Battle Game")
clock = pygame.time.Clock()

# Colors ================================================================================
WHITE, BLACK, GREEN, RED, YELLOW, GRAY, DARK_GRAY = (255,255,255), (0,0,0), (0,200,0), (200,0,0), (255,200,0), (100,100,100), (40,40,40)

# ============== BACKGROUNDS - CHANGE IMAGES HERE ==============
MENU_BG = "./images/bg/menu.jpg"
BATTLE_BG = "./images/bg/battlebg.jpg"
SELECTION_BG = "./images/bg/selection.jpg"

def load_bg(path):
    if os.path.exists(path):
        try:
            bg = pygame.image.load(path)
            return pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except: 
            print(f"Error loading: {path}")
    return None

menu_bg = load_bg(MENU_BG)
battle_bg = load_bg(BATTLE_BG)
selection_bg = load_bg(SELECTION_BG)
# ==============================================================

# States ================================================================================
MENU, SELECTION, BATTLE, END = 0, 1, 2, 3
state = MENU

event_log = []

def log(msg):
    entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    event_log.append(entry)
    print(entry)

def save_log():
    try:
        with open("game_event_log.txt", "w", encoding="utf-8") as f:
            f.write("=== TURN-BASED BATTLE GAME - EVENT LOG ===\n\n")
            for e in event_log: 
                f.write(e + "\n")
        log("Event log saved")
    except Exception as e: 
        print(f"Error saving log: {e}")

class Unit:
    def __init__(self, name, prof, sprite_path=None):
        self.name, self.prof, self.rank, self.exp = name, prof, 1, 0
        self.hp_max = self.hp = 100
        
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
        dmg = max(0, self.atk - target.defense + random.randint(-5, 10))
        target.hp = max(0, target.hp - dmg)
        target.alive = target.hp > 0
        
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
        self.exp += exp
        log(f"{self.name} +{exp} EXP (Total: {self.exp})")
        if self.exp >= 100:
            self.rank += 1
            self.exp -= 100
            log(f"LEVEL UP! {self.name} -> Rank {self.rank}!")
    
    def draw(self, x, y, show_hover=False, is_turn=False):
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
            f"Experience: {self.exp}/100"
        ]
        for i, stat in enumerate(stats):
            stat_text = f_stats.render(stat, True, WHITE)
            screen.blit(stat_text, (x + sprite_size//2 - stat_text.get_width()//2, stats_y + i*18))
        
        return rect

# Character sprites ================================================================================
base_chars = [
    ("Warrior", "Warrior", "./images/sprites/warrior.png"),
    ("Warrior", "Archer", "./images/sprites/archer.png"),
    ("Warrior", "Assassin", "./images/sprites/assassin.webp"),
    ("Tank", "Paladin", "./images/sprites/knight.png"),
    ("Tank", "Tank", "./images/sprites/tanker.png"),
    ("Tank", "Guardian", "./images/sprites/guardian.png")
]
# ==============================================================

player_team, ai_team = [], []
selected = [False] * 6
message = ""
turn_order, turn_idx, current = [], 0, None

def reset():
    global player_team, ai_team, selected, message, state, turn_order, turn_idx, current, event_log
    player_team, ai_team, selected = [], [], [False]*6
    message, state, turn_order, turn_idx, current, event_log = "", MENU, [], 0, None, []
    log("Game Reset")

def create_turns():
    global turn_order
    turn_order = []
    for i in range(3):
        turn_order.append(("player", player_team[i]))
        turn_order.append(("ai", ai_team[i]))
    log("Turn order: P1,AI1,P2,AI2,P3,AI3")

def next_turn():
    global turn_idx, current, message
    attempts = 0
    while attempts < len(turn_order):
        turn_idx = (turn_idx + 1) % len(turn_order)
        team, unit = turn_order[turn_idx]
        if unit.alive:
            current = (team, unit)
            if team == "player":
                message = f"Your turn: {unit.name}! Select a target"
                log(f"Player turn: {unit.name}")
            else:
                message = f"AI turn: {unit.name}"
                log(f"AI turn: {unit.name}")
                pygame.time.wait(400)
                ai_turn()
            return
        attempts += 1

def ai_turn():
    global message
    team, attacker = current
    targets = [p for p in player_team if p.alive]
    if not targets: 
        return
    
    target = min(targets, key=lambda x: x.hp)
    dmg = attacker.attack(target)
    message = f"{attacker.name} attacked {target.name}! ({dmg} damage)"
    if not target.alive: 
        message += f" - {target.name} defeated!"
    
    check_end()
    if state == BATTLE:
        pygame.time.wait(400)
        next_turn()

def check_end():
    global state, message
    p_alive = sum(1 for p in player_team if p.alive)
    ai_alive = sum(1 for p in ai_team if p.alive)
    
    if p_alive == 0:
        state, message = END, "AI TEAM WINS!"
        log("GAME OVER: AI Victory")
        save_log()
    elif ai_alive == 0:
        state, message = END, "PLAYER TEAM WINS!"
        log("GAME OVER: Player Victory")
        save_log()

def btn(x, y, w, h, txt, col):
    m = pygame.mouse.get_pos()
    r = pygame.Rect(x, y, w, h)
    if r.collidepoint(m): 
        col = tuple(min(c+30, 255) for c in col)
    pygame.draw.rect(screen, col, r)
    pygame.draw.rect(screen, WHITE, r, 2)
    f = pygame.font.Font(None, 28)
    t = f.render(txt, True, WHITE)
    screen.blit(t, (x+w//2-t.get_width()//2, y+h//2-t.get_height()//2))
    return r

running = True
log("Game Started")

while running:
    screen.fill(BLACK)
    
    # Draw backgrounds ==========================================
    if state == MENU and menu_bg: 
        screen.blit(menu_bg, (0, 0))
    elif state == SELECTION and selection_bg: 
        screen.blit(selection_bg, (0, 0))
    elif state == BATTLE and battle_bg: 
        screen.blit(battle_bg, (0, 0))
    
    m_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_log()
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            
            if state == MENU:
                if pygame.Rect(540, 400, 200, 60).collidepoint(pos):
                    state = SELECTION
                    log("Entered selection")
            
            elif state == SELECTION:
                for i in range(6):
                    col, row = i % 3, i // 3
                    x_pos = 180 + col * 320
                    y_pos = 180 + row * 260
                    if pygame.Rect(x_pos, y_pos, 120, 120).collidepoint(pos):
                        if selected[i]:
                            selected[i] = False
                            prof, name, spr = base_chars[i]
                            player_team = [p for p in player_team if p.name != name]
                            log(f"Deselected: {name}")
                        elif len(player_team) < 3:
                            selected[i] = True
                            prof, name, spr = base_chars[i]
                            player_team.append(Unit(name, prof, spr))
                            log(f"Selected: {name} ({prof})")
                
                if len(player_team) == 3 and pygame.Rect(540, 660, 200, 50).collidepoint(pos):
                    log("AI Team Setup")
                    for i in range(3):
                        prof = random.choice(["Warrior", "Tank"])
                        ai_sprite = random.choice(base_chars)[2]
                        ai_team.append(Unit(f"IA{i+1}", prof, ai_sprite))
                    
                    create_turns()
                    turn_idx, state = -1, BATTLE
                    log("Battle Started!")
                    next_turn()
            
            elif state == BATTLE:
                if current and current[0] == "player":
                    for i, p in enumerate(ai_team):
                        x_pos = 960
                        y_pos = 150 + i * 200
                        if pygame.Rect(x_pos, y_pos, 120, 120).collidepoint(pos) and p.alive:
                            team, attacker = current
                            dmg = attacker.attack(p)
                            message = f"{attacker.name} dealt {dmg} damage to {p.name}!"
                            if not p.alive: 
                                message += f" - {p.name} defeated!"
                            check_end()
                            if state == BATTLE:
                                pygame.time.wait(400)
                                next_turn()
                            break
            
            elif state == END:
                if pygame.Rect(400, 480, 180, 50).collidepoint(pos): 
                    reset()
                elif pygame.Rect(700, 480, 180, 50).collidepoint(pos):
                    reset()
                    state = SELECTION
    
    # DRAW =================================================================================
    if state == MENU:
        f1 = pygame.font.Font(None, 80)
        t = f1.render("TURN-BASED BATTLE", True, BLACK)
        screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 200))
        
        f2 = pygame.font.Font(None, 28)
        t2 = f2.render("ITGP2008 Assignment", True, BLACK)
        screen.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, 290))
        
        btn(540, 400, 200, 60, "START GAME", GREEN)
    
    elif state == SELECTION:
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
            btn(540, 660, 200, 50, "START BATTLE", (50,100,200))
    
    elif state == BATTLE:
        f = pygame.font.Font(None, 44)
        t = f.render("⚔️ BATTLE ⚔️", True, YELLOW)
        screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 15))
        
        # OUR TEAM ===============================================================================
        f2 = pygame.font.Font(None, 28)
        screen.blit(f2.render("YOUR TEAM", True, GREEN), (80, 80))
        for i, p in enumerate(player_team):
            is_turn = current and current[0]=="player" and current[1]==p
            p.draw(80, 150 + i * 200, False, is_turn)
        
        # AI TEAM =======================================================================================
        screen.blit(f2.render("AI TEAM", True, RED), (1050, 80))
        p_turn = current and current[0]=="player"
        for i, p in enumerate(ai_team):
            p.hover = False
            if pygame.Rect(960, 150 + i*200, 120, 120).collidepoint(m_pos) and p_turn and p.alive:
                p.hover = True
            p.draw(960, 150 + i * 200, p_turn)
        
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
    
    elif state == END:
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
        
        btn(400, 480, 180, 50, "MAIN MENU", (50,100,200))
        btn(700, 480, 180, 50, "PLAY AGAIN", GREEN)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()