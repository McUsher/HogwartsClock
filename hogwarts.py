#do the logging
import logging
fmt_str = '[%(asctime)s] %(levelname)s @ line %(lineno)d: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=fmt_str)

import os
from sys import version

import pygame
from pygame.constants import NOFRAME

from animator import StillAni, RunningAni, ExplodeAni
from animator import TYPE_RUN, TYPE_EXPLODE, TYPE_STILL
import config
from texthandler import TextHandler



print(f"Python version=",version)


# Check loading of Modules
if not pygame.font: logging.error('pygame.font module could not be loaded!')
if not pygame.mixer: logging.error('pygame.mixer module could not be loaded!')

running = False

def main():
    # set window at x,y = 0,0
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
    global pygame
    pygame.init()

    clock_rect = pygame.Rect(config.CLOCK_X, config.CLOCK_Y, config.CLOCK_WIDTH, config.CLOCK_HEIGHT)

    textHandler = TextHandler()
    
    screen = pygame.display.set_mode((config.GEO_WIDTH, config.GEO_HEIGHT), NOFRAME)
    pygame.display.set_caption("HogwartsClock")
    pygame.mouse.set_visible(0) #no mouse here...
    pygame.key.set_repeat(1, 30)
    clock = pygame.time.Clock()
    black = (0, 0, 0)      # @UnusedVariable
    white = (255,255,255)  # @UnusedVariable
    red = (255,0,0)        # @UnusedVariable
    screen.fill(black)
    screenRect = pygame.Rect(0,0,config.GEO_WIDTH, config.GEO_HEIGHT)  # @UnusedVariable
    animation = None
    animations = None
    global running
    running = True
    while running:
        if not animation or animation.done:
            text = textHandler.render()
            if not animations:
                animations = {
                    TYPE_STILL:     StillAni(screen),
                    TYPE_RUN:       RunningAni(screen),
                    TYPE_EXPLODE:   ExplodeAni(screen),
                }
            animation = animations.get(textHandler.aniprops.typ)
            animation.clock_rect = clock_rect
            animation.updateAniProps(textHandler.aniprops)
            animation.start(text)
                
                
            #logger.debug("rect={},  speed={}".format(textRect, speed))
        clock.tick(animation.get_fps())
        animation.update()
           
        if(animation.info != 0):
            fpsText = textHandler.renderFPS(animation.info, True)
        else:
            fpsText = textHandler.renderFPS(f"{round(clock.get_fps())}fps")

        if fpsText:
            fpsRect = fpsText.get_rect()
            fpsRect.x = config.GEO_WIDTH - fpsRect.width
            fpsRect.y = config.GEO_HEIGHT - fpsRect.height
            screen.blit(fpsText, fpsRect)
        
        handleEvents()
        pygame.display.update(clock_rect)

        
def handleEvents():
    global pygame
    global running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
    
# check if we are main....
if __name__ == '__main__':
    main()
