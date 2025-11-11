import pygame

# Screen dimensions ================================================================================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 780

# Colors ================================================================================
WHITE, BLACK, GREEN, RED, YELLOW, GRAY, DARK_GRAY = (255,255,255), (0,0,0), (0,200,0), (200,0,0), (255,200,0), (100,100,100), (40,40,40)

# States ================================================================================
MENU, SELECTION, BATTLE, END = 0, 1, 2, 3

# ============== BACKGROUNDS - CHANGE IMAGES HERE ==============
MENU_BG = "./images/bg/menu.jpg"
BATTLE_BG = "./images/bg/battlebg.jpg"
SELECTION_BG = "./images/bg/selection.jpg"

# ============== MUSIC - CHANGE MUSIC HERE ==============
Menu_music = "./sounds/menu.mp3"
Selection_music ="./sounds/selection.mp3"
Battle_music ="./sounds/battle.mp3"
Win_music ="./sounds/win.mp3"
Loss_music ="./sounds/loss.mp3"

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