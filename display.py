from datetime import date, datetime
import logging
import os
import time

from pygame import font, draw
from pygame.surface import Surface
import config


path = os.path.dirname(os.path.abspath(__file__))
fontpath = os.path.join(path, "fonts")
print(f"fontpath={fontpath}")

def getDefaultFont():
    return font.Font(os.path.join(fontpath, "spleen-16x32_mod.bdf"),32)

def getFont(font_name=None):
    try:
        use = font.Font(os.path.join(fontpath,font_name),10)
    except:
        use = getDefaultFont()
        logging.critical("Font not found: {}".format(font_name))
    logging.info("Font set to: {}".format(use))
    return use

class Displays(object):
    def __init__(self):
        self.standard = Standard()
        self.countdown = CountDown()
        self.do_standard = True
    
    def setDefault(self):
        self.standard.__setDefaults__()
        self.countdown.__setDefaults__()
        self.do_standard = True
    
    def updateStandard(self, json):
        self.standard.__updateData__(json)
    
    def update_countdown(self, json):
        self.countdown.__updateData__(json)
        
    def render(self, val, val_str):
        if not self.countdown.active:
            return self.standard.render(val, val_str)
        self.do_standard = not self.do_standard
        if self.do_standard:
            return self.standard.render(val, val_str)
        return self.countdown.render()

class Standard(object):

    def __init__(self):
        self.__setDefaults__()

    def render(self, val, val_str):
        hours = time.strftime("%H")
        minutes = time.strftime("%M")
        try:
            dynSep = " " if val < -9 else "  "
            txt = self.display_string.format(h=hours, m=minutes, dynSep=dynSep, val=val_str)
        except Exception as e:
            logging.error(f"parsing error: {e}")
            txt = "ParsingError"
        logging.debug("Rendering text:{}".format(txt))
        return self.font.render(txt, True, (255,255,255), (0,0,0))

        
    def __updateData__(self, json):
        print(json["font"])
        self.font = getFont(json["font"])
        self.display_string = json["displayString"]
    
    def __setDefaults__(self):
        self.font = getDefaultFont()
        self.display_string = "{h}:{m} {temp}°"


class CountDown(Standard):
    def __init__(self):
        super().__init__()

    def render(self):
        txts = self.display_string.format(val=self.count).split("\n")
        logging.debug(f"countdown={txts}")
        if len(txts) == 1:
            return self.font.render(txts[0], True, (255,255,255), (0,0,0))
        """ we have a multiline text...."""
        fnts = []
        maxW = 0
        totH = 0
        for t in txts:
            f = self.font.render(t, True, (255,255,255), (0,0,0))
            r = f.get_rect()
            totH += r.height
            maxW = max(maxW, r.width)
            fnts.append(f)
        size = w, h = (config.CLOCK_WIDTH, config.CLOCK_HEIGHT)
        surface =  Surface(size)
        curY = (h-totH)/2
        for f in fnts:
            r = f.get_rect()
            r.x = (w - r.width) / 2
            r.y = curY
            surface.blit(f, r)
            curY += r.height
        return surface
         
        
    def __setDefaults__(self):
        self.display_string = ""
        self.font = getDefaultFont()
        self.count = 0
        self.active = False
        
    def __updateData__(self,json):
        if json:
            self.display_string = json["displayString"]
            self.font = getFont(json["font"])
            self.active = json["active"]
            self.date = datetime.strptime(json["date"], "%Y-%m-%d").date()
            self.count = (self.date - date.today()).days
            self.active = self.active and self.count >= 0
        else:
            self.__setDefaults__()
        logging.debug(f"countdown, active={self.active}, count={self.count}")







