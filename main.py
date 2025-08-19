# ==============================================================================
# main.py
# Stark überarbeitet: Phasen-basierte Game-Loop, Animation, Team-Cockpit
# ==============================================================================
import pygame
import sys
from typing import Dict, List, Optional

from src.game.game_state import GameState, AKTIONSPHASE, AUFLOESUNGSPHASE, VORBEREITUNGSPHASE
from src.core.player import Player
from src.ui.animation import ResolutionAnimation

# --- Pygame Setup ---
pygame.init()
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mission Enceladus - Prototyp")
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 36, bold=True)
small_font = pygame.font.SysFont("Arial", 18)
clock = pygame.time.Clock()

# --- Colors ---
COLOR_BACKGROUND = (10, 20, 40)
COLOR_STATUS_ZONE = (20, 40, 60)
COLOR_FOCUS_ZONE = (30, 60, 90)
COLOR_ACTION_ZONE = (20, 40, 60)
COLOR_WHITE = (220, 220, 220)
COLOR_PLAYER_PORTRAIT = (100, 100, 120)
COLOR_PLAYER_ACTIVE = (255, 255, 0)
COLOR_BAR_FUEL = (200, 100, 0)
COLOR_BAR_OXYGEN = (0, 150, 200)
COLOR_BAR_INTEGRITY = (180, 0, 0)
COLOR_CARD = (50, 80, 120)
COLOR_CARD_SELECTED = (255, 200, 0)
COLOR_TASK_SLOT = (15, 30, 50)
COLOR_TASK_SLOT_HOVER = (45, 90, 150)
COLOR_BUTTON = (0, 120, 0)
COLOR_BUTTON_HOVER = (0, 180, 0)

def draw_text(surface, text, pos, color=COLOR_WHITE, f=font, center=False):
    """Helper function to draw text."""
    text_surface = f.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = pos
    else:
        text_rect.topleft = pos
    surface.blit(text_surface, text_rect)

def draw_status_bar(surface, game_state: GameState) -> List[pygame.Rect]:
    """Draws the top status bar with resources and player portraits."""
    pygame.draw.rect(surface, COLOR_STATUS_ZONE, (0, 0, SCREEN_WIDTH, 100))
    portrait_rects = []
    
    # Resources
    draw_text(surface, f"Fuel: {game_state.fuel}", (50, 20))
    pygame.draw.rect(surface, COLOR_BAR_FUEL, (50, 50, game_state.fuel * 20, 30))
    draw_text(surface, f"Oxygen: {game_state.oxygen}", (300, 20))
    pygame.draw.rect(surface, COLOR_BAR_OXYGEN, (300, 50, game_state.oxygen * 20, 30))
    draw_text(surface, f"Integrity: {game_state.integrity}", (550, 20))
    pygame.draw.rect(surface, COLOR_BAR_INTEGRITY, (550, 50, game_state.integrity * 20, 30))

    # Player Portraits
    for i, player in enumerate(game_state.players):
        rect = pygame.Rect(SCREEN_WIDTH - (4 - i) * 80, 20, 60, 60)
        portrait_rects.append(rect)
        pygame.draw.rect(surface, COLOR_PLAYER_PORTRAIT, rect)
        if i == game_state.active_player_index:
            pygame.draw.rect(surface, COLOR_PLAYER_ACTIVE, rect, 4)
        draw_text(surface, f"P{i+1}", (0,0), center=rect.center)
    return portrait_rects

def draw_tasks(surface, game_state: GameState, interactive: bool) -> Dict[str, pygame.Rect]:
    """Draws the central focus area with the current tasks."""
    pygame.draw.rect(surface, COLOR_FOCUS_ZONE, (0, 100, SCREEN_WIDTH, 300))
    task_rects = {}
    
    # Crisis Slot
    crisis_rect = pygame.Rect(50, 150, 550, 200)
    is_hovered = interactive and crisis_rect.collidepoint(pygame.mouse.get_pos()) and game_state.selected_card_obj is not None
    slot_color = COLOR_TASK_SLOT_HOVER if is_hovered else COLOR_TASK_SLOT
    pygame.draw.rect(surface, slot_color, crisis_rect)
    pygame.draw.rect(surface, COLOR_WHITE, crisis_rect, 2)
    draw_text(surface, "AKTUELLE KRISE", (crisis_rect.x + 20, crisis_rect.y + 10))
    if game_state.current_crisis:
        draw_text(surface, game_state.current_crisis.name, (crisis_rect.x + 20, crisis_rect.y + 50))
        # KORREKTUR: Hinzufügen der Anforderungs-Anzeige
        req_text = ", ".join([f"{v} {k[:4]}" for k, v in game_state.current_crisis.requirements.items()])
        draw_text(surface, f"Anforderungen: {req_text}", (crisis_rect.x + 20, crisis_rect.y + 90), f=small_font)
    task_rects["crisis"] = crisis_rect
    
    # Duty Slot
    duty_rect = pygame.Rect(SCREEN_WIDTH - 600, 150, 550, 200)
    is_hovered = interactive and duty_rect.collidepoint(pygame.mouse.get_pos()) and game_state.selected_card_obj is not None
    slot_color = COLOR_TASK_SLOT_HOVER if is_hovered else COLOR_TASK_SLOT
    pygame.draw.rect(surface, slot_color, duty_rect)
    pygame.draw.rect(surface, COLOR_WHITE, duty_rect, 2)
    draw_text(surface, "PFLICHTAUFGABE", (duty_rect.x + 20, duty_rect.y + 10))
    if game_state.current_duty_task:
        draw_text(surface, game_state.current_duty_task.name, (duty_rect.x + 20, duty_rect.y + 50))
        # KORREKTUR: Hinzufügen der Anforderungs-Anzeige
        req_text = ", ".join([f"{v} {k[:4]}" for k, v in game_state.current_duty_task.requirements.items()])
        draw_text(surface, f"Anforderungen: {req_text}", (duty_rect.x + 20, duty_rect.y + 90), f=small_font)
    task_rects["duty"] = duty_rect
    
    return task_rects

