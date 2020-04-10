import threading
import logging
import os
import time
from thingspeak_get import ThingSpeakRetriever
from pygame import font
from animator import AniProps
import json
import config

class TextHandler():
    
    def __init__(self):
        self.lastFileMod = None
        path = os.path.dirname(os.path.abspath(__file__))
        self.fontpath = os.path.join(path, "fonts")
        self.file = os.path.join(os.path.dirname(os.path.abspath(__file__)), config.FILE)
        logging.info("text config file={}".format(self.file))
        self.aniprops = AniProps().setDefault()
        self.thingspeakRetriever = ThingSpeakRetriever()
        self.showFPS = False 
        self.__check()
        
    def render(self):
        hours = time.strftime("%H")
        minutes = time.strftime("%M")
        try:
            txt = self.displayString.format(h=hours, m=minutes, temp=self.thingspeakRetriever.currentTemp)
        except:
            txt = "ParsingError"
        logging.debug("Rendering text:{}".format(txt))
        return self.currentFont.render(txt, True, (255,255,255), (0,0,0))
    
    def renderFPS(self, text, force=False):
        if self.showFPS or force:
            return self.fontFPS.render(text, True, (255,255,255), (0,0,0))
        return None
    
    def __getFont(self, name=None):
        try:
            use = font.Font(os.path.join(self.fontpath,name),10)
        except:
            use = font.Font(os.path.join(self.fontpath, "spleen-16x32_mod.bdf"),32)
            logging.critical("Font not found: {}".format(name))
        logging.info("Font set to: {}".format(use))
        return use

    def __setRecheck(self):
        thread = threading.Timer(config.CHECK_FILE_SECONDS, self.__check)
        thread.setDaemon(True)
        thread.start()
    
    def __check(self):
        modified = time.ctime(os.path.getmtime(self.file))
        if self.lastFileMod and self.lastFileMod == modified:
            #logging.debug(" no change in text config file={}".format(self.file))
            self.__setRecheck()
            return
        self.lastFileMod = modified
        try:
            vals = eval(open(self.file, encoding="utf-8").read())
            # restart ?
            if(vals["restart"]==1):
                vals["restart"] = 0
                with open(self.file, 'w', encoding='utf8') as outfile:
                    json.dump(vals, outfile, indent=4, ensure_ascii=False)
                os.system("./killRunClock.sh")
            self.displayString = vals["displayString"]
            self.aniprops.update(vals["ani"])
            self.currentFont = self.__getFont(vals["font"])
            self.thingspeakRetriever.set_update_time(vals["updateTemp"])
            if("showFPS" in vals):
                self.showFPS = vals["showFPS"] == 1
                self.fontFPS = font.Font(os.path.join(self.fontpath,"spleen-5x8.bdf"), 8)
            logging.getLogger().setLevel(vals["loglevel"])
            logging.critical("LogLevel set to {}, showFPS={}".format(vals["loglevel"], self.showFPS))
            logging.info("new text config={}".format(self.displayString))
        except Exception as e:
            logging.critical("Could not read config file {} - setting defaults".format(self.file))
            logging.critical("Exeption was: {}".format(e))
            self.displayString = "{h}:{m} {temp}°"
            self.aniprops.setDefault()
            self.thingspeakRetriever.set_update_time(0)
            self.currentFont = self.__getFont()
        finally:
            self.__setRecheck()
