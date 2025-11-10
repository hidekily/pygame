import pygame
import sys
import random
import os
from datetime import datetime

pygame.init()
screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("Turn-Based Battle Game")
clock = pygame.time.Clock()

# Colors
WHITE, BLACK, GREEN, RED, YELLOW, GRAY = (255,255,255), (0,0,0), (0,200,0), (200,0,0), (255,200,0), (100,100,100)

# ============== BACKGROUNDS - CHANGE IMAGES HERE ==============
# Put your background images in the same folder as this script
MENU_BG = "menu_bg.png"      # <-- CHANGE THIS to your menu background filename
BATTLE_BG = "battle_bg.png"  # <-- CHANGE THIS to your battle background filename

def load_bg(path):
    if os.path.exists(path):
        try:
            bg = pygame.image.load(path)
            return pygame.transform.scale(bg, (1200, 700))
        except: pass
    return None

menu_bg = load_bg(MENU_BG)
battle_bg = load_bg(BATTLE_BG)
# ==============================================================

# States
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
            for e in event_log: f.write(e + "\n")
        log("Event log saved")
    except Exception as e: print(f"Error: {e}")

class Unit:
    def __init__(self, name, prof, sprite_path=None):
        self.name, self.prof, self.rank, self.exp = name, prof, 1, 0
        self.hp_max = self.hp = 100
        
        if prof == "Warrior":
            self.atk, self.defense = random.randint(5, 20), random.randint(1, 10)
        else:  # Tanker
            self.atk, self.defense = random.randint(1, 10), random.randint(5, 15)
        
        self.alive = True
        self.sprite = None
        if sprite_path and os.path.exists(sprite_path):
            try:
                self.sprite = pygame.image.load(sprite_path)
                self.sprite = pygame.transform.scale(self.sprite, (100, 100))
            except: pass
        
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
        if not target.alive: log(f"{target.name} defeated!")
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
        
        rect = pygame.Rect(x, y, 100, 100)
        
        if is_turn and self.alive:
            pulse = abs((pygame.time.get_ticks() % 800) / 400 - 1) * 4 + 2
            pygame.draw.rect(screen, YELLOW, (x-5, y-5, 110, 110), int(pulse))
        
        if show_hover and self.hover and self.alive:
            pygame.draw.rect(screen, YELLOW, (x-3, y-3, 106, 106), 3)
        if self.attacked: pygame.draw.rect(screen, RED, (x-2, y-2, 104, 104), 5)
        if self.attacking: pygame.draw.rect(screen, GREEN, (x-2, y-2, 104, 104), 5)
        
        if self.sprite: screen.blit(self.sprite, (x, y))
        else: pygame.draw.rect(screen, GRAY if not self.alive else (200,50,50) if self.prof=="Warrior" else (100,70,40), rect)
        
        pygame.draw.rect(screen, BLACK, rect, 3)
        
        f = pygame.font.Font(None, 20)
        screen.blit(f.render(self.name[:12], True, WHITE), (x - 120, y + 10))
        screen.blit(f.render(f"Lv.{self.rank}", True, YELLOW), (x - 120, y + 30))
        
        bx, by = x + 112, y + 20
        pygame.draw.rect(screen, RED, (bx, by, 110, 10))
        pygame.draw.rect(screen, GREEN, (bx, by, int((self.hp/self.hp_max)*110), 10))
        pygame.draw.rect(screen, BLACK, (bx, by, 110, 10), 2)
        
        f2 = pygame.font.Font(None, 16)
        screen.blit(f2.render(f"HP:{self.hp}/{self.hp_max}", True, WHITE), (bx, by+12))
        for i, s in enumerate([f"ATK:{self.atk}", f"DEF:{self.defense}", f"EXP:{self.exp}/100"]):
            screen.blit(f2.render(s, True, WHITE), (bx, by+30+i*16))
        return rect

