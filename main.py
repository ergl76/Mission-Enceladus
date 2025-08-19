# ==============================================================================
# main.py
# KOMPLETT ÜBERARBEITET in diesem Sprint.
# ==============================================================================
import pygame
import sys
from typing import Dict, List, Optional

from src.game.game_state import GameState
from src.core.player import Player
from src.core.tasks import CrisisCard, DutyTask
from src.core.cards import ActionCard

# --- Pygame Setup ---
pygame.init()
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mission Enceladus - Prototyp")
font = pygame.font.SysFont("Arial", 24)
small_font = pygame.font.SysFont("Arial", 18)
clock = pygame.time.Clock()

# --- Colors ---
COLOR_BACKGROUND = (10, 20, 40)
COLOR_STATUS_ZONE = (20, 40, 60)
COLOR_FOCUS_ZONE = (30, 60, 90)
COLOR_ACTION_ZONE = (20, 40, 60)
COLOR_WHITE = (220, 220, 220)
COLOR_BAR_FUEL = (200, 100, 0)
COLOR_BAR_OXYGEN = (0, 150, 200)
COLOR_BAR_INTEGRITY = (180, 0, 0)
COLOR_CARD = (50, 80, 120)
COLOR_CARD_SELECTED = (255, 200, 0)
COLOR_TASK_SLOT = (15, 30, 50)
COLOR_TASK_SLOT_HOVER = (45, 90, 150)
COLOR_BUTTON = (0, 120, 0)
COLOR_BUTTON_HOVER = (0, 180, 0)


def draw_text(surface, text, pos, color=COLOR_WHITE, f=font):
    """Helper function to draw text."""
    text_surface = f.render(text, True, color)
    surface.blit(text_surface, pos)

def draw_status_bar(surface, game_state: GameState):
    """Draws the top status bar with global resources."""
    pygame.draw.rect(surface, COLOR_STATUS_ZONE, (0, 0, SCREEN_WIDTH, 100))
    
    # --- Fuel ---
    draw_text(surface, "Treibstoff", (50, 20))
    pygame.draw.rect(surface, (0,0,0), (50, 50, 200, 30), 2)
    pygame.draw.rect(surface, COLOR_BAR_FUEL, (50, 50, game_state.fuel * 20, 30))

    # --- Oxygen ---
    draw_text(surface, "Sauerstoff", (350, 20))
    pygame.draw.rect(surface, (0,0,0), (350, 50, 200, 30), 2)
    pygame.draw.rect(surface, COLOR_BAR_OXYGEN, (350, 50, game_state.oxygen * 20, 30))

    # --- Integrity ---
    draw_text(surface, "Schiffsintegrität", (650, 20))
    pygame.draw.rect(surface, (0,0,0), (650, 50, 200, 30), 2)
    pygame.draw.rect(surface, COLOR_BAR_INTEGRITY, (650, 50, game_state.integrity * 20, 30))

def draw_tasks(surface, crisis: Optional[CrisisCard], duty: Optional[DutyTask], game_state: GameState) -> Dict[str, pygame.Rect]:
    """Draws the central focus area with the current tasks."""
    pygame.draw.rect(surface, COLOR_FOCUS_ZONE, (0, 100, SCREEN_WIDTH, 300))
    
    task_rects = {}
    
    # --- Crisis Slot ---
    crisis_rect = pygame.Rect(50, 150, 550, 200)
    is_hovered = crisis_rect.collidepoint(pygame.mouse.get_pos()) and game_state.selected_card_obj is not None
    slot_color = COLOR_TASK_SLOT_HOVER if is_hovered else COLOR_TASK_SLOT
    pygame.draw.rect(surface, slot_color, crisis_rect)
    pygame.draw.rect(surface, COLOR_WHITE, crisis_rect, 2)
    draw_text(surface, "AKTUELLE KRISE", (crisis_rect.x + 20, crisis_rect.y + 10))
    if crisis:
        draw_text(surface, crisis.name, (crisis_rect.x + 20, crisis_rect.y + 50))
        req_text = ", ".join([f"{v} {k[:4]}" for k, v in crisis.requirements.items()])
        draw_text(surface, f"Anforderungen: {req_text}", (crisis_rect.x + 20, crisis_rect.y + 90), f=small_font)
    task_rects["crisis"] = crisis_rect
    
    # --- Duty Slot ---
    duty_rect = pygame.Rect(SCREEN_WIDTH - 600, 150, 550, 200)
    is_hovered = duty_rect.collidepoint(pygame.mouse.get_pos()) and game_state.selected_card_obj is not None
    slot_color = COLOR_TASK_SLOT_HOVER if is_hovered else COLOR_TASK_SLOT
    pygame.draw.rect(surface, slot_color, duty_rect)
    pygame.draw.rect(surface, COLOR_WHITE, duty_rect, 2)
    draw_text(surface, "PFLICHTAUFGABE", (duty_rect.x + 20, duty_rect.y + 10))
    if duty:
        draw_text(surface, duty.name, (duty_rect.x + 20, duty_rect.y + 50))
        req_text = ", ".join([f"{v} {k[:4]}" for k, v in duty.requirements.items()])
        draw_text(surface, f"Anforderungen: {req_text}", (duty_rect.x + 20, duty_rect.y + 90), f=small_font)
    task_rects["duty"] = duty_rect
    
    return task_rects

