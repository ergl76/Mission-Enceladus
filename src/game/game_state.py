# ==============================================================================
# src/game/game_state.py
# Stark erweitert: Setup-Phase, Game-Over, Spieler-Rotation, etc.
# ==============================================================================
import random
from typing import List, Optional, Tuple, Dict, Set
from collections import defaultdict
from src.core.player import Player
from src.core.tasks import ChallengeCard, DutyTask
from src.game.decks import create_initial_action_deck, create_challenge_deck_phase1
from src.core import constants
from src.core.cards import ActionCard, JokerCard
from src.core.deck import Deck

# Phase Constants
SETUP_SCREEN = "SetupScreen"
LAGEBESPRECHUNG = "Lagebesprechung"
AKTIONSPHASE = "Aktionsphase"
AUFLOESUNGSPHASE = "Auflösungsphase"
VORBEREITUNGSPHASE = "Vorbereitungsphase"
GAME_OVER = "GameOver"

class GameState:
    """Manages the entire state of the game."""
    def __init__(self):
        self.current_phase = SETUP_SCREEN
        self.players: List[Player] = []
        self.selected_character_indices: Set[int] = set()

    def start_game(self):
        """Initializes all game variables after character selection."""
        self.fuel = 10
        self.oxygen = 10
        self.integrity = 10
        self.mission_progress = 0
        
        self.action_deck = create_initial_action_deck()
        self.challenge_deck = create_challenge_deck_phase1(len(self.selected_character_indices))
        self.discard_pile = Deck([])
        
        self.players = [Player(f"Spieler {i+1}") for i in sorted(list(self.selected_character_indices))]
        
        # Determine random start player
        self.active_player_index = random.randint(0, len(self.players) - 1)
        
        self.current_challenge: Optional[ChallengeCard] = None
        self.current_duty_task: Optional[DutyTask] = None
        
        self.selected_card_index: Optional[int] = None
        self.selected_card_obj: Optional[ActionCard] = None
        self.assigned_to_challenge: List[ActionCard] = []
        self.assigned_to_duty: List[ActionCard] = []
        self.players_who_contributed: Set[Player] = set()

        for player in self.players:
            player.draw_hand(self.action_deck)
        self.setup_new_round()

    def setup_new_round(self):
        self.current_phase = LAGEBESPRECHUNG
        self.current_challenge = self.challenge_deck.draw()
        self.current_duty_task = DutyTask(
            name="System-Check", penalty_escalation=[],
            req_1_2_players={constants.LIFE_SUPPORT: 1, constants.RESEARCH: 1},
            req_3_4_players={constants.LIFE_SUPPORT: 2, constants.RESEARCH: 2},
            player_count=len(self.players)
        )
        self.current_phase = AKTIONSPHASE

    def select_card(self, card_index: int, player: Player):
        if self.current_phase != AKTIONSPHASE: return
        if 0 <= card_index < len(player.hand):
            self.selected_card_index = card_index
            self.selected_card_obj = player.hand[card_index]

    def assign_selected_card_to_task(self, task_name: str, player: Player):
        if not self.selected_card_obj: return
        card = player.hand.pop(self.selected_card_index)
        if task_name == "challenge": self.assigned_to_challenge.append(card)
        else: self.assigned_to_duty.append(card)
        self.players_who_contributed.add(player)
        self.selected_card_index = None
        self.selected_card_obj = None

    def start_resolution_phase(self):
        if self.current_phase != AKTIONSPHASE: return
        self.current_phase = AUFLOESUNGSPHASE

    def resolve_tasks(self) -> Tuple[bool, bool, Dict[str, int], Dict[str, int]]:
        def count_symbols(cards: List[ActionCard]) -> Dict[str, int]:
            provided = defaultdict(int)
            jokers = sum(1 for card in cards if isinstance(card, JokerCard))
            for card in cards:
                if hasattr(card, 'symbol'): provided[card.symbol] += 1
            if jokers > 0:
                all_symbols = [constants.NAVIGATION, constants.REPAIR, constants.RESEARCH, constants.LIFE_SUPPORT]
                for symbol_type in all_symbols:
                    provided[symbol_type] += jokers
            return dict(provided)

        duty_provided = count_symbols(self.assigned_to_duty)
        challenge_provided = count_symbols(self.assigned_to_challenge)
        
        duty_success = all(duty_provided.get(s, 0) >= r for s, r in self.current_duty_task.requirements.items())
        challenge_success = not self.current_challenge or all(challenge_provided.get(s, 0) >= r for s, r in self.current_challenge.requirements.items())
        
        return duty_success, challenge_success, duty_provided, challenge_provided

    def apply_consequences(self, duty_success: bool, challenge_success: bool):
        if not duty_success: self.integrity -= 2
        if self.current_challenge:
            if challenge_success and "Fortschritt" in self.current_challenge.reward:
                self.mission_progress += 1
            elif not challenge_success:
                if "Integrität" in self.current_challenge.penalty: self.integrity -= 1
                if "Treibstoff" in self.current_challenge.penalty: self.fuel -= 1
        self.check_for_defeat()

    def check_for_defeat(self):
        if self.fuel <= 0 or self.oxygen <= 0 or self.integrity <= 0:
            self.current_phase = GAME_OVER

    def prepare_next_round(self):
        if self.current_phase != VORBEREITUNGSPHASE: return
        self.discard_pile.cards.extend(self.assigned_to_challenge)
        self.discard_pile.cards.extend(self.assigned_to_duty)
        self.assigned_to_challenge.clear()
        self.assigned_to_duty.clear()
        for player in self.players_who_contributed:
            player.draw_hand(self.action_deck)
        self.players_who_contributed.clear()
        self.active_player_index = (self.active_player_index + 1) % len(self.players)
        self.setup_new_round()