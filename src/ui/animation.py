# ==============================================================================
# src/ui/animation.py
# REFACTORING: 'crisis' wurde zu 'challenge' umbenannt.
# ==============================================================================
import pygame

# Animation States
IDLE, ANIM_DUTY_HIGHLIGHT, ANIM_DUTY_COUNT, ANIM_DUTY_RESULT, ANIM_CHALLENGE_HIGHLIGHT, ANIM_CHALLENGE_COUNT, ANIM_CHALLENGE_RESULT, FINISHED = range(8)

class ResolutionAnimation:
    """Manages the visual feedback sequence during the resolution phase."""
    def __init__(self, duty_success, challenge_success, duty_provided, challenge_provided, duty_req, challenge_req):
        self.state = ANIM_DUTY_HIGHLIGHT
        self.timer = 0
        self.font = pygame.font.SysFont("Arial", 48, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 24)
        self.duty_success, self.challenge_success = duty_success, challenge_success
        self.duty_provided, self.challenge_provided = duty_provided, challenge_provided
        self.duty_req, self.challenge_req = duty_req, challenge_req
    
    def update(self, dt):
        self.timer += dt
        transitions = {
            ANIM_DUTY_HIGHLIGHT: (0.5, ANIM_DUTY_COUNT),
            ANIM_DUTY_COUNT: (1.5, ANIM_DUTY_RESULT),
            ANIM_DUTY_RESULT: (1.5, ANIM_CHALLENGE_HIGHLIGHT),
            ANIM_CHALLENGE_HIGHLIGHT: (0.5, ANIM_CHALLENGE_COUNT),
            ANIM_CHALLENGE_COUNT: (1.5, ANIM_CHALLENGE_RESULT),
            ANIM_CHALLENGE_RESULT: (1.5, FINISHED),
        }
        if self.state in transitions and self.timer > transitions[self.state][0]:
            self.timer = 0
            self.state = transitions[self.state][1]
            
    def draw(self, surface):
        if self.state in [ANIM_DUTY_HIGHLIGHT, ANIM_DUTY_COUNT, ANIM_DUTY_RESULT]:
            self._draw_overlay_for_task(surface, "duty", self.duty_req, self.duty_provided, self.duty_success)
        if self.state in [ANIM_CHALLENGE_HIGHLIGHT, ANIM_CHALLENGE_COUNT, ANIM_CHALLENGE_RESULT] and self.challenge_req:
            self._draw_overlay_for_task(surface, "challenge", self.challenge_req, self.challenge_provided, self.challenge_success)

    def _draw_overlay_for_task(self, surface, task_name, requirements, provided, success):
        rect = pygame.Rect(680, 150, 550, 200) if task_name == "duty" else pygame.Rect(50, 150, 550, 200)
        
        if self.state in [ANIM_DUTY_HIGHLIGHT, ANIM_CHALLENGE_HIGHLIGHT]:
            pygame.draw.rect(surface, (255, 255, 0, 100), rect)
        elif self.state in [ANIM_DUTY_COUNT, ANIM_CHALLENGE_COUNT]:
            y_offset = 0
            for symbol, required in requirements.items():
                provided_val = provided.get(symbol, 0)
                text = f"{symbol}: {provided_val} / {required}"
                color = (0, 200, 0) if provided_val >= required else (200, 0, 0)
                text_surf = self.small_font.render(text, True, color)
                surface.blit(text_surf, (rect.centerx - text_surf.get_width() // 2, rect.centery - 20 + y_offset))
                y_offset += 30
        elif self.state in [ANIM_DUTY_RESULT, ANIM_CHALLENGE_RESULT]:
            result_text, result_color = ("ERFOLG", (0, 255, 0)) if success else ("FEHLSCHLAG", (255, 0, 0))
            text_surf = self.font.render(result_text, True, result_color)
            overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, rect.topleft)
            surface.blit(text_surf, (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2))

    @property
    def is_finished(self): return self.state == FINISHED