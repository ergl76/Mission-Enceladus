# ==============================================================================
# main.py
# Grundlegend überarbeitet für das Energie-Management-System und Cockpit-UI.
# ==============================================================================
import pygame
import sys
from typing import Dict, List, Optional, Set, Tuple
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

def draw_cockpit(surface, game_state: GameState) -> Dict[str, List[pygame.Rect]]:
    """Zeichnet das neue Cockpit mit allen Systemanzeigen und Energie-Interaktionen."""
    interactive_elements = defaultdict(list)
    cockpit_rect = pygame.Rect(LEFT_PANEL_WIDTH, 0, CENTER_PANEL_WIDTH, SCREEN_HEIGHT)
    
    # --- Lebenserhaltung ---
    systems = ["oxygen", "water", "temperature", "air_pressure"]
    for i, system in enumerate(systems):
        x_pos = cockpit_rect.x + 50 + (i * 220)
        draw_text(surface, system.title(), (x_pos, 50))
        value = getattr(game_state, system)
        # Balken
        for j in range(6):
            color = COLOR_GREEN if j < value else COLOR_GREY
            pygame.draw.rect(surface, color, (x_pos, 100 + j * 30, 150, 20))
        # Buttons
        plus_rect = pygame.Rect(x_pos + 160, 100, 40, 40)
        minus_rect = pygame.Rect(x_pos + 160, 150, 40, 40)
        pygame.draw.rect(surface, COLOR_GREEN, plus_rect)
        pygame.draw.rect(surface, COLOR_RED, minus_rect)
        draw_text(surface, "+", plus_rect.center, center=True)
        draw_text(surface, "-", minus_rect.center, center=True)
        interactive_elements[f"{system}_plus"].append(plus_rect)
        interactive_elements[f"{system}_minus"].append(minus_rect)
        
    # --- Navigation & Schub ---
    nav_systems = ["thrust", "navigation"]
    for i, system in enumerate(nav_systems):
        x_pos = cockpit_rect.x + 250 + (i * 400)
        draw_text(surface, system.title(), (x_pos, 350))
        # Balken...
        # Buttons...
        
    # --- Energie-Pool ---
    draw_text(surface, f"Energy Pool: {game_state.energy_pool}", (cockpit_rect.centerx, 600), center=True, f=big_font)
    
    # --- Herausforderung ---
    if game_state.current_challenge:
        challenge = game_state.current_challenge
        draw_text(surface, f"Ziel: {challenge.name}", (cockpit_rect.centerx, 500), center=True)
        draw_text(surface, f"Schub: {game_state.thrust}/{challenge.target_thrust} | Navigation: {game_state.navigation}/{challenge.target_navigation}",
                  (cockpit_rect.centerx, 540), center=True)

    return interactive_elements

def main():
    game_state = GameState()
    # ...
    
    while True:
        # ... Event-Schleife ...
        if game_state.current_phase == AKTIONSPHASE:
            for system_key, rects in interactive_rects.get('cockpit_buttons', {}).items():
                if rects[0].collidepoint(mouse_pos):
                    system, change = system_key.split('_')
                    amount = 1 if change == 'plus' else -1
                    game_state.modify_system_value(system, amount)
        
        # ...
        
        if game_state.current_phase == AKTIONSPHASE and all(p.is_ready for p in game_state.players):
            game_state.current_phase = AUFLOESUNGSPHASE
            game_state.resolve_challenge()
            game_state.current_phase = VORBEREITUNGSPHASE
            game_state.prepare_next_round()

        screen.fill(COLOR_BACKGROUND)
        if game_state.current_phase == SETUP_SCREEN:
            # ...
        elif game_state.current_phase == GAME_OVER:
            # ...
        else:
            # --- NEUES LAYOUT ZEICHNEN ---
            # ... draw_zone1_travel_map ...
            cockpit_buttons = draw_cockpit(screen, game_state)
            # ... draw_zone3_crew_control ...
            
            interactive_rects['cockpit_buttons'] = cockpit_buttons
        
        # ...
        pygame.display.flip()
        
if __name__ == "__main__":
    main()