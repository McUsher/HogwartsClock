#do the logging
import logging
fmt_str = '[%(asctime)s] %(levelname)s @ line %(lineno)d: %(message)s'
# "basicConfig" is a convenience function, explained later
logging.basicConfig(level=logging.DEBUG, format=fmt_str)

from sys import version
print(f"Python version=",version)
from animator import StillAni, RunningAni, ExplodeAni


# Pygame-Modul importieren.
import pygame
import config
from texthandler import TextHandler
from animator import TYPE_RUN, TYPE_EXPLODE, TYPE_STILL
import os


# Überprüfen, ob die optionalen Text- und Sound-Module geladen werden konnten.
if not pygame.font: print('Fehler pygame.font Modul konnte nicht geladen werden!')
if not pygame.mixer: print('Fehler pygame.mixer Modul konnte nicht geladen werden!')

running = False

def main():
    # set window at x,y = 0,0
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
    # Initialisieren aller Pygame-Module und    
    # Fenster erstellen (wir bekommen eine Surface, die den Bildschirm repräsentiert).
    global pygame
    pygame.init()

    clock_rect = pygame.Rect(config.GEO_WIDTH-config.CLOCK_WIDTH, config.GEO_HEIGHT-config.CLOCK_HEIGHT, config.CLOCK_WIDTH, config.CLOCK_HEIGHT)

    textHandler = TextHandler()
    
    screen = pygame.display.set_mode((config.GEO_WIDTH, config.GEO_HEIGHT), config.SCREEN_TYPE)
    # Titel des Fensters setzen, Mauszeiger nicht verstecken und Tastendrücke wiederholt senden.
    pygame.display.set_caption("HogwartsClock")
    pygame.mouse.set_visible(0)
    pygame.key.set_repeat(1, 30)
    # Clock-Objekt erstellen, das wir benötigen, um die Framerate zu begrenzen.
    clock = pygame.time.Clock()
    # create a font object. 
    black = (0, 0, 0)      # @UnusedVariable
    white = (255,255,255)  # @UnusedVariable
    red = (255,0,0)        # @UnusedVariable
    screen.fill(black)
    screenRect = pygame.Rect(0,0,config.GEO_WIDTH, config.GEO_HEIGHT)  # @UnusedVariable
    animation = None
    animations = None
    # Die Schleife, und damit unser Spiel, läuft solange running == True.
    global running
    running = True
    while running:

        # Framerate auf x Frames pro Sekunde beschränken. Pygame wartet, falls das Programm schneller läuft.
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
        # Inhalt von screen anzeigen.
        pygame.display.update(clock_rect)

        
def handleEvents():
    global pygame
    global running
    # Alle aufgelaufenen Events holen und abarbeiten.
    for event in pygame.event.get():
        # Spiel beenden, wenn wir ein QUIT-Event finden.
        if event.type == pygame.QUIT:
            running = False
        # Wir interessieren uns auch für "Taste gedrückt"-Events.
        if event.type == pygame.KEYDOWN:
            # Wenn Escape gedrückt wird, posten wir ein QUIT-Event in Pygames Event-Warteschlange.
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
    
# Überprüfen, ob dieses Modul als Programm läuft und nicht in einem anderen Modul importiert wird.
if __name__ == '__main__':
    # Unsere Main-Funktion aufrufen.
    main()
    #     except Exception as e:
#         logger.critical("GoneFuck..:")
#         logger.critical(e)
#     finally:
#         pygame.event.post(pygame.event.Event(pygame.QUIT))
