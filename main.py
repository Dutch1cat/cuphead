import pygame
import os
import sys
from bloop import Bloop
from health_bar import HealthBar
from sirBlub import SirBlub
# === Configurazione iniziale ===
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

blub = SirBlub(400, HEIGHT - 64)
bloop = Bloop(100, HEIGHT - 64)
health_bar = HealthBar(bloop)
running = True

while running:
    screen.fill((200, 230, 255))  # sfondo azzurrino

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    bloop.update(keys)
    bloop.draw(screen)
    health_bar.draw(screen)
    blub.update(bloop)
    blub.draw(screen)

    keys = pygame.key.get_pressed()
    

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()