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

# --- NEUE LAYOUT-ZEICHENFUNKTIONEN ---

def draw_zone1_travel_map(surface, progress: int, total_steps: int = 10):
    """Zone 1: Zeichnet die Reisekarte in der linken Spalte."""
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
    """Zone 2: Zeichnet das gesamte zentrale Spielfeld."""
    # Definiere die Bereiche innerhalb der zentralen Spalte
    status_rect = pygame.Rect(LEFT_PANEL_WIDTH, 0, CENTER_PANEL_WIDTH, 100)
    remaining_height = SCREEN_HEIGHT - status_rect.height
    focus_rect = pygame.Rect(LEFT_PANEL_WIDTH, status_rect.height, CENTER_PANEL_WIDTH, remaining_height / 2)
    action_rect = pygame.Rect(LEFT_PANEL_WIDTH, status_rect.height + focus_rect.height, CENTER_PANEL_WIDTH, remaining_height / 2)
    
    # 2a: Statusleiste
    pygame.draw.rect(surface, COLOR_STATUS_ZONE, status_rect)
    draw_text(surface, f"Fuel: {game_state.fuel}", (status_rect.x + 20, 20))
    pygame.draw.rect(surface, COLOR_GREY, (status_rect.x + 20, 50, 200, 30), 2)
    pygame.draw.rect(surface, (200,100,0), (status_rect.x + 20, 50, game_state.fuel * 20, 30))
    # ... weitere Ressourcen ...
    
    # 2b: Fokus-Bereich (Aufgaben)
    pygame.draw.rect(surface, (30,60,90), focus_rect)
    challenge_slot = pygame.Rect(focus_rect.x + 20, focus_rect.y + 20, focus_rect.width / 2 - 30, focus_rect.height - 40)
    duty_slot = pygame.Rect(focus_rect.centerx + 10, focus_rect.y + 20, focus_rect.width / 2 - 30, focus_rect.height - 40)
    # ... Aufgaben zeichnen (Logik unverändert) ...
    
    # 2c: Aktions-Bereich (Handkarten)
    pygame.draw.rect(surface, (20,40,60), action_rect)
    card_rects = []
    player = game_state.active_character
    start_x = action_rect.centerx - (len(player.hand) * 170 - 20) / 2
    for i, card in enumerate(player.hand):
        card_rect = pygame.Rect(start_x + i * 170, action_rect.y + 30, 150, 220)
        card_rects.append(card_rect)
        # ... Karten zeichnen (Logik unverändert) ...

    return {
        "challenge_slot": challenge_slot,
        "duty_slot": duty_slot,
        "card_rects": card_rects
    }
    
def draw_zone3_crew_control(surface, game_state: GameState) -> Dict:
    """Zone 3: Zeichnet die Crew-Steuerung in der rechten Spalte."""
    crew_rect = pygame.Rect(LEFT_PANEL_WIDTH + CENTER_PANEL_WIDTH, 0, RIGHT_PANEL_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(surface, COLOR_PANEL_BG, crew_rect)
    
    portrait_rects = []
    ready_button_rects = []
    
    for i, player in enumerate(game_state.players):
        y_pos = 50 + i * 150
        # Porträt
        rect = pygame.Rect(crew_rect.x + 20, y_pos, crew_rect.width - 40, 80)
        portrait_rects.append(rect)
        is_active = player == game_state.active_character
        pygame.draw.rect(surface, COLOR_GREY, rect, border_radius=5)
        if is_active:
            pygame.draw.rect(surface, COLOR_YELLOW, rect, 4, border_radius=5)
        draw_text(surface, player.name, rect.center, center=True, f=small_font)
        if player.is_ready:
            draw_text(surface, "✓", rect.topright + pygame.Vector2(-15, 5), color=COLOR_GREEN, f=big_font)
            
        # Ready Button
        ready_rect = pygame.Rect(crew_rect.x + 20, y_pos + 90, crew_rect.width - 40, 40)
        ready_button_rects.append(ready_rect)
        button_color = COLOR_GREEN if player.is_ready else COLOR_RED
        pygame.draw.rect(surface, button_color, ready_rect, border_radius=10)
        draw_text(surface, "Bereit", ready_rect.center, center=True, f=small_font)
        
    return {
        "portrait_rects": portrait_rects,
        "ready_button_rects": ready_button_rects
    }

def main():
    game_state = GameState()
    # ... andere Variablen ...
    
    while True:
        # ... Event-Handling (Logik bleibt gleich, aber die Rects kommen aus neuen Quellen) ...
        
        screen.fill(COLOR_BACKGROUND)
        if game_state.current_phase == SETUP_SCREEN:
            # ... Setup-Screen zeichnen ...
        elif game_state.current_phase == GAME_OVER:
            # ... Game-Over-Screen zeichnen ...
        else:
            # --- NEUES LAYOUT ZEICHNEN ---
            draw_zone1_travel_map(screen, game_state.mission_progress)
            center_rects = draw_zone2_center_panel(screen, game_state)
            crew_rects = draw_zone3_crew_control(screen, game_state)
            
            # Interaktive Rects für Klick-Logik sammeln
            interactive_rects = {
                'challenge_slot': center_rects['challenge_slot'],
                'duty_slot': center_rects['duty_slot'],
                'card_rects': center_rects['card_rects'],
                'portrait_rects': crew_rects['portrait_rects'],
                'ready_button_rects': crew_rects['ready_button_rects']
            }
            # ... Animationen zeichnen ...
        
        # ... Maus-Cursor Logik ...
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()