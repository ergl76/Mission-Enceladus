# ==============================================================================
# src/ui/animation.py
# NEUE DATEI: Manager für die "Sequenz der Wahrheit"
# ==============================================================================
import pygame
from typing import Dict

# Animation States
IDLE = 0
ANIM_DUTY_HIGHLIGHT = 1
ANIM_DUTY_COUNT = 2
ANIM_DUTY_RESULT = 3
ANIM_CRISIS_HIGHLIGHT = 4
ANIM_CRISIS_COUNT = 5
ANIM_CRISIS_RESULT = 6
FINISHED = 7

class ResolutionAnimation:
    """Manages the visual feedback sequence during the resolution phase."""

    def __init__(self, duty_success, crisis_success, duty_provided, crisis_provided, duty_req, crisis_req):
        self.state = ANIM_DUTY_HIGHLIGHT
        self.timer = 0
        self.font = pygame.font.SysFont("Arial", 48, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 24)

        self.duty_success = duty_success
        self.crisis_success = crisis_success
        self.duty_provided = duty_provided
        self.crisis_provided = crisis_provided
        self.duty_req = duty_req
        self.crisis_req = crisis_req
    
    def update(self, dt):
        """Updates the animation timer and state."""
        self.timer += dt
        
        if self.state == ANIM_DUTY_HIGHLIGHT and self.timer > 0.5:
            self.timer = 0
            self.state = ANIM_DUTY_COUNT
        elif self.state == ANIM_DUTY_COUNT and self.timer > 1.5:
            self.timer = 0
            self.state = ANIM_DUTY_RESULT
        elif self.state == ANIM_DUTY_RESULT and self.timer > 1.5:
            self.timer = 0
            self.state = ANIM_CRISIS_HIGHLIGHT
        elif self.state == ANIM_CRISIS_HIGHLIGHT and self.timer > 0.5:
            self.timer = 0
            self.state = ANIM_CRISIS_COUNT
        elif self.state == ANIM_CRISIS_COUNT and self.timer > 1.5:
            self.timer = 0
            self.state = ANIM_CRISIS_RESULT
        elif self.state == ANIM_CRISIS_RESULT and self.timer > 1.5:
            self.timer = 0
            self.state = FINISHED
            
    def draw(self, surface):
        """Draws the animation overlays on the screen."""
        if self.state == IDLE or self.state == FINISHED:
            return

        # --- Duty Animation ---
        if self.state in [ANIM_DUTY_HIGHLIGHT, ANIM_DUTY_COUNT, ANIM_DUTY_RESULT]:
            self._draw_overlay_for_task(surface, "duty", self.duty_req, self.duty_provided, self.duty_success)
            
        # --- Crisis Animation ---
        if self.state in [ANIM_CRISIS_HIGHLIGHT, ANIM_CRISIS_COUNT, ANIM_CRISIS_RESULT]:
            self._draw_overlay_for_task(surface, "crisis", self.crisis_req, self.crisis_provided, self.crisis_success)

    def _draw_overlay_for_task(self, surface, task_name, requirements, provided, success):
        # Determine rect based on task name
        x_pos = 680 if task_name == "duty" else 50
        rect = pygame.Rect(x_pos, 150, 550, 200)

        # Highlight
        if self.state in [ANIM_DUTY_HIGHLIGHT, ANIM_CRISIS_HIGHLIGHT]:
            pygame.draw.rect(surface, (255, 255, 0, 100), rect)

        # Counter
        if self.state in [ANIM_DUTY_COUNT, ANIM_CRISIS_COUNT]:
            y_offset = 0
            for symbol, required in requirements.items():
                provided_val = provided.get(symbol, 0)
                text = f"{symbol}: {provided_val} / {required}"
                color = (0, 200, 0) if provided_val >= required else (200, 0, 0)
                text_surf = self.small_font.render(text, True, color)
                surface.blit(text_surf, (rect.centerx - text_surf.get_width() // 2, rect.centery - 20 + y_offset))
                y_offset += 30

        # Result Text
        if self.state in [ANIM_DUTY_RESULT, ANIM_CRISIS_RESULT]:
            result_text = "ERFOLG" if success else "FEHLSCHLAG"
            result_color = (0, 255, 0) if success else (255, 0, 0)
            text_surf = self.font.render(result_text, True, result_color)
            overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, rect.topleft)
            surface.blit(text_surf, (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2))

    @property
    def is_finished(self):
        return self.state == FINISHED