def draw_player_hand(surface, player_to_show: Player, is_active_player: bool, game_state: GameState) -> List[pygame.Rect]:
    """Draws a player's hand."""
    pygame.draw.rect(surface, COLOR_ACTION_ZONE, (0, 400, SCREEN_WIDTH, SCREEN_HEIGHT - 400))
    
    if not is_active_player:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - 400), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 400))
        draw_text(surface, f"Blick ins Cockpit von {player_to_show.name}", (SCREEN_WIDTH/2, 420), center=True, f=big_font)

    card_rects = []
    start_x = (SCREEN_WIDTH - (len(player_to_show.hand) * 170 - 20)) / 2
    for i, card in enumerate(player_to_show.hand):
        card_rect = pygame.Rect(start_x + i * 170, 480, 150, 220)
        card_rects.append(card_rect)
        
        border_color = COLOR_WHITE
        border_width = 2
        if is_active_player and i == game_state.selected_card_index:
            border_color = COLOR_CARD_SELECTED
            border_width = 5

        pygame.draw.rect(surface, COLOR_CARD, card_rect)
        pygame.draw.rect(surface, border_color, card_rect, border_width)
        draw_text(surface, card.name, (card_rect.x + 10, card_rect.y + 10), f=small_font)
        if hasattr(card, 'symbol'):
             draw_text(surface, card.symbol, (card_rect.x + 10, card_rect.y + 40))
             
    return card_rects if is_active_player else []

def draw_confirm_button(surface, interactive: bool) -> pygame.Rect:
    button_rect = pygame.Rect(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 80, 200, 50)
    is_hovered = interactive and button_rect.collidepoint(pygame.mouse.get_pos())
    button_color = COLOR_BUTTON_HOVER if is_hovered else COLOR_BUTTON
    
    pygame.draw.rect(surface, button_color, button_rect)
    # KORREKTUR: Der Positionsparameter 'pos' ist jetzt der Mittelpunkt des Buttons.
    draw_text(surface, "Aktionen bestätigen", button_rect.center, f=small_font, center=True)
    return button_rect

def main():
    game_state = GameState(num_players=4)
    active_player = game_state.players[game_state.active_player_index]
    
    resolution_anim: Optional[ResolutionAnimation] = None
    viewing_player: Optional[Player] = None

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # MOUSE UP: For Team-Cockpit view
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    viewing_player = None

            # MOUSE DOWN: For interactions
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Team-Cockpit Logic: Hold to view other hands
                    for i, rect in enumerate(portrait_rects):
                        if rect.collidepoint(mouse_pos) and i != game_state.active_player_index:
                            viewing_player = game_state.players[i]
                            break
                    
                    if game_state.current_phase == AKTIONSPHASE:
                        # Card Selection
                        for i, rect in enumerate(card_rects):
                            if rect.collidepoint(mouse_pos):
                                game_state.select_card(i, active_player)
                                break
                        
                        # Card Assignment
                        if game_state.selected_card_obj:
                            if task_rects["crisis"].collidepoint(mouse_pos):
                                game_state.assign_selected_card_to_task("crisis", active_player)
                            elif task_rects["duty"].collidepoint(mouse_pos):
                                game_state.assign_selected_card_to_task("duty", active_player)
                                
                        # Confirm Button
                        if confirm_button_rect.collidepoint(mouse_pos):
                            game_state.start_resolution_phase()
                            duty_success, crisis_success, duty_provided, crisis_provided = game_state.resolve_tasks()
                            game_state.apply_consequences(duty_success, crisis_success)
                            resolution_anim = ResolutionAnimation(
                                duty_success, crisis_success,
                                duty_provided, crisis_provided,
                                game_state.current_duty_task.requirements,
                                game_state.current_crisis.requirements
                            )

        # --- Game Logic Update (State Machine) ---
        if game_state.current_phase == AUFLOESUNGSPHASE and resolution_anim:
            resolution_anim.update(dt)
            if resolution_anim.is_finished:
                resolution_anim = None
                game_state.current_phase = VORBEREITUNGSPHASE
                game_state.prepare_next_round() # This will ultimately set phase to AKTIONSPHASE
                active_player = game_state.players[game_state.active_player_index]

        # --- Drawing ---
        screen.fill(COLOR_BACKGROUND)
        
        portrait_rects = draw_status_bar(screen, game_state)
        
        interactive_ui = game_state.current_phase == AKTIONSPHASE
        task_rects = draw_tasks(screen, game_state, interactive_ui)
        
        player_to_show = viewing_player if viewing_player else active_player
        is_active_player_view = viewing_player is None
        card_rects = draw_player_hand(screen, player_to_show, is_active_player_view, game_state)
        
        confirm_button_rect = draw_confirm_button(screen, interactive_ui)

        # Draw animation overlay if it's running
        if resolution_anim:
            resolution_anim.draw(screen)
            
        # --- Cursor Update ---
        interactive_rects = card_rects + list(task_rects.values()) + portrait_rects + [confirm_button_rect]
        is_over_interactive = any(rect.collidepoint(mouse_pos) for rect in interactive_rects)
        
        if is_over_interactive and game_state.current_phase == AKTIONSPHASE:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()