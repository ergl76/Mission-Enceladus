# ==============================================================================
# main.py
# KORRIGIERT: Behebt NameError und ValueError. Stellt volle Funktionalität wieder her.
# ==============================================================================
import pygame
import sys
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict
from src.game.game_state import GameState, SETUP_SCREEN, AKTIONSPHASE, AUFLOESUNGSPHASE, VORBEREITUNGSPHASE, GAME_OVER

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mission Enceladus - Prototyp")
font = pygame.font.SysFont("Arial", 24, bold=True)
big_font = pygame.font.SysFont("Arial", 36, bold=True)
small_font = pygame.font.SysFont("Arial", 18)
clock = pygame.time.Clock()

# --- Layout & Farben ---
LEFT_PANEL_WIDTH = int(SCREEN_WIDTH * 0.15)
RIGHT_PANEL_WIDTH = int(SCREEN_WIDTH * 0.15)
CENTER_PANEL_WIDTH = SCREEN_WIDTH - LEFT_PANEL_WIDTH - RIGHT_PANEL_WIDTH
COLOR_BACKGROUND = (10, 20, 40)
COLOR_PANEL_BG = (15, 30, 50)
COLOR_WHITE = (220, 220, 220)
COLOR_GREY = (100, 100, 120)
COLOR_YELLOW = (255, 255, 0)
COLOR_GREEN = (0, 200, 0)
COLOR_RED = (200, 0, 0)

def draw_text(surface, text, pos, color=COLOR_WHITE, f=font, center=False):
    text_surface = f.render(text, True, color)
    text_rect = text_surface.get_rect(center=pos) if center else text_surface.get_rect(topleft=pos)
    surface.blit(text_surface, text_rect)

def draw_setup_screen(surface, selected_indices: Set[int]) -> Tuple[List[pygame.Rect], pygame.Rect]:
    surface.fill(COLOR_BACKGROUND)
    draw_text(surface, "CREW-MANIFEST", (SCREEN_WIDTH / 2, 100), center=True, f=big_font)
    char_rects = []
    char_names = ["Sauerstoff", "Wasser", "Temperatur", "Luftdruck"]
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
    
def draw_cockpit(surface, game_state: GameState) -> List[Tuple[pygame.Rect, str, int]]:
    interactive_elements = []
    cockpit_rect = pygame.Rect(LEFT_PANEL_WIDTH, 0, CENTER_PANEL_WIDTH, SCREEN_HEIGHT)
    
    systems = {"oxygen": "Sauerstoff", "water": "Wasser", "temperature": "Temperatur", "airpressure": "Luftdruck"}
    for i, (sys_key, sys_name) in enumerate(systems.items()):
        x_pos = cockpit_rect.x + 30 + (i * (CENTER_PANEL_WIDTH / 4))
        draw_text(surface, sys_name, (x_pos, 50))
        value = getattr(game_state, sys_key)
        for j in range(6):
            color = COLOR_GREEN if j < value else COLOR_GREY
            pygame.draw.rect(surface, color, (x_pos, 100 + j * 30, 150, 20))
        
        plus_rect = pygame.Rect(x_pos + 160, 100, 40, 95)
        minus_rect = pygame.Rect(x_pos + 160, 205, 40, 75)
        pygame.draw.rect(surface, COLOR_GREEN, plus_rect)
        pygame.draw.rect(surface, COLOR_RED, minus_rect)
        draw_text(surface, "+", plus_rect.center, center=True)
        draw_text(surface, "-", minus_rect.center, center=True)
        interactive_elements.append((plus_rect, sys_key, 1))
        interactive_elements.append((minus_rect, sys_key, -1))
        
    nav_systems = {"thrust": "Schub", "navigation": "Navigation"}
    for i, (sys_key, sys_name) in enumerate(nav_systems.items()):
        x_pos = cockpit_rect.x + 100 + (i * 450)
        draw_text(surface, sys_name, (x_pos, 350))
        value = getattr(game_state, sys_key)
        for j in range(8):
             color = COLOR_YELLOW if j < value else COLOR_GREY
             pygame.draw.rect(surface, color, (x_pos, 400 + j * 25, 150, 20))
        plus_rect = pygame.Rect(x_pos + 160, 400, 40, 95)
        minus_rect = pygame.Rect(x_pos + 160, 505, 40, 95)
        pygame.draw.rect(surface, COLOR_GREEN, plus_rect)
        pygame.draw.rect(surface, COLOR_RED, minus_rect)
        draw_text(surface, "+", plus_rect.center, center=True)
        draw_text(surface, "-", minus_rect.center, center=True)
        interactive_elements.append((plus_rect, sys_key, 1))
        interactive_elements.append((minus_rect, sys_key, -1))
        
    draw_text(surface, f"Energie: {game_state.energy_pool}", (cockpit_rect.centerx, 650), center=True, f=big_font)
    
    if game_state.current_challenge:
        challenge = game_state.current_challenge
        draw_text(surface, f"Herausforderung: {challenge.name}", (cockpit_rect.centerx, 500), center=True)
        draw_text(surface, f"Ziel: Schub {challenge.target_thrust} | Navigation {challenge.target_navigation}", (cockpit_rect.centerx, 540), center=True)
    return interactive_elements

