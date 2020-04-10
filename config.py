import logging
from sys import platform

FILE="config.json"

print(f"platform=", platform)
if(platform == "win32"):
    logging.critical("Platform win32 is setting some debug stuff:")
    CHECK_FILE_SECONDS = 1
    logging.critical(f"    checking for {FILE} every {CHECK_FILE_SECONDS} seconds")
else:
    CHECK_FILE_SECONDS = 20


# dimension of the display (virtual framebuffer...)
GEO_WIDTH = 132
GEO_HEIGHT = 64
GEOMETRY = "{}x{}".format(GEO_WIDTH, GEO_HEIGHT)

# visible area (BOTTOM RIGHT) for display Waveshare 2.23 OLED
CLOCK_WIDTH = 128
CLOCK_HEIGHT = 32
CLOCK_X = GEO_WIDTH - CLOCK_WIDTH
CLOCK_Y = GEO_HEIGHT - CLOCK_HEIGHT
REF_EXPLODE = (GEO_WIDTH-3*16-8, GEO_HEIGHT-CLOCK_Y/2)