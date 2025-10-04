import pygame

#Basics
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
TITLE = "Industrial Capitalist"
FPS = 60

clock = pygame.time.Clock()
tile_size = 30

pygame.display.set_caption(TITLE)


#Colours
BGC = (50, 50, 50) #BackGroundColour
WHITE = (255, 255, 255)
