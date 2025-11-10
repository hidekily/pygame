import pygame
import sys
import os

# init our game
pygame.init()
# defines our screen size 
screenX, screenY = 980, 480
screen = pygame.display.set_mode((screenX, screenY))

# lets our app run
running = True

# page var
gameScreen = 1

bg1 = pygame.image.load('./images/test.jpg').convert()
bg1 = pygame.transform.scale(bg1, (screenX, screenY))

bg2 = pygame.image.load('./images/test2.jpg').convert()
bg2 = pygame.transform.scale(bg2, (screenX, screenY))

# init screen button
buttonInit = pygame.Rect(25, 25, 200, 50)

# draws our button
def drawButton(button, text, color):
    pygame.draw.rect(screen, color, button)
    font = pygame.font.Font(None, 36)
    textSurface = font.render(text, True, (255, 255, 255))
    textRect = textSurface.get_rect(center=button.center)
    screen.blit(textSurface, textRect)

# start of our application
while running:
    os.system('cls')
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            # page 1 
            if gameScreen == 1:
                if buttonInit.collidepoint(pos): 
                    gameScreen = 2 

            # page 2
            elif gameScreen == 2:
                if buttonInit.collidepoint(pos): 
                    gameScreen = 1

    if gameScreen == 1:
        screen.blit(bg1, (0, 0))  
        drawButton(buttonInit, "team selection", (0, 128, 255))  
    elif gameScreen == 2:
        screen.blit(bg2, (0, 0))  
        drawButton(buttonInit, "back to init screen", (255, 128, 40))

    # reloading our games bg
    pygame.display.flip()