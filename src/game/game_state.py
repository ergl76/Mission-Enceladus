# ==============================================================================
# src/game/game_state.py
# NEUE DATEI in diesem Sprint.
# ==============================================================================
from typing import List, Optional
from src.core.player import Player
from src.core.tasks import CrisisCard, DutyTask
from src.game.decks import create_initial_action_deck, create_crisis_deck_phase1
from src.core import constants
from src.core.cards import ActionCard

class GameState:
    """Manages the entire state of the game."""
    def __init__(self, num_players: int = 4):
        # Global Resources
        self.fuel = 10
        self.oxygen = 10
        self.integrity = 10
        
        # Decks
        self.action_deck = create_initial_action_deck()
        self.crisis_deck = create_crisis_deck_phase1(num_players)
        
        # Players
        self.players = [Player(f"Player {i+1}") for i in range(num_players)]
        for player in self.players:
            player.draw_hand(self.action_deck)
        
        # Current Round State
        self.current_crisis: Optional[CrisisCard] = None
        self.current_duty_task: Optional[DutyTask] = None
        
        # UI & Interaction State
        self.selected_card_index: Optional[int] = None
        self.selected_card_obj: Optional[ActionCard] = None
        
        self.assigned_to_crisis: List[ActionCard] = []
        self.assigned_to_duty: List[ActionCard] = []

    def setup_new_round(self):
        """Sets up the tasks for a new round."""
        print("\n--- Setting up new round ---")
        # Draw a new crisis card
        self.current_crisis = self.crisis_deck.draw()
        if not self.current_crisis:
            print("CRISIS DECK IS EMPTY!")
            # Handle game end or reshuffle logic here later
        
        # Define the duty task for the current phase (static for now)
        self.current_duty_task = DutyTask(
            name="System-Check",
            penalty_escalation=["-1 Integrity", "-2 Integrity"],
            req_1_2_players={constants.LIFE_SUPPORT: 1, constants.RESEARCH: 1},
            req_3_4_players={constants.LIFE_SUPPORT: 2, constants.RESEARCH: 2},
            player_count=len(self.players)
        )
        print(f"New Crisis: {self.current_crisis.name if self.current_crisis else 'None'}")
        print(f"Duty Task: {self.current_duty_task.name}")

    def select_card(self, card_index: int, player: Player):
        """Selects a card from the player's hand."""
        if 0 <= card_index < len(player.hand):
            self.selected_card_index = card_index
            self.selected_card_obj = player.hand[card_index]
            print(f"Selected card: {self.selected_card_obj}")

    def assign_selected_card_to_task(self, task_name: str, player: Player):
        """Assigns the selected card to a specified task."""
        if self.selected_card_obj and self.selected_card_index is not None:
            card = player.hand.pop(self.selected_card_index)
            if task_name == "crisis":
                self.assigned_to_crisis.append(card)
                print(f"Assigned {card.name} to Crisis.")
            elif task_name == "duty":
                self.assigned_to_duty.append(card)
                print(f"Assigned {card.name} to Duty Task.")
            
            # Reset selection
            self.selected_card_index = None
            self.selected_card_obj = None

    def end_action_phase(self):
        """Ends the action phase and clears assignments."""
        print("\n--- Aktionen bestätigt ---")
        print(f"Assigned to Crisis: {self.assigned_to_crisis}")
        print(f"Assigned to Duty: {self.assigned_to_duty}")
        # In a future sprint, this is where we resolve the tasks.
        self.assigned_to_crisis.clear()
        self.assigned_to_duty.clear()
        print("Assignments cleared for next action.")