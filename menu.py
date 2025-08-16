import pygame
import sys
import subprocess
import os
import main
import livello2
import livello3

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Seleziona Livello")
font = pygame.font.SysFont(None, 48)

WHITE = (255, 255, 255)
GRAY = (30, 30, 30)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)

# Livelli
levels = [
    {"label": "Livello 1: Sir Blub", "file": "main.py", "number": 1},
    {"label": "Livello 2: Chef Plu", "file": "livello2.py", "number": 2},
    {"label": "Livello 3: ???", "file": "livello3.py", "number": 3},
]

selected_index = 0

def get_resource_path(relative_path):
    """Ottieni il percorso corretto per le risorse, sia in sviluppo che compilato"""
    if hasattr(sys, '_MEIPASS'):
        # Quando è compilato con PyInstaller
        return os.path.join(sys._MEIPASS, relative_path)
    # Quando è in sviluppo
    return os.path.join(os.path.dirname(__file__), relative_path)

def draw_menu():
    screen.fill(GRAY)
    title = font.render("Seleziona un livello", True, WHITE)
    screen.blit(title, (250, 50))

    for i, level in enumerate(levels):
        color = YELLOW if i == selected_index else BLUE
        rect = pygame.Rect(250, 150 + i * 100, 300, 60)
        pygame.draw.rect(screen, color, rect)
        label = font.render(level["label"], True, WHITE)
        screen.blit(label, (rect.x + 20, rect.y + 10))

def menu_loop():
    global selected_index
    clock = pygame.time.Clock()

    while True:
        draw_menu()
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(levels)
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(levels)
                elif event.key == pygame.K_RETURN:
                    if levels[selected_index]["number"] == 1:
                        main.main_loop()
                    elif levels[selected_index]["number"] == 2:
                        livello2.main_loop()
                    elif levels[selected_index]["number"] == 3:
                        livello3.main_loop()

menu_loop()
