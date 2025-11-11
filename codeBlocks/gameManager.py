import random
from unit import Unit
from config import MENU, BATTLE, END, base_chars, Battle_music, Win_music, Loss_music
from utils import log, save_log, play_music
from battle import create_turns

class GameManager:
    def __init__(self):
        self.state = MENU
        self.player_team = []
        self.ai_team = []
        self.selected = [False] * 6
        self.message = ""
        self.turn_order = []
        self.turn_idx = 0
        self.current = None
    
    def reset(self):
        """Game Reset"""
        self.player_team = []
        self.ai_team = []
        self.selected = [False] * 6
        self.message = ""
        self.turn_order = []
        self.turn_idx = 0
        self.current = None
        self.state = MENU
        log("Game Reset")
    
    def start_battle(self):
        """Init BAttle"""
        log("AI Team Setup")
        for i in range(3):
            prof = random.choice(["Warrior", "Tank"])
            ai_sprite = random.choice(base_chars)[2]
            self.ai_team.append(Unit(f"IA{i+1}", prof, ai_sprite))
        
        self.turn_order = create_turns(self.player_team, self.ai_team)
        self.turn_idx = -1
        self.state = BATTLE
        log("Battle Started!")
        play_music(Battle_music)
    
    def check_end(self):
        """Verify Battle"""
        p_alive = sum(1 for p in self.player_team if p.alive)
        ai_alive = sum(1 for p in self.ai_team if p.alive)
        
        if p_alive == 0:
            self.state = END
            self.message = "AI TEAM WINS!"
            log("GAME OVER: AI Victory")
            play_music(Loss_music)
            save_log()
            
        elif ai_alive == 0:
            self.state = END
            self.message = "PLAYER TEAM WINS!"
            log("GAME OVER: Player Victory")
            play_music(Win_music)
            save_log()
    
    def get_game_state(self):
        """Return current game state"""
        return {
            'player_team': self.player_team,
            'ai_team': self.ai_team,
            'message': self.message
        }