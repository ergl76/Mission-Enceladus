# ==============================================================================
# main.py
# Umfassend überarbeitet, um das neue 3-Spalten-Layout zu implementieren.
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

# --- Layout-Konstanten ---
LEFT_PANEL_WIDTH = int(SCREEN_WIDTH * 0.15)
RIGHT_PANEL_WIDTH = int(SCREEN_WIDTH * 0.15)
CENTER_PANEL_WIDTH = SCREEN_WIDTH - LEFT_PANEL_WIDTH - RIGHT_PANEL_WIDTH

# Colors
COLOR_BACKGROUND = (10, 20, 40)
COLOR_WHITE = (220, 220, 220)
COLOR_GREY = (100, 100, 120)
COLOR_YELLOW = (255, 255, 0)
COLOR_GREEN = (0, 200, 0)
COLOR_RED = (200, 0, 0)
COLOR_PANEL_BG = (15, 30, 50)
COLOR_STATUS_ZONE = (20, 40, 60)
COLOR_CARD = (50, 80, 120)

# Globale Variable für die Raketenanimation
rocket_current_y, rocket_target_y = 0, 0

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

def draw_zone1_travel_map(surface, progress: int, total_steps: int = 10):
    global rocket_current_y, rocket_target_y
    map_rect = pygame.Rect(0, 0, LEFT_PANEL_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(surface, COLOR_PANEL_BG, map_rect)

    start_pos_y = map_rect.height - 50
    end_pos_y = 50
    draw_text(surface, "🌍", (map_rect.centerx, start_pos_y), f=big_font, center=True)
    draw_text(surface, "🪐", (map_rect.centerx, end_pos_y), f=big_font, center=True)
    
    path_height = start_pos_y - end_pos_y
    for i in range(1, total_steps):
        y = start_pos_y - (i * path_height / total_steps)
        pygame.draw.line(surface, COLOR_GREY, (map_rect.centerx - 10, y), (map_rect.centerx + 10, y), 2)

    target_y = start_pos_y - (progress * path_height / total_steps)
    rocket_target_y = target_y
    if abs(rocket_current_y - rocket_target_y) > 0.5:
        rocket_current_y += (rocket_target_y - rocket_current_y) * 0.05
    else:
        rocket_current_y = rocket_target_y
    draw_text(surface, "🚀", (map_rect.centerx, rocket_current_y), f=big_font, center=True)

def draw_zone2_center_panel(surface, game_state: GameState) -> Dict:
    status_rect = pygame.Rect(LEFT_PANEL_WIDTH, 0, CENTER_PANEL_WIDTH, 100)
    remaining_height = SCREEN_HEIGHT - status_rect.height
    focus_rect = pygame.Rect(LEFT_PANEL_WIDTH, status_rect.height, CENTER_PANEL_WIDTH, remaining_height / 2)
    action_rect = pygame.Rect(LEFT_PANEL_WIDTH, status_rect.height + focus_rect.height, CENTER_PANEL_WIDTH, remaining_height / 2)
    
    pygame.draw.rect(surface, COLOR_STATUS_ZONE, status_rect)
    draw_text(surface, f"Fuel: {game_state.fuel}", (status_rect.x + 20, 20))
    pygame.draw.rect(surface, COLOR_GREY, (status_rect.x + 20, 50, 200, 30), 2)
    pygame.draw.rect(surface, (200,100,0), (status_rect.x + 20, 50, game_state.fuel * 20, 30))
    # ... more resources ...
    
    pygame.draw.rect(surface, (30,60,90), focus_rect)
    challenge_slot = pygame.Rect(focus_rect.x + 20, focus_rect.y + 20, focus_rect.width / 2 - 30, focus_rect.height - 40)
    duty_slot = pygame.Rect(focus_rect.centerx + 10, focus_rect.y + 20, focus_rect.width / 2 - 30, focus_rect.height - 40)
    
    # KORREKTUR: Die Logik zum Zeichnen der Aufgaben wurde hier wieder eingefügt.
    def draw_single_task(task, assigned_cards, rect):
        pygame.draw.rect(surface, COLOR_PANEL_BG, rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_WHITE, rect, 2, border_radius=10)
        if not task: return
        draw_text(surface, task.name, rect.topleft + pygame.Vector2(20, 20))
        provided = defaultdict(int)
        jokers = sum(1 for card in assigned_cards if isinstance(card, JokerCard))
        for card in assigned_cards:
            if hasattr(card, 'symbol'): provided[card.symbol] += 1
        if jokers > 0:
            for symbol_type in constants.__dict__.values():
                if isinstance(symbol_type, str): provided[symbol_type] += jokers
        y_offset = 60
        for symbol, required in task.requirements.items():
            x_offset = 0
            draw_text(surface, f"{symbol}:", rect.topleft + pygame.Vector2(20, y_offset))
            for i in range(required):
                color = COLOR_GREEN if provided.get(symbol, 0) > i else COLOR_GREY
                pygame.draw.circle(surface, color, (rect.x + 150 + x_offset, rect.y + y_offset + 10), 10)
                x_offset += 30
            y_offset += 40
            
    draw_single_task(game_state.current_challenge, game_state.assigned_to_challenge, challenge_slot)
    draw_single_task(game_state.current_duty_task, game_state.assigned_to_duty, duty_slot)
    
    pygame.draw.rect(surface, (20,40,60), action_rect)
    card_rects = []
    player = game_state.active_character
    if player:
        start_x = action_rect.centerx - (len(player.hand) * 170 - 20) / 2
        for i, card in enumerate(player.hand):
            card_rect = pygame.Rect(start_x + i * 170, action_rect.y + (action_rect.height - 220) / 2, 150, 220)
            card_rects.append(card_rect)
            border_color = COLOR_YELLOW if i == game_state.selected_card_index else COLOR_WHITE
            pygame.draw.rect(surface, COLOR_CARD, card_rect, border_radius=10)
            pygame.draw.rect(surface, border_color, card_rect, 2, border_radius=10)
            draw_text(surface, card.name, (card_rect.x + 10, card_rect.y + 10), f=small_font)
            symbol_text = "JOKER" if isinstance(card, JokerCard) else getattr(card, 'symbol', '')
            draw_text(surface, symbol_text, (card_rect.x + 10, card_rect.y + 40))

    return {"challenge_slot": challenge_slot, "duty_slot": duty_slot, "card_rects": card_rects}
    
def draw_zone3_crew_control(surface, game_state: GameState) -> Dict:
    crew_rect = pygame.Rect(LEFT_PANEL_WIDTH + CENTER_PANEL_WIDTH, 0, RIGHT_PANEL_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(surface, COLOR_PANEL_BG, crew_rect)
    
    portrait_rects, ready_button_rects = [], []
    if not game_state.players:
        return {"portrait_rects": [], "ready_button_rects": []}

    for i, player in enumerate(game_state.players):
        y_pos = 50 + i * 150
        rect = pygame.Rect(crew_rect.x + 20, y_pos, crew_rect.width - 40, 80)
        portrait_rects.append(rect)
        is_active = player == game_state.active_character
        pygame.draw.rect(surface, COLOR_GREY, rect, border_radius=5)
        if is_active:
            pygame.draw.rect(surface, COLOR_YELLOW, rect, 4, border_radius=5)
        draw_text(surface, player.name, rect.center, center=True, f=small_font)
        if player.is_ready:
            draw_text(surface, "✓", rect.topright + pygame.Vector2(-15, 5), color=COLOR_GREEN, f=big_font)
            
        ready_rect = pygame.Rect(crew_rect.x + 20, y_pos + 90, crew_rect.width - 40, 40)
        ready_button_rects.append(ready_rect)
        button_color = COLOR_GREEN if player.is_ready else COLOR_RED
        pygame.draw.rect(surface, button_color, ready_rect, border_radius=10)
        draw_text(surface, "Bereit", ready_rect.center, center=True, f=small_font)
        
    return {"portrait_rects": portrait_rects, "ready_button_rects": ready_button_rects}

def main():
    game_state = GameState()
    interactive_rects = {}
    resolution_anim = None
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state.current_phase == SETUP_SCREEN:
                    if interactive_rects.get('start_button') and interactive_rects['start_button'].collidepoint(mouse_pos) and 1 <= len(game_state.selected_character_indices) <= 4:
                        game_state.start_game()
                    else:
                        for i, rect in enumerate(interactive_rects.get('char_rects', [])):
                            if rect.collidepoint(mouse_pos):
                                if i in game_state.selected_character_indices: game_state.selected_character_indices.remove(i)
                                else: game_state.selected_character_indices.add(i)
                elif game_state.current_phase == AKTIONSPHASE:
                    for i, rect in enumerate(interactive_rects.get('portrait_rects', [])):
                        if rect.collidepoint(mouse_pos):
                            game_state.active_character = game_state.players[i]
                            game_state.selected_card_index = None
                            game_state.selected_card_obj = None
                    for i, rect in enumerate(interactive_rects.get('ready_button_rects', [])):
                        if rect.collidepoint(mouse_pos):
                            game_state.players[i].is_ready = not game_state.players[i].is_ready

                    for i, rect in enumerate(interactive_rects.get('card_rects', [])):
                        if rect.collidepoint(mouse_pos):
                            game_state.select_card(i, game_state.active_character)
                    if game_state.selected_card_obj:
                        if interactive_rects.get('challenge_slot').collidepoint(mouse_pos):
                            game_state.assign_selected_card_to_task("challenge", game_state.active_character)
                        elif interactive_rects.get('duty_slot').collidepoint(mouse_pos):
                            game_state.assign_selected_card_to_task("duty", game_state.active_character)

                elif game_state.current_phase == GAME_OVER:
                    if interactive_rects.get('new_mission_button').collidepoint(mouse_pos):
                        game_state = GameState()
                    if interactive_rects.get('exit_button').collidepoint(mouse_pos):
                        pygame.quit(); sys.exit()
        
        # KORREKTUR: Die Logik zum Rundenabschluss wurde hier eingefügt.
        if game_state.current_phase == AKTIONSPHASE and game_state.players and all(p.is_ready for p in game_state.players):
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
            interactive_rects = {'char_rects': char_rects, 'start_button': start_button_rect}
        elif game_state.current_phase == GAME_OVER:
            new_mission_button, exit_button = draw_game_over_screen(screen, game_state)
            interactive_rects = {'new_mission_button': new_mission_button, 'exit_button': exit_button}
        else:
            draw_zone1_travel_map(screen, game_state.mission_progress)
            center_rects = draw_zone2_center_panel(screen, game_state)
            crew_rects = draw_zone3_crew_control(screen, game_state)
            
            interactive_rects = {
                'challenge_slot': center_rects['challenge_slot'],
                'duty_slot': center_rects['duty_slot'],
                'card_rects': center_rects['card_rects'],
                'portrait_rects': crew_rects['portrait_rects'],
                'ready_button_rects': crew_rects['ready_button_rects']
            }
            if resolution_anim: resolution_anim.draw(screen)
        
        all_interactive_rects = []
        for key, value in interactive_rects.items():
            if isinstance(value, list):
                all_interactive_rects.extend(value)
            elif isinstance(value, pygame.Rect):
                all_interactive_rects.append(value)
        
        is_over_interactive = any(rect and rect.collidepoint(mouse_pos) for rect in all_interactive_rects)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if is_over_interactive else pygame.SYSTEM_CURSOR_ARROW)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()