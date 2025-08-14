
import pygame
class HealthBar:
    def __init__(self, bloop):
        self.bloop = bloop
        self.position = (20, 20)
        self.size = (200, 20)

    def draw(self, screen):
        # Calcolo percentuale
        hp_ratio = self.bloop.current_hp / self.bloop.max_hp
        # Sfondo barra
        pygame.draw.rect(screen, (50, 50, 50), (*self.position, *self.size))
        # Barra vita
        pygame.draw.rect(screen, (255, 0, 0), (
            self.position[0],
            self.position[1],
            self.size[0] * hp_ratio,
            self.size[1]
        ))