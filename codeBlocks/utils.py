import pygame
import os
from datetime import datetime
from config import WHITE

event_log = []

# Sound system state
music_enabled = True
sfx_enabled = True
music_volume = 0.5

# Preload sound effects (TC-48: Handle missing sounds)
sounds = {}
sound_files = {
    'attack': './sounds/attack.mp3',
    'hit': './sounds/hit.mp3',
    'defeat': './sounds/defeat.mp3',
    'levelup': './sounds/levelup.mp3',
    'coin': './sounds/coin.mp3',
    'click': './sounds/click.mp3',
    'select': './sounds/select.mp3',
    'recruit': './sounds/recruit.mp3'
}

def load_sounds():
    """Load all sound effects"""
    for name, path in sound_files.items():
        try:
            if os.path.exists(path):
                sounds[name] = pygame.mixer.Sound(path)
                sounds[name].set_volume(0.5)
            else:
                sounds[name] = None
                print(f"Sound not found: {path}")
        except Exception as e:
            sounds[name] = None
            print(f"Error loading {name}: {e}")

def play_sfx(sound_name, delay=0):
    """TC-36 to TC-43: Play sound effect with optional delay"""
    if not sfx_enabled or sound_name not in sounds or sounds[sound_name] is None:
        return
    
    try:
        if delay > 0:
            # TC-37: Hit sound with 200ms delay
            pygame.time.set_timer(pygame.USEREVENT + 1, delay, 1)
            # Store sound to play later
            pygame.event.post(pygame.event.Event(pygame.USEREVENT + 1, {'sound': sound_name}))
        else:
            sounds[sound_name].play()
    except Exception as e:
        log(f"Error playing sound {sound_name}: {e}")

def toggle_music():
    """TC-44: Toggle music on/off with M key"""
    global music_enabled
    music_enabled = not music_enabled
    
    if music_enabled:
        pygame.mixer.music.unpause()
        log("Music enabled")
    else:
        pygame.mixer.music.pause()
        log("Music disabled")
    
    return music_enabled

def toggle_sfx():
    """TC-45: Toggle sound effects with N key"""
    global sfx_enabled
    sfx_enabled = not sfx_enabled
    log(f"SFX {'enabled' if sfx_enabled else 'disabled'}")
    return sfx_enabled

def volume_up():
    """TC-46: Increase volume with + key"""
    global music_volume
    music_volume = min(1.0, music_volume + 0.1)
    pygame.mixer.music.set_volume(music_volume)
    log(f"Volume: {int(music_volume * 100)}%")
    return music_volume

def volume_down():
    """TC-47: Decrease volume with - key"""
    global music_volume
    music_volume = max(0.0, music_volume - 0.1)
    pygame.mixer.music.set_volume(music_volume)
    log(f"Volume: {int(music_volume * 100)}%")
    return music_volume

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
        if not music_enabled:
            return
        pygame.mixer.music.stop()
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.set_volume(music_volume)
        pygame.mixer.music.play(loop)
        log(f"Playing music: {file_name}")
    except Exception as e:
        log(f"Error playing music: {e}")

def btn(screen, x, y, w, h, txt, col, enabled=True):
    """Draw button with optional disabled state"""
    m = pygame.mouse.get_pos()
    r = pygame.Rect(x, y, w, h)
    
    # TC-41: Button click sound
    clicked = False
    if enabled and r.collidepoint(m):
        col = tuple(min(c+30, 255) for c in col)
        if pygame.mouse.get_pressed()[0]:
            clicked = True
            play_sfx('click')
    
    if not enabled:
        col = (80, 80, 80)  # Gray out disabled buttons
    
    pygame.draw.rect(screen, col, r)
    pygame.draw.rect(screen, WHITE, r, 2)
    f = pygame.font.Font(None, 28)
    t = f.render(txt, True, WHITE if enabled else (150, 150, 150))
    screen.blit(t, (x+w//2-t.get_width()//2, y+h//2-t.get_height()//2))
    return r, clicked