def draw_player_hand(surface, player: Player, game_state: GameState) -> List[pygame.Rect]:
    """Draws the current player's hand in the action zone."""
    pygame.draw.rect(surface, COLOR_ACTION_ZONE, (0, 400, SCREEN_WIDTH, SCREEN_HEIGHT - 400))
    
    card_rects = []
    start_x = 50
    card_gap = 20
    card_width = 150
    card_height = 200

    for i, card in enumerate(player.hand):
        card_x = start_x + i * (card_width + card_gap)
        card_rect = pygame.Rect(card_x, 450, card_width, card_height)
        card_rects.append(card_rect)
        
        # Draw selection highlight
        border_color = COLOR_CARD_SELECTED if i == game_state.selected_card_index else COLOR_WHITE
        border_width = 5 if i == game_state.selected_card_index else 2

        pygame.draw.rect(surface, COLOR_CARD, card_rect)
        pygame.draw.rect(surface, border_color, card_rect, border_width)
        
        # Draw card info
        draw_text(surface, card.name, (card_x + 10, 460), f=small_font)
        if hasattr(card, 'symbol'):
             draw_text(surface, card.symbol, (card_x + 10, 500))

    return card_rects

def draw_confirm_button(surface) -> pygame.Rect:
    """Draws the confirm button."""
    button_rect = pygame.Rect(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 80, 200, 50)
    is_hovered = button_rect.collidepoint(pygame.mouse.get_pos())
    button_color = COLOR_BUTTON_HOVER if is_hovered else COLOR_BUTTON
    
    pygame.draw.rect(surface, button_color, button_rect)
    draw_text(surface, "Aktionen bestätigen", (button_rect.x + 10, button_rect.y + 10), f=small_font)
    return button_rect

def main():
    """Main game loop."""
    game_state = GameState(num_players=4)
    game_state.setup_new_round()
    
    # For this prototype, we'll only interact with Player 1
    active_player = game_state.players[0]

    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left mouse button
                    mouse_pos = event.pos
                    
                    # 1. Card Selection Logic
                    for i, card_rect in enumerate(card_rects):
                        if card_rect.collidepoint(mouse_pos):
                            game_state.select_card(i, active_player)
                            break
                    
                    # 2. Card Assignment Logic
                    if game_state.selected_card_obj:
                        if task_rects["crisis"].collidepoint(mouse_pos):
                            game_state.assign_selected_card_to_task("crisis", active_player)
                        elif task_rects["duty"].collidepoint(mouse_pos):
                            game_state.assign_selected_card_to_task("duty", active_player)
                            
                    # 3. Confirm Button Logic
                    if confirm_button_rect.collidepoint(mouse_pos):
                        game_state.end_action_phase()


        # --- Drawing ---
        screen.fill(COLOR_BACKGROUND)
        
        # Draw UI Zones and get interactive element rects
        draw_status_bar(screen, game_state)
        task_rects = draw_tasks(screen, game_state.current_crisis, game_state.current_duty_task, game_state)
        card_rects = draw_player_hand(screen, active_player, game_state)
        confirm_button_rect = draw_confirm_button(screen)
        
        # --- Update Display ---
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()