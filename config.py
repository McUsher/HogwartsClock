import logging
from sys import platform

from pygame.constants import FULLSCREEN, NOFRAME


FILE="config.json"

print(f"platform=", platform)
if(platform == "win32"):
    logging.critical("Platform win32 is setting some debug stuff:")
    SCREEN_TYPE = NOFRAME
    logging.critical(f"    window properties set to NOFRAME")
    CHECK_FILE_SECONDS = 1
    logging.critical(f"    checking for {FILE} every {CHECK_FILE_SECONDS} seconds")
else:
    SCREEN_TYPE = FULLSCREEN
    CHECK_FILE_SECONDS = 20


# dimension of the display (virtual framebuffer...)
GEO_WIDTH = 132
GEO_HEIGHT = 64
GEOMETRY = "{}x{}".format(GEO_WIDTH, GEO_HEIGHT)

# visible area (BOTTOM RIGHT) for display Waveshare 2.23 OLED
CLOCK_WIDTH = 128
CLOCK_HEIGHT = 32