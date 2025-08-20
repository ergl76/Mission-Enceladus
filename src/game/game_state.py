# ==============================================================================
# src/game/game_state.py
# Grundlegend überarbeitet für das Energie-Management-System.
# ==============================================================================
import random
from typing import List, Optional, Tuple, Dict, Set
from src.core.player import Player
from src.core.tasks import ChallengeCard
from src.game.decks import create_challenge_deck_phase1

# Phase Constants
SETUP_SCREEN = "SetupScreen"
VERFALLSPHASE = "Verfallsphase"
ENERGIEPHASE = "Energiephase"
AKTIONSPHASE = "Aktionsphase" # Behalten für die Energie-Zuteilung
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
        self.round_counter = 1
        self.challenges_completed_counter = 0
        self.mission_progress = 0
        
        self.challenge_deck = create_challenge_deck_phase1(len(self.selected_character_indices))
        
        # Charakter-Spezialisierungen
        specializations = ["Sauerstoff", "Wasser", "Temperatur", "Luftdruck"]
        selected_specs = [specializations[i] for i in sorted(list(self.selected_character_indices))]
        
        self.players = [Player(f"Spieler {i+1}", spec) for i, spec in enumerate(selected_specs)]
        
        start_player_index = random.randint(0, len(self.players) - 1)
        self.active_character = self.players[start_player_index]
        
        # Neue System-Werte
        self.oxygen = 6
        self.water = 6
        self.temperature = 6
        self.air_pressure = 6
        self.thrust = 0
        self.navigation = 0
        self.energy_pool = 0
        
        self.current_challenge: Optional[ChallengeCard] = self.challenge_deck.pop(0)

        self.start_new_round()

    def start_new_round(self):
        """Führt die Verfalls- und Energiephase aus und startet die Aktionsphase."""
        # Phase 1: Verfallsphase
        self.current_phase = VERFALLSPHASE
        print(f"\n--- RUNDE {self.round_counter}: VERFALLSPHASE ---")
        self.oxygen = max(0, self.oxygen - 2)
        self.water = max(0, self.water - 2)
        self.temperature = max(0, self.temperature - 2)
        self.air_pressure = max(0, self.air_pressure - 2)
        self.check_for_defeat()
        if self.current_phase == GAME_OVER: return
        
        # Phase 2: Energiephase
        self.current_phase = ENERGIEPHASE
        print("--- PHASE: ENERGIEPHASE ---")
        # Energie-Zuteilung basierend auf Spielerzahl (Beispielwerte)
        energy_map = {1: 4, 2: 6, 3: 8, 4: 10}
        self.energy_pool = energy_map.get(len(self.players), 10)

        for player in self.players:
            player.is_ready = False
            
        self.current_phase = AKTIONSPHASE
        print("--- PHASE: AKTIONSPHASE ---")

    def modify_system_value(self, system: str, amount: int) -> bool:
        """Versucht, Energie auszugeben, um einen Systemwert zu ändern."""
        
        # Spezialisierungs-Bonus prüfen
        cost = amount
        if amount > 0 and self.active_character.specialization.lower() == system:
             # Bei Spezialisierung kostet eine Erhöhung um 2 nur 1 Energie
            if self.energy_pool >= 1:
                setattr(self, system, min(6, getattr(self, system) + 2))
                self.energy_pool -= 1
                return True
            return False

        # Standard Kosten-Nutzen-Rechnung
        if self.energy_pool >= cost:
            current_value = getattr(self, system)
            max_value = 8 if system in ["thrust", "navigation"] else 6
            new_value = max(0, min(max_value, current_value + amount))
            
            # Energie wird nur verbraucht, wenn eine Änderung stattfindet
            if new_value != current_value:
                setattr(self, system, new_value)
                self.energy_pool -= cost
                return True
        return False
        
    def check_for_defeat(self):
        if self.oxygen <= 0 or self.water <= 0 or self.temperature <= 0 or self.air_pressure <= 0:
            self.current_phase = GAME_OVER

    def resolve_challenge(self):
        """Prüft den Erfolg der aktuellen Herausforderung."""
        if self.current_challenge:
            if self.thrust >= self.current_challenge.target_thrust and self.navigation >= self.current_challenge.target_navigation:
                # Erfolg
                self.mission_progress += 1
                self.challenges_completed_counter += 1
                print("Herausforderung ERFOLGREICH!")
            else:
                # Fehlschlag
                print("Herausforderung GESCHEITERT!")
        
        # Reset für die nächste Runde
        self.thrust = 0
        self.navigation = 0

    def prepare_next_round(self):
        if self.current_phase != VORBEREITUNGSPHASE: return
        
        current_idx = self.players.index(self.active_character)
        next_idx = (current_idx + 1) % len(self.players)
        self.active_character = self.players[next_idx]
        
        if self.challenge_deck:
            self.current_challenge = self.challenge_deck.pop(0)
        else:
            self.current_challenge = None # Später Sieg-Bedingung

        self.round_counter += 1
        self.start_new_round()