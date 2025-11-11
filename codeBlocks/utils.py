import pygame
import os
from datetime import datetime
from config import WHITE

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

def load_bg(path, width, height):
    if os.path.exists(path):
        try:
            bg = pygame.image.load(path)
            return pygame.transform.scale(bg, (width, height))
        except: 
            print(f"Error loading: {path}")
    return None

def play_music(file_name, loop=-1):
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.play(loop)
        log(f"Playing music: {file_name}")
    except Exception as e:
        log(f"Error playing music: {e}")

def btn(screen, x, y, w, h, txt, col):
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