import threading
import logging
import os
import time
from thingspeak_get import ThingSpeakRetriever
from animator import AniProps
import json
import config
from display import Displays, getFont

class TextHandler():
    
    def __init__(self):
        self.lastFileMod = None
        self.displays = Displays()
        self.file = os.path.join(os.path.dirname(os.path.abspath(__file__)), config.FILE)
        logging.info("text config file={}".format(self.file))
        self.aniprops = AniProps().setDefault()
        self.thingspeakRetriever = ThingSpeakRetriever()
        self.showFPS = False 
        self.__check()
        
    def render(self):
        return self.displays.render(self.thingspeakRetriever.current_value, self.thingspeakRetriever.current_value_string, self.doPowerTest)
    
    def renderFPS(self, text, force=False):
        if self.showFPS or force:
            return self.fontFPS.render(text, True, (255,255,255), (0,0,0))
        return None
    
    def __setRecheck(self):
        thread = threading.Timer(self.recheck_file_seconds , self.__check)
        thread.setDaemon(True)
        thread.start()
    
    def __check(self):
        modified = time.ctime(os.path.getmtime(self.file))
        if self.lastFileMod == modified:
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
            self.displays.updateStandard(vals["display"])
            self.aniprops.update(vals["ani"])
            self.thingspeakRetriever.update_data(vals["thingspeak"])
            self.recheck_file_seconds = vals["recheckConfig"]
            if self.recheck_file_seconds < 10:
                logging.warn("Time for recheck the config file is pretty low")
            self.displays.update_countdown(None)
            if "countDown" in vals:
                self.displays.update_countdown(vals["countDown"])
            if "showFPS" in vals:
                self.showFPS = vals["showFPS"] == 1
                self.fontFPS = getFont("spleen-5x8.bdf")
            if "powerTest" in vals:
                self.doPowerTest = vals["powerTest"]
            logging.info("new text config={}".format(self.displays))
            logging.getLogger().setLevel(vals["loglevel"])
            logging.info(f"LogLevel set to {vals['loglevel']}, showFPS={self.showFPS}, recheckConfigSeconds={self.recheck_file_seconds}")
        except Exception as e:
            logging.critical(f"Could not read config file {self.file} - setting defaults")
            logging.critical(f"Exeption was: {e}")
            self.displays.setDefault(debugText = e)
            self.aniprops.setDefault()
            self.recheck_file_seconds = 5
            self.doPowerTest = False
            self.thingspeakRetriever.update_data(None)
        finally:
            self.__setRecheck()