def draw_zone1_travel_map(surface, progress: int, total_steps: int = 10):
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
    rocket_y = start_pos_y - (progress * path_height / total_steps)
    draw_text(surface, "🚀", (map_rect.centerx, rocket_y), f=big_font, center=True)
    
def draw_zone3_crew_control(surface, game_state: GameState) -> Dict:
    crew_rect = pygame.Rect(LEFT_PANEL_WIDTH + CENTER_PANEL_WIDTH, 0, RIGHT_PANEL_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(surface, COLOR_PANEL_BG, crew_rect)
    portrait_rects, ready_button_rects = [], []
    if not game_state.players: return {"portrait_rects": [], "ready_button_rects": []}
    for i, player in enumerate(game_state.players):
        y_pos = 50 + i * 150
        rect = pygame.Rect(crew_rect.x + 20, y_pos, crew_rect.width - 40, 80)
        portrait_rects.append(rect)
        is_active = player == game_state.active_character
        pygame.draw.rect(surface, COLOR_GREY, rect, border_radius=5)
        if is_active: pygame.draw.rect(surface, COLOR_YELLOW, rect, 4, border_radius=5)
        draw_text(surface, f"{player.name}", rect.center, center=True, f=small_font)
        if player.is_ready: draw_text(surface, "✓", rect.topright + pygame.Vector2(-15, 5), color=COLOR_GREEN, f=big_font)
        ready_rect = pygame.Rect(crew_rect.x + 20, y_pos + 90, crew_rect.width - 40, 40)
        ready_button_rects.append(ready_rect)
        button_color = COLOR_GREEN if player.is_ready else COLOR_RED
        pygame.draw.rect(surface, button_color, ready_rect, border_radius=10)
        draw_text(surface, "Bereit", ready_rect.center, center=True, f=small_font)
    return {"portrait_rects": portrait_rects, "ready_button_rects": ready_button_rects}

def main():
    game_state = GameState()
    interactive_rects = {}
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state.current_phase == SETUP_SCREEN:
                    if interactive_rects.get('start_button').collidepoint(mouse_pos) and 1 <= len(game_state.selected_character_indices) <= 4:
                        game_state.start_game()
                    else:
                        for i, rect in enumerate(interactive_rects.get('char_rects', [])):
                            if rect.collidepoint(mouse_pos):
                                if i in game_state.selected_character_indices: game_state.selected_character_indices.remove(i)
                                else: game_state.selected_character_indices.add(i)
                elif game_state.current_phase == AKTIONSPHASE:
                    for i, rect in enumerate(interactive_rects.get('portrait_rects', [])):
                        if rect.collidepoint(mouse_pos): game_state.active_character = game_state.players[i]
                    for i, rect in enumerate(interactive_rects.get('ready_button_rects', [])):
                        if rect.collidepoint(mouse_pos): game_state.players[i].is_ready = not game_state.players[i].is_ready
                    for rect, system, amount in interactive_rects.get('cockpit_buttons', []):
                        if rect.collidepoint(mouse_pos):
                            game_state.modify_system_value(system, amount)
                elif game_state.current_phase == GAME_OVER:
                    new_mission_button, exit_button = interactive_rects.get('new_mission_button'), interactive_rects.get('exit_button')
                    if new_mission_button and new_mission_button.collidepoint(mouse_pos): game_state = GameState()
                    if exit_button and exit_button.collidepoint(mouse_pos): pygame.quit(); sys.exit()

        if game_state.current_phase == AKTIONSPHASE and game_state.players and all(p.is_ready for p in game_state.players):
            game_state.current_phase = AUFLOESUNGSPHASE
            game_state.resolve_challenge()
            if not game_state.check_for_defeat():
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
            cockpit_buttons = draw_cockpit(screen, game_state)
            crew_controls = draw_zone3_crew_control(screen, game_state)
            interactive_rects = {**crew_controls, 'cockpit_buttons': cockpit_buttons}

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()