# ==============================================================================
# src/game/game_state.py
# KORRIGIERT: Schub und Navigation werden nach einer Herausforderung nicht mehr zurückgesetzt.
# ==============================================================================
import random
from typing import List, Optional, Set
from src.core.player import Player
from src.core.tasks import ChallengeCard
from src.game.decks import create_challenge_deck_phase1

# Phase Constants
SETUP_SCREEN = "SetupScreen"
VERFALLSPHASE = "Verfallsphase"
ENERGIEPHASE = "Energiephase"
AKTIONSPHASE = "Aktionsphase"
AUFLOESUNGSPHASE = "Auflösungsphase"
VORBEREITUNGSPHASE = "Vorbereitungsphase"
GAME_OVER = "GameOver"

class GameState:
    """Manages the entire state of the game using the energy system."""
    def __init__(self):
        self.current_phase = SETUP_SCREEN
        self.players: List[Player] = []
        self.selected_character_indices: Set[int] = set()

    def start_game(self):
        self.round_counter = 0
        self.challenges_completed_counter = 0
        self.mission_progress = 0
        
        self.challenge_deck = create_challenge_deck_phase1()
        
        specializations = ["oxygen", "water", "temperature", "airpressure"]
        char_names = ["Sauerstoff", "Wasser", "Temperatur", "Luftdruck"]
        
        selected_specs = [specializations[i] for i in sorted(list(self.selected_character_indices))]
        selected_names = [char_names[i] for i in sorted(list(self.selected_character_indices))]
        self.players = [Player(name, spec) for name, spec in zip(selected_names, selected_specs)]
        
        start_player_index = random.randint(0, len(self.players) - 1)
        self.active_character = self.players[start_player_index]
        
        self.oxygen = 6
        self.water = 6
        self.temperature = 6
        self.airpressure = 6
        self.thrust = 0
        self.navigation = 0
        self.energy_pool = 0
        
        self.current_challenge: Optional[ChallengeCard] = None
        self.start_new_round()

    def start_new_round(self):
        self.round_counter += 1
        self.current_phase = VERFALLSPHASE
        print(f"\n--- RUNDE {self.round_counter}: VERFALLSPHASE ---")
        self.oxygen = max(0, self.oxygen - 2)
        self.water = max(0, self.water - 2)
        self.temperature = max(0, self.temperature - 2)
        self.airpressure = max(0, self.airpressure - 2)
        if self.check_for_defeat(): return
        
        self.current_phase = ENERGIEPHASE
        print("--- PHASE: ENERGIEPHASE ---")
        energy_map = {1: 4, 2: 6, 3: 8, 4: 10}
        self.energy_pool = energy_map.get(len(self.players), 10)
        
        if self.challenge_deck and not self.current_challenge:
             self.current_challenge = self.challenge_deck.pop(0)

        for player in self.players:
            player.is_ready = False
            
        self.current_phase = AKTIONSPHASE
        print("--- PHASE: AKTIONSPHASE ---")

    def modify_system_value(self, system: str, amount: int):
        cost = 1 
        
        if amount > 0 and self.active_character.specialization == system:
            if self.energy_pool >= cost:
                setattr(self, system, min(6, getattr(self, system) + 2))
                self.energy_pool -= cost
        elif amount != 0:
            if self.energy_pool >= cost:
                max_value = 8 if system in ["thrust", "navigation"] else 6
                current_value = getattr(self, system)
                new_value = max(0, min(max_value, current_value + amount))
                if new_value != current_value:
                    setattr(self, system, new_value)
                    self.energy_pool -= cost
        
        self.check_for_defeat()
        
    def check_for_defeat(self) -> bool:
        if self.oxygen <= 0 or self.water <= 0 or self.temperature <= 0 or self.airpressure <= 0:
            self.current_phase = GAME_OVER
            print("NIEDERLAGE: Ein Lebenserhaltungssystem ist kollabiert.")
            return True
        return False

    def resolve_challenge(self):
        if self.current_challenge:
            if self.thrust >= self.current_challenge.target_thrust and self.navigation >= self.current_challenge.target_navigation:
                self.mission_progress += 1
                self.challenges_completed_counter += 1
                print("Herausforderung ERFOLGREICH!")
            else:
                print("Herausforderung GESCHEITERT!")
        
        # KORREKTUR: Schub und Navigation werden NICHT mehr zurückgesetzt.
        self.current_challenge = None

    def prepare_next_round(self):
        if self.current_phase != VORBEREITUNGSPHASE: return
        
        current_idx = self.players.index(self.active_character)
        next_idx = (current_idx + 1) % len(self.players)
        self.active_character = self.players[next_idx]
        
        self.start_new_round()