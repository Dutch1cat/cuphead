import pygame
import sys
import subprocess

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
    {"label": "Livello 1: Sir Blub", "file": "main.py"},
    {"label": "Livello 2: Chef Plu", "file": "livello2.py"},
    {"label": "Livello 3: ???", "file": "livello3.py"},
]

selected_index = 0

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
                    subprocess.Popen(["python", levels[selected_index]["file"]])
                    pygame.quit()
                    sys.exit()

menu_loop()