# ============== CHARACTER SPRITES - CHANGE HERE ==============
# Format: (Profession, Name, sprite_filename)
# Put your sprite images in a "sprites" folder
base_chars = [
    ("Warrior", "Warrior", "sprites/warrior.png"),    # <-- CHANGE sprite path
    ("Warrior", "Archer", "sprites/archer.png"),      # <-- CHANGE sprite path
    ("Warrior", "Assassin", "sprites/assassin.png"),  # <-- CHANGE sprite path
    ("Tanker", "Paladin", "sprites/paladin.png"),     # <-- CHANGE sprite path
    ("Tanker", "Tank", "sprites/tank.png"),           # <-- CHANGE sprite path
    ("Tanker", "Guardian", "sprites/guardian.png")    # <-- CHANGE sprite path
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
                message = f"Your turn: {unit.name}! Select target"
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
    if not targets: return
    
    target = min(targets, key=lambda x: x.hp)
    dmg = attacker.attack(target)
    message = f"{attacker.name} attacked {target.name}! ({dmg} dmg)"
    if not target.alive: message += f" - {target.name} defeated!"
    
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
    if r.collidepoint(m): col = tuple(min(c+30, 255) for c in col)
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
    
    # Draw backgrounds
    if state == MENU and menu_bg: screen.blit(menu_bg, (0, 0))
    elif state == BATTLE and battle_bg: screen.blit(battle_bg, (0, 0))
    
    m_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_log()
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            
            if state == MENU:
                if pygame.Rect(500, 350, 200, 60).collidepoint(pos):
                    state = SELECTION
                    log("Entered selection")
            
            elif state == SELECTION:
                for i in range(6):
                    col, row = i % 3, i // 3
                    x, y = 200 + col * 280, 180 + row * 180
                    if pygame.Rect(x, y, 100, 100).collidepoint(pos):
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
                
                if len(player_team) == 3 and pygame.Rect(500, 580, 200, 50).collidepoint(pos):
                    log("AI Team Setup")
                    for _ in range(3):
                        prof = random.choice(["Warrior", "Tanker"])
                        # ============== AI SPRITE - CHANGE HERE ==============
                        # By default, AI uses random sprites from base_chars
                        # To give AI specific sprites, replace the line below:
                        ai_sprite = random.choice(base_chars)[2]  # <-- CHANGE: Use specific sprite path like "sprites/enemy1.png"
                        # ====================================================
                        ai_team.append(Unit(f"AI{random.randint(10,99)}", prof, ai_sprite))
                    
                    create_turns()
                    turn_idx, state = -1, BATTLE
                    log("Battle Started!")
                    next_turn()
            
            elif state == BATTLE:
                if current and current[0] == "player":
                    for i, p in enumerate(ai_team):
                        x, y = 800, 120 + i * 180
                        if pygame.Rect(x, y, 100, 100).collidepoint(pos) and p.alive:
                            team, attacker = current
                            dmg = attacker.attack(p)
                            message = f"{attacker.name} dealt {dmg} dmg to {p.name}!"
                            if not p.alive: message += f" - {p.name} defeated!"
                            check_end()
                            if state == BATTLE:
                                pygame.time.wait(400)
                                next_turn()
                            break
            
            elif state == END:
                if pygame.Rect(350, 420, 180, 50).collidepoint(pos): reset()
                elif pygame.Rect(670, 420, 180, 50).collidepoint(pos):
                    reset()
                    state = SELECTION
    
    # DRAW
    if state == MENU:
        f1 = pygame.font.Font(None, 80)
        t = f1.render("TURN-BASED BATTLE", True, YELLOW)
        screen.blit(t, (600-t.get_width()//2, 150))
        f2 = pygame.font.Font(None, 28)
        t2 = f2.render("ITGP2008 Assignment", True, WHITE)
        screen.blit(t2, (600-t2.get_width()//2, 240))
        btn(500, 350, 200, 60, "START GAME", GREEN)
    
    elif state == SELECTION:
        f = pygame.font.Font(None, 44)
        t = f.render("SELECT YOUR TEAM (3 UNITS)", True, WHITE)
        screen.blit(t, (600-t.get_width()//2, 40))
        c = f.render(f"{len(player_team)}/3 Selected", True, GREEN if len(player_team)==3 else WHITE)
        screen.blit(c, (600-c.get_width()//2, 100))
        
        for i in range(6):
            col, row = i % 3, i // 3
            x, y = 200 + col * 280, 180 + row * 180
            prof, name, spr = base_chars[i]
            
            color = (200,50,50) if prof=="Warrior" else (100,70,40)
            pygame.draw.rect(screen, color, (x, y, 100, 100))
            pygame.draw.rect(screen, BLACK, (x, y, 100, 100), 3)
            
            if pygame.Rect(x, y, 100, 100).collidepoint(m_pos):
                pygame.draw.rect(screen, YELLOW, (x-2, y-2, 104, 104), 3)
            if selected[i]:
                pygame.draw.rect(screen, YELLOW, (x-4, y-4, 108, 108), 5)
            
            f1, f2 = pygame.font.Font(None, 20), pygame.font.Font(None, 14)
            screen.blit(f1.render(name, True, WHITE), (x+50-f1.render(name,True,WHITE).get_width()//2, y+35))
            screen.blit(f2.render(prof, True, GRAY), (x+50-f2.render(prof,True,WHITE).get_width()//2, y+55))
        
        if len(player_team) == 3:
            btn(500, 580, 200, 50, "START BATTLE", (50,100,200))
    
    elif state == BATTLE:
        f = pygame.font.Font(None, 44)
        t = f.render("⚔️ BATTLE ⚔️", True, YELLOW)
        screen.blit(t, (600-t.get_width()//2, 15))
        
        f2 = pygame.font.Font(None, 28)
        screen.blit(f2.render("YOUR TEAM", True, GREEN), (40, 80))
        for i, p in enumerate(player_team):
            is_turn = current and current[0]=="player" and current[1]==p
            p.draw(180, 120+i*180, False, is_turn)
        
        screen.blit(f2.render("AI TEAM", True, RED), (970, 80))
        p_turn = current and current[0]=="player"
        for i, p in enumerate(ai_team):
            p.hover = False
            if pygame.Rect(800, 120+i*180, 100, 100).collidepoint(m_pos) and p_turn and p.alive:
                p.hover = True
            p.draw(800, 120+i*180, p_turn)
        
        f3 = pygame.font.Font(None, 24)
        msg = f3.render(message[:70], True, WHITE)
        mr = msg.get_rect(center=(600, 650))
        pygame.draw.rect(screen, BLACK, (mr.x-10, mr.y-5, mr.width+20, mr.height+10))
        pygame.draw.rect(screen, YELLOW, (mr.x-10, mr.y-5, mr.width+20, mr.height+10), 2)
        screen.blit(msg, mr)
        
        if current:
            t, c = current
            col = GREEN if t=="player" else RED
            txt = f.render(f"TURN: {c.name}", True, col)
            tr = txt.get_rect(center=(600, 60))
            pygame.draw.rect(screen, BLACK, (tr.x-12, tr.y-6, tr.width+24, tr.height+12))
            pygame.draw.rect(screen, col, (tr.x-12, tr.y-6, tr.width+24, tr.height+12), 3)
            screen.blit(txt, tr)
    
    elif state == END:
        f = pygame.font.Font(None, 70)
        col = GREEN if "PLAYER" in message else RED
        t = f.render(message, True, col)
        screen.blit(t, (600-t.get_width()//2, 220))
        
        f2 = pygame.font.Font(None, 28)
        p_alive = sum(1 for p in player_team if p.alive)
        ai_alive = sum(1 for p in ai_team if p.alive)
        t2 = f2.render(f"Final: Your Team {p_alive} x {ai_alive} AI Team", True, WHITE)
        screen.blit(t2, (600-t2.get_width()//2, 320))
        t3 = f2.render("Log saved: game_event_log.txt", True, GRAY)
        screen.blit(t3, (600-t3.get_width()//2, 360))
        
        btn(350, 420, 180, 50, "MAIN MENU", (50,100,200))
        btn(670, 420, 180, 50, "PLAY AGAIN", GREEN)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()