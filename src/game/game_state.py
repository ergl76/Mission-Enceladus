# ==============================================================================
# src/game/game_state.py
# Stark überarbeitet: Phasen-Manager, Auflösungslogik, etc.
# ==============================================================================
from typing import List, Optional, Tuple, Dict, Set
from collections import defaultdict
from src.core.player import Player
from src.core.tasks import CrisisCard, DutyTask
from src.game.decks import create_initial_action_deck, create_crisis_deck_phase1
from src.core import constants
from src.core.cards import ActionCard, StandardCard, EfficiencyCard, JokerCard
from src.core.deck import Deck

# Phase Constants
LAGEBESPRECHUNG = "Lagebesprechung"
AKTIONSPHASE = "Aktionsphase"
AUFLOESUNGSPHASE = "Auflösungsphase"
VORBEREITUNGSPHASE = "Vorbereitungsphase"

class GameState:
    """Manages the entire state of the game."""
    def __init__(self, num_players: int = 4):
        # Game State Machine
        self.current_phase = LAGEBESPRECHUNG
        
        # Global Resources
        self.fuel = 10
        self.oxygen = 10
        self.integrity = 10
        
        # Decks & Piles
        self.action_deck = create_initial_action_deck()
        self.crisis_deck = create_crisis_deck_phase1(num_players)
        self.discard_pile = Deck([])
        
        # Players
        self.players = [Player(f"Player {i+1}") for i in range(num_players)]
        self.active_player_index = 0 # Player 1 starts
        
        # Current Round State
        self.current_crisis: Optional[CrisisCard] = None
        self.current_duty_task: Optional[DutyTask] = None
        
        # Interaction & Assignment State
        self.selected_card_index: Optional[int] = None
        self.selected_card_obj: Optional[ActionCard] = None
        self.assigned_to_crisis: List[ActionCard] = []
        self.assigned_to_duty: List[ActionCard] = []
        self.players_who_contributed: Set[Player] = set()

        # Initial Setup
        for player in self.players:
            player.draw_hand(self.action_deck)
        self.setup_new_round()

    def setup_new_round(self):
        """Sets up the tasks for a new round and transitions to Aktionsphase."""
        print("\n--- PHASE: LAGEBESPRECHUNG ---")
        self.current_crisis = self.crisis_deck.draw()
        if not self.current_crisis:
            print("CRISIS DECK IS EMPTY!")
        
        self.current_duty_task = DutyTask(
            name="System-Check",
            penalty_escalation=["-1 Integrity", "-2 Integrity"],
            req_1_2_players={constants.LIFE_SUPPORT: 1, constants.RESEARCH: 1},
            req_3_4_players={constants.LIFE_SUPPORT: 2, constants.RESEARCH: 2},
            player_count=len(self.players)
        )
        print(f"New Crisis: {self.current_crisis.name if self.current_crisis else 'None'}")
        print(f"Duty Task: {self.current_duty_task.name}")
        self.current_phase = AKTIONSPHASE
        print("--- PHASE: AKTIONSPHASE ---")

    def select_card(self, card_index: int, player: Player):
        """Selects a card from the player's hand."""
        if self.current_phase != AKTIONSPHASE: return
        if 0 <= card_index < len(player.hand):
            self.selected_card_index = card_index
            self.selected_card_obj = player.hand[card_index]
            print(f"Selected card: {self.selected_card_obj}")

    def assign_selected_card_to_task(self, task_name: str, player: Player):
        """Assigns the selected card to a specified task."""
        if not self.selected_card_obj: return
        
        card = player.hand.pop(self.selected_card_index)
        if task_name == "crisis":
            self.assigned_to_crisis.append(card)
        elif task_name == "duty":
            self.assigned_to_duty.append(card)
        
        self.players_who_contributed.add(player)
        print(f"Assigned {card.name} to {task_name.title()}.")
        
        self.selected_card_index = None
        self.selected_card_obj = None

    def start_resolution_phase(self):
        if self.current_phase != AKTIONSPHASE: return
        print("\n--- PHASE: AUFLÖSUNGSPHASE ---")
        self.current_phase = AUFLOESUNGSPHASE

    def resolve_tasks(self) -> Tuple[bool, bool, Dict[str, int], Dict[str, int]]:
        """
        Counts symbols for assigned cards and checks for success.
        Returns: (duty_success, crisis_success, duty_provided, crisis_provided)
        """
        # Count provided symbols for Duty Task
        duty_provided = defaultdict(int)
        for card in self.assigned_to_duty:
            if hasattr(card, 'symbol'):
                duty_provided[card.symbol] += 1
        
        # Count provided symbols for Crisis Task
        crisis_provided = defaultdict(int)
        for card in self.assigned_to_crisis:
            if hasattr(card, 'symbol'):
                crisis_provided[card.symbol] += 1
                
        # Check success for Duty Task
        duty_success = True
        if self.current_duty_task:
            for symbol, required in self.current_duty_task.requirements.items():
                if duty_provided[symbol] < required:
                    duty_success = False
                    break
        
        # Check success for Crisis Task
        crisis_success = True
        if self.current_crisis:
            for symbol, required in self.current_crisis.requirements.items():
                if crisis_provided[symbol] < required:
                    crisis_success = False
                    break
                    
        return duty_success, crisis_success, dict(duty_provided), dict(crisis_provided)

    def apply_consequences(self, duty_success: bool, crisis_success: bool):
        """Applies penalties and rewards based on task resolution."""
        print("Applying consequences...")
        if not duty_success:
            self.integrity -= 1
            print("Duty Task FAILED! -1 Integrity.")
        else:
            print("Duty Task SUCCESSFUL!")
            
        if not crisis_success:
            self.fuel -= 1 # Placeholder penalty
            print("Crisis FAILED! -1 Fuel.")
        else:
            self.fuel += 1 # Placeholder reward
            print("Crisis SUCCESSFUL! +1 Fuel.")

    def prepare_next_round(self):
        """Cleans up the completed round and prepares for the next one."""
        if self.current_phase != VORBEREITUNGSPHASE: return
        print("\n--- PHASE: VORBEREITUNGSPHASE ---")

        # Discard used cards
        self.discard_pile.cards.extend(self.assigned_to_crisis)
        self.discard_pile.cards.extend(self.assigned_to_duty)
        self.assigned_to_crisis.clear()
        self.assigned_to_duty.clear()
        
        # Refill hands
        print("Refilling player hands...")
        for player in self.players_who_contributed:
            player.draw_hand(self.action_deck)
        self.players_who_contributed.clear()
        
        # Transition to next round setup
        self.current_phase = LAGEBESPRECHUNG
        self.setup_new_round()