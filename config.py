FILE="config.json"

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