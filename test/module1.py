import pygame, sys
from pygame.locals import *

pygame.init()

fpsClock = pygame.time.Clock()

# set up the window
DISPLAYSURF = pygame.display.set_mode((900, 900), 0, 32)
pygame.display.set_caption('Animation')

WHITE = (255, 255, 255)
catImg = pygame.image.load('cat.png')

catx = 10
caty = 10
direction = 'right'
dt = 0
while True: # the main game loop
    DISPLAYSURF.fill(WHITE)


    if direction == 'right':
        catx += 1 * dt
        if catx == 280:
            direction = 'down'
    elif direction == 'down':
        caty += 1 * dt
        if caty == 220:
            direction = 'left'
    elif direction == 'left':
        catx -= 1 * dt
        if catx == 10:
            direction = 'up'
    elif direction == 'up':
        caty -= 1 * dt
        if caty == 10:
            direction = 'right'

    DISPLAYSURF.blit(catImg, (catx, caty))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
    dt = fpsClock.tick(95)