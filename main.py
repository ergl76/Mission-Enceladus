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
    
    draw_text(surface, f"Reisedauer: {game_state.round_counter} Runden", (SCREEN_WIDTH/2, 250), center=True)
    draw_text(surface, f"Gemeisterte Herausforderungen: {game_state.challenges_completed_counter}", (SCREEN_WIDTH/2, 300), center=True)
    draw_text(surface, f"Weiteste Etappe: {game_state.mission_progress} / 10", (SCREEN_WIDTH/2, 350), center=True)
    
    new_mission_rect = pygame.Rect(SCREEN_WIDTH/2 - 350, 500, 300, 70)
    pygame.draw.rect(surface, COLOR_GREEN, new_mission_rect, border_radius=10)
    draw_text(surface, "Neue Mission starten", new_mission_rect.center, center=True)
    
    exit_rect = pygame.Rect(SCREEN_WIDTH/2 + 50, 500, 300, 70)
    pygame.draw.rect(surface, COLOR_RED, exit_rect, border_radius=10)
    draw_text(surface, "Mission beenden", exit_rect.center, center=True)
    
    return new_mission_rect, exit_rect

def draw_travel_map(surface, progress: int, total_steps: int = 10):
    # KORREKTUR: Die Reisekarte wird nun über die gesamte Bildschirmhöhe gezeichnet.
    margin = 20
    map_rect = pygame.Rect(margin, margin, 80, SCREEN_HEIGHT - (2 * margin))
    pygame.draw.rect(surface, (0, 0, 0, 180), map_rect, border_radius=10)
    
    start_pos_y = map_rect.bottom - 40
    end_pos_y = map_rect.top + 40
    draw_text(surface, "🌍", (map_rect.centerx, start_pos_y), f=big_font, center=True)
    draw_text(surface, "🪐", (map_rect.centerx, end_pos_y), f=big_font, center=True)
    
    path_height = start_pos_y - end_pos_y
    for i in range(1, total_steps):
        y = start_pos_y - (i * path_height / total_steps)
        pygame.draw.line(surface, COLOR_GREY, (map_rect.centerx - 10, y), (map_rect.centerx + 10, y), 2)
        
    rocket_y = start_pos_y - (progress * path_height / total_steps)
    draw_text(surface, "🚀", (map_rect.centerx, rocket_y), f=big_font, center=True)

def draw_status_bar(surface, game_state: GameState) -> List[pygame.Rect]:
    pygame.draw.rect(surface, COLOR_STATUS_ZONE, (0, 0, SCREEN_WIDTH, 100))
    portrait_rects = []
    draw_text(surface, f"Fuel: {game_state.fuel}", (120, 20))
    pygame.draw.rect(surface, (0,0,0), (120, 50, 200, 30), 2)
    pygame.draw.rect(surface, COLOR_BAR_FUEL, (120, 50, game_state.fuel * 20, 30))
    draw_text(surface, f"Oxygen: {game_state.oxygen}", (370, 20))
    pygame.draw.rect(surface, (0,0,0), (370, 50, 200, 30), 2)
    pygame.draw.rect(surface, COLOR_BAR_OXYGEN, (370, 50, game_state.oxygen * 20, 30))
    draw_text(surface, f"Integrity: {game_state.integrity}", (620, 20))
    pygame.draw.rect(surface, (0,0,0), (620, 50, 200, 30), 2)
    pygame.draw.rect(surface, COLOR_BAR_INTEGRITY, (620, 50, game_state.integrity * 20, 30))
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
    pygame.draw.rect(surface, COLOR_FOCUS_ZONE, (100, 100, SCREEN_WIDTH - 120, 300))
    def draw_single_task(task, assigned_cards, rect):
        pygame.draw.rect(surface, (15,30,50), rect)
        pygame.draw.rect(surface, COLOR_WHITE, rect, 2)
        if not task: return
        draw_text(surface, task.name, rect.topleft + pygame.Vector2(20, 20))
        provided = defaultdict(int)
        jokers = sum(1 for card in assigned_cards if isinstance(card, JokerCard))
        for card in assigned_cards:
            if hasattr(card, 'symbol'): provided[card.symbol] += 1
        if jokers > 0:
            for symbol_type in constants.__dict__.values():
                if isinstance(symbol_type, str): provided[symbol_type] += jokers
        y_offset = 100
        for symbol, required in task.requirements.items():
            x_offset = 0
            draw_text(surface, f"{symbol}:", rect.topleft + pygame.Vector2(20, y_offset))
            for i in range(required):
                color = COLOR_GREEN if provided.get(symbol, 0) > i else COLOR_GREY
                pygame.draw.circle(surface, color, (rect.x + 150 + x_offset, rect.y + y_offset + 10), 10)
                x_offset += 30
            y_offset += 40
    challenge_rect = pygame.Rect(120, 120, 500, 260)
    duty_rect = pygame.Rect(660, 120, 500, 260)
    draw_single_task(game_state.current_challenge, game_state.assigned_to_challenge, challenge_rect)
    draw_single_task(game_state.current_duty_task, game_state.assigned_to_duty, duty_rect)
    return {"challenge": challenge_rect, "duty": duty_rect}

def draw_player_hand_and_ready_button(surface, player: Player, game_state: GameState) -> Tuple[List[pygame.Rect], pygame.Rect]:
    pygame.draw.rect(surface, COLOR_ACTION_ZONE, (0, 400, SCREEN_WIDTH, SCREEN_HEIGHT - 400))
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
    ready_button_rect = pygame.Rect(SCREEN_WIDTH - 250, 420, 200, 50)
    button_color = COLOR_GREEN if player.is_ready else COLOR_RED
    pygame.draw.rect(surface, button_color, ready_button_rect, border_radius=10)
    draw_text(surface, f"{player.name} Bereit", ready_button_rect.center, center=True)
    return card_rects, ready_button_rect

def main():
    game_state = GameState()
    resolution_anim = None
    
    char_rects, start_button_rect = [], None
    portrait_rects, task_rects, card_rects, ready_button_rect = [], {}, [], None

    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state.current_phase == SETUP_SCREEN:
                    for i, rect in enumerate(char_rects):
                        if rect.collidepoint(mouse_pos):
                            if i in game_state.selected_character_indices: game_state.selected_character_indices.remove(i)
                            else: game_state.selected_character_indices.add(i)
                    if start_button_rect and start_button_rect.collidepoint(mouse_pos) and 1 <= len(game_state.selected_character_indices) <= 4:
                        game_state.start_game()
                elif game_state.current_phase == AKTIONSPHASE:
                    active_player = game_state.active_character
                    for i, rect in enumerate(portrait_rects):
                        if rect.collidepoint(mouse_pos):
                            game_state.active_character = game_state.players[i]
                            game_state.selected_card_index = None
                            game_state.selected_card_obj = None
                    for i, rect in enumerate(card_rects):
                        if rect.collidepoint(mouse_pos): game_state.select_card(i, active_player)
                    if game_state.selected_card_obj:
                        # KORREKTUR: Greift auf das task_rects Dictionary zu
                        if task_rects["challenge"].collidepoint(mouse_pos):
                            game_state.assign_selected_card_to_task("challenge", active_player)
                        elif task_rects["duty"].collidepoint(mouse_pos):
                            game_state.assign_selected_card_to_task("duty", active_player)
                    if ready_button_rect and ready_button_rect.collidepoint(mouse_pos):
                        active_player.is_ready = not active_player.is_ready
                elif game_state.current_phase == GAME_OVER:
                    new_mission_button, exit_button = draw_game_over_screen(screen, game_state)
                    if new_mission_button.collidepoint(mouse_pos):
                        game_state = GameState()
                    if exit_button.collidepoint(mouse_pos):
                        pygame.quit(); sys.exit()
        
        if game_state.current_phase == AKTIONSPHASE and game_state.check_if_all_players_ready():
            game_state.start_resolution_phase()
            duty_success, challenge_success, duty_provided, challenge_provided = game_state.resolve_tasks()
            game_state.apply_consequences(duty_success, challenge_success)
            challenge_reqs = game_state.current_challenge.requirements if game_state.current_challenge else {}
            resolution_anim = ResolutionAnimation(duty_success, challenge_success, duty_provided, challenge_provided, game_state.current_duty_task.requirements, challenge_reqs)
            
        if game_state.current_phase == AUFLOESUNGSPHASE and resolution_anim:
            resolution_anim.update(0.016)
            if resolution_anim.is_finished:
                resolution_anim = None
                game_state.current_phase = VORBEREITUNGSPHASE
                game_state.prepare_next_round()

        screen.fill(COLOR_BACKGROUND)
        if game_state.current_phase == SETUP_SCREEN:
            char_rects, start_button_rect = draw_setup_screen(screen, game_state.selected_character_indices)
        elif game_state.current_phase == GAME_OVER:
            draw_game_over_screen(screen, game_state)
        else:
            draw_travel_map(screen, game_state.mission_progress)
            portrait_rects = draw_status_bar(screen, game_state)
            task_rects = draw_tasks(screen, game_state)
            card_rects, ready_button_rect = draw_player_hand_and_ready_button(screen, game_state.active_character, game_state)
            if resolution_anim: resolution_anim.draw(screen)

        all_interactive_rects = []
        if game_state.current_phase == SETUP_SCREEN:
            all_interactive_rects.extend(char_rects)
            all_interactive_rects.append(start_button_rect)
        elif game_state.current_phase == AKTIONSPHASE:
            all_interactive_rects.extend(portrait_rects)
            all_interactive_rects.extend(task_rects.values())
            all_interactive_rects.extend(card_rects)
            all_interactive_rects.append(ready_button_rect)

        is_over_interactive = any(rect and rect.collidepoint(mouse_pos) for rect in all_interactive_rects)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if is_over_interactive else pygame.SYSTEM_CURSOR_ARROW)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()