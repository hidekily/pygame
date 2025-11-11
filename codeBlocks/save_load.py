import json
import os
from utils import log
from config import base_chars

def save_game(game):
    """TC-27: Save game to JSON file"""
    try:
        # Get sprite paths for units
        def get_sprite_path(unit):
            for prof, name, sprite in base_chars:
                if unit.name == name:
                    return sprite
            return None
        
        data = {
            'version': '1.0',
            'state': game.state,
            'turn_idx': game.turn_idx,
            'message': game.message,
            'player_team': [
                {
                    **unit.to_dict(),
                    'sprite_path': get_sprite_path(unit)
                }
                for unit in game.player_team
            ],
            'ai_team': [
                {
                    **unit.to_dict(),
                    'sprite_path': get_sprite_path(unit)
                }
                for unit in game.ai_team
            ],
            'current': {
                'team': game.current[0] if game.current else None,
                'unit_name': game.current[1].name if game.current else None
            } if game.current else None
        }
        
        with open('game_save.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        log("Game saved successfully!")
        return True, "Game saved to game_save.json"
        
    except Exception as e:
        log(f"Error saving game: {e}")
        return False, f"Save failed: {e}"

def load_game(game):
    """TC-29: Load game from JSON file"""
    try:
        # TC-30: Handle missing save file
        if not os.path.exists('game_save.json'):
            log("No save file found")
            return False, "No save found"
        
        with open('game_save.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # TC-57: Handle invalid/corrupted save file
        if 'version' not in data:
            log("Invalid save file format")
            return False, "Invalid save file"
        
        # Import Unit here to avoid circular import
        from unit import Unit
        
        # Restore player team
        game.player_team = []
        for unit_data in data['player_team']:
            sprite = unit_data.get('sprite_path')
            unit = Unit.from_dict(unit_data, sprite)
            game.player_team.append(unit)
        
        # Restore AI team
        game.ai_team = []
        for unit_data in data['ai_team']:
            sprite = unit_data.get('sprite_path')
            unit = Unit.from_dict(unit_data, sprite)
            game.ai_team.append(unit)
        
        # Restore game state
        game.state = data['state']
        game.turn_idx = data['turn_idx']
        game.message = data['message']
        
        # Restore turn order
        from battle import create_turns
        game.turn_order = create_turns(game.player_team, game.ai_team)
        
        # Restore current turn
        if data['current'] and data['current']['team']:
            team_name = data['current']['team']
            unit_name = data['current']['unit_name']
            
            # Find the unit
            team = game.player_team if team_name == 'player' else game.ai_team
            for unit in team:
                if unit.name == unit_name:
                    game.current = (team_name, unit)
                    break
        else:
            game.current = None
        
        log("Game loaded successfully!")
        return True, "Game loaded from save file"
        
    except json.JSONDecodeError:
        log("Corrupted save file")
        return False, "Save file corrupted"
    except Exception as e:
        log(f"Error loading game: {e}")
        return False, f"Load failed: {e}"

def has_save_file():
    """Check if save file exists"""
    return os.path.exists('game_save.json')