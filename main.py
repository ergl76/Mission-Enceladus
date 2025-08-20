# ==============================================================================
# main.py
# Umfassend erweitert: Hot-Seat, Ready-Check, erweiterter Game-Over Screen
# ==============================================================================
import pygame
import sys
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict
from src.game.game_state import GameState, SETUP_SCREEN, AKTIONSPHASE, AUFLOESUNGSPHASE, VORBEREITUNGSPHASE, GAME_OVER
from src.core.player import Player
from src.ui.animation import ResolutionAnimation
from src.core.cards import JokerCard
from src.core import constants

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mission Enceladus - Prototyp")
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 36, bold=True)
small_font = pygame.font.SysFont("Arial", 18)
clock = pygame.time.Clock()

# Colors
COLOR_BACKGROUND = (10, 20, 40)
COLOR_WHITE = (220, 220, 220)
COLOR_GREY = (100, 100, 120)
COLOR_YELLOW = (255, 255, 0)
COLOR_GREEN = (0, 200, 0)
COLOR_RED = (200, 0, 0)
COLOR_STATUS_ZONE = (20, 40, 60)
COLOR_FOCUS_ZONE = (30, 60, 90)
COLOR_ACTION_ZONE = (20, 40, 60)
COLOR_PLAYER_PORTRAIT = (100, 100, 120)
COLOR_PLAYER_ACTIVE = (255, 255, 0)
COLOR_BAR_FUEL = (200, 100, 0)
COLOR_BAR_OXYGEN = (0, 150, 200)
COLOR_BAR_INTEGRITY = (180, 0, 0)
COLOR_CARD = (50, 80, 120)
COLOR_CARD_SELECTED = (255, 200, 0)

def draw_text(surface, text, pos, color=COLOR_WHITE, f=font, center=False):
    text_surface = f.render(text, True, color)
    text_rect = text_surface.get_rect(center=pos) if center else text_surface.get_rect(topleft=pos)
    surface.blit(text_surface, text_rect)

def draw_setup_screen(surface, selected_indices: Set[int]) -> Tuple[List[pygame.Rect], pygame.Rect]:
    surface.fill(COLOR_BACKGROUND)
    draw_text(surface, "CREW-MANIFEST", (SCREEN_WIDTH / 2, 100), center=True, f=big_font)
    char_rects = []
    char_names = ["Kapitän", "Wissenschaftlerin", "Ingenieurin", "Pilotin"]
    for i, name in enumerate(char_names):
        rect = pygame.Rect(200 + i * 220, 250, 200, 250)
        char_rects.append(rect)
        color = COLOR_YELLOW if i in selected_indices else COLOR_GREY
        pygame.draw.rect(surface, color, rect, 5, border_radius=10)
        draw_text(surface, name, rect.midtop + pygame.Vector2(0, 20), center=True)
    start_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - 150, 600, 300, 70)
    is_ready = 1 <= len(selected_indices) <= 4
    button_color = COLOR_GREEN if is_ready else COLOR_GREY
    pygame.draw.rect(surface, button_color, start_button_rect, border_radius=10)
    draw_text(surface, "MISSION STARTEN", start_button_rect.center, center=True)
    return char_rects, start_button_rect

def draw_game_over_screen(surface, game_state: GameState) -> Tuple[pygame.Rect, pygame.Rect]:
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0,0))
    draw_text(surface, "MISSION GESCHEITERT", (SCREEN_WIDTH/2, 150), center=True, f=big_font, color=COLOR_RED)
    
    # Stats
    draw_text(surface, f"Reisedauer: {game_state.round_counter} Runden", (SCREEN_WIDTH/2, 250), center=True)
    draw_text(surface, f"Gemeisterte Herausforderungen: {game_state.challenges_completed_counter}", (SCREEN_WIDTH/2, 300), center=True)
    draw_text(surface, f"Weiteste Etappe: {game_state.mission_progress} / 10", (SCREEN_WIDTH/2, 350), center=True)
    
    # Buttons
    new_mission_rect = pygame.Rect(SCREEN_WIDTH/2 - 350, 500, 300, 70)
    pygame.draw.rect(surface, COLOR_GREEN, new_mission_rect, border_radius=10)
    draw_text(surface, "Neue Mission starten", new_mission_rect.center, center=True)
    
    exit_rect = pygame.Rect(SCREEN_WIDTH/2 + 50, 500, 300, 70)
    pygame.draw.rect(surface, COLOR_RED, exit_rect, border_radius=10)
    draw_text(surface, "Mission beenden", exit_rect.center, center=True)
    
    return new_mission_rect, exit_rect

def draw_travel_map(surface, progress: int):
    map_rect = pygame.Rect(20, 120, 60, SCREEN_HEIGHT - 240)
    pygame.draw.rect(surface, (0,0,0), map_rect, border_radius=5)
    rocket_y = map_rect.bottom - (progress * (map_rect.height / 10)) - 15
    draw_text(surface, "🚀", (map_rect.centerx, rocket_y), f=big_font, center=True)

def draw_status_bar(surface, game_state: GameState) -> List[pygame.Rect]:
    pygame.draw.rect(surface, COLOR_STATUS_ZONE, (0, 0, SCREEN_WIDTH, 100))
    portrait_rects = []
    # Resource bars... (unchanged)
    for i, player in enumerate(game_state.players):
        rect = pygame.Rect(SCREEN_WIDTH - (len(game_state.players) - i) * 100, 20, 80, 60)
        portrait_rects.append(rect)
        is_active = player == game_state.active_character
        pygame.draw.rect(surface, COLOR_PLAYER_PORTRAIT, rect, border_radius=5)
        if is_active:
            pygame.draw.rect(surface, COLOR_PLAYER_ACTIVE, rect, 4, border_radius=5)
        draw_text(surface, player.name, rect.center, center=True, f=small_font)
        if player.is_ready:
            draw_text(surface, "✓", rect.topright + pygame.Vector2(-15, 5), color=COLOR_GREEN, f=big_font)
    return portrait_rects

def draw_tasks(surface, game_state: GameState) -> Dict[str, pygame.Rect]:
    # ... (unchanged)
    return {"challenge": pygame.Rect(120, 120, 500, 260), "duty": pygame.Rect(660, 120, 500, 260)}

def draw_player_hand_and_ready_button(surface, player: Player, game_state: GameState) -> Tuple[List[pygame.Rect], pygame.Rect]:
    pygame.draw.rect(surface, COLOR_ACTION_ZONE, (0, 400, SCREEN_WIDTH, SCREEN_HEIGHT - 400))
    
    # Hand
    card_rects = []
    start_x = (SCREEN_WIDTH - (len(player.hand) * 170 - 20)) / 2
    for i, card in enumerate(player.hand):
        card_rect = pygame.Rect(start_x + i * 170, 480, 150, 220)
        card_rects.append(card_rect)
        border_width = 5 if i == game_state.selected_card_index else 2
        border_color = COLOR_YELLOW if i == game_state.selected_card_index else COLOR_WHITE
        pygame.draw.rect(surface, COLOR_CARD, card_rect, border_radius=10)
        pygame.draw.rect(surface, border_color, card_rect, border_width, border_radius=10)
        draw_text(surface, card.name, (card_rect.x + 10, card_rect.y + 10), f=small_font)
        symbol_text = "JOKER" if isinstance(card, JokerCard) else getattr(card, 'symbol', '')
        draw_text(surface, symbol_text, (card_rect.x + 10, card_rect.y + 40))
        
    # Ready Button
    ready_button_rect = pygame.Rect(SCREEN_WIDTH - 250, 420, 200, 50)
    button_color = COLOR_GREEN if player.is_ready else COLOR_RED
    pygame.draw.rect(surface, button_color, ready_button_rect, border_radius=10)
    draw_text(surface, f"{player.name} Bereit", ready_button_rect.center, center=True)
    
    return card_rects, ready_button_rect

def main():
    game_state = GameState()
    resolution_anim = None
    interactive_rects = {}

    while True:
        dt = clock.tick(60) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state.current_phase == SETUP_SCREEN:
                    for i, rect in enumerate(interactive_rects.get('char_rects', [])):
                        if rect.collidepoint(mouse_pos):
                            if i in game_state.selected_character_indices: game_state.selected_character_indices.remove(i)
                            else: game_state.selected_character_indices.add(i)
                    if interactive_rects.get('start_button') and interactive_rects['start_button'].collidepoint(mouse_pos) and 1 <= len(game_state.selected_character_indices) <= 4:
                        game_state.start_game()
                elif game_state.current_phase == AKTIONSPHASE:
                    for i, rect in enumerate(interactive_rects.get('portrait_rects', [])):
                        if rect.collidepoint(mouse_pos):
                            game_state.active_character = game_state.players[i]
                            game_state.selected_card_index = None # Deselect card on player switch
                            game_state.selected_card_obj = None
                    for i, rect in enumerate(interactive_rects.get('card_rects', [])):
                        if rect.collidepoint(mouse_pos): game_state.select_card(i, game_state.active_character)
                    if game_state.selected_card_obj:
                        if interactive_rects.get('task_rects', {}).get('challenge').collidepoint(mouse_pos):
                            game_state.assign_selected_card_to_task("challenge", game_state.active_character)
                        elif interactive_rects.get('task_rects', {}).get('duty').collidepoint(mouse_pos):
                            game_state.assign_selected_card_to_task("duty", game_state.active_character)
                    if interactive_rects.get('ready_button') and interactive_rects['ready_button'].collidepoint(mouse_pos):
                        game_state.active_character.is_ready = not game_state.active_character.is_ready
                elif game_state.current_phase == GAME_OVER:
                    if interactive_rects.get('new_mission_button') and interactive_rects['new_mission_button'].collidepoint(mouse_pos):
                        game_state = GameState() # Reset the game
                    if interactive_rects.get('exit_button') and interactive_rects['exit_button'].collidepoint(mouse_pos):
                        pygame.quit(); sys.exit()
        
        if game_state.current_phase == AKTIONSPHASE and game_state.check_if_all_players_ready():
            game_state.start_resolution_phase()
            duty_success, challenge_success, duty_provided, challenge_provided = game_state.resolve_tasks()
            game_state.apply_consequences(duty_success, challenge_success)
            challenge_reqs = game_state.current_challenge.requirements if game_state.current_challenge else {}
            resolution_anim = ResolutionAnimation(duty_success, challenge_success, duty_provided, challenge_provided, game_state.current_duty_task.requirements, challenge_reqs)
            
        if game_state.current_phase == AUFLOESUNGSPHASE and resolution_anim:
            resolution_anim.update(dt)
            if resolution_anim.is_finished:
                resolution_anim = None
                game_state.current_phase = VORBEREITUNGSPHASE
                game_state.prepare_next_round()

        screen.fill(COLOR_BACKGROUND)
        if game_state.current_phase == SETUP_SCREEN:
            char_rects, start_button_rect = draw_setup_screen(screen, game_state.selected_character_indices)
            interactive_rects = {'char_rects': char_rects, 'start_button': start_button_rect}
        elif game_state.current_phase == GAME_OVER:
            new_mission_button, exit_button = draw_game_over_screen(screen, game_state)
            interactive_rects = {'new_mission_button': new_mission_button, 'exit_button': exit_button}
        else:
            draw_travel_map(screen, game_state.mission_progress)
            portrait_rects = draw_status_bar(screen, game_state)
            task_rects = draw_tasks(screen, game_state)
            card_rects, ready_button_rect = draw_player_hand_and_ready_button(screen, game_state.active_character, game_state)
            interactive_rects = {'portrait_rects': portrait_rects, 'task_rects': list(task_rects.values()), 'card_rects': card_rects, 'ready_button': ready_button_rect}
            if resolution_anim: resolution_anim.draw(screen)

        is_over_interactive = any(rect.collidepoint(mouse_pos) for group in interactive_rects.values() if group for rect in (group if isinstance(group, list) else [group]))
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if is_over_interactive else pygame.SYSTEM_CURSOR_ARROW)
        
        pygame.display.flip()

if __name__ == "__main__":
    main()