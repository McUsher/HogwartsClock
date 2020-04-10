import time
from pygame import draw, Vector2 as Vector
from lib.timelog import Timelog
import numpy
import random
import logging


black = (0, 0, 0)      # @UnusedVariable
white = (255,255,255)  # @UnusedVariable

TYPE_STILL = "still"
TYPE_RUN = "run"
TYPE_EXPLODE = "explode"
TYPES = [TYPE_STILL, TYPE_RUN, TYPE_EXPLODE]

COR = 1 #  1+ correction for 10 digit display (2digit temp) fits perfect

class AniProps:
    
    def __init__(self):
        self.__setDefaults__()
        
    def __setDefaults__(self):
        self.typ = TYPE_STILL
        self.speed = 1
        self.fps = 1
        self.wait = 1
        self.updated = False
        
    def setDefault(self):
        self.__setDefaults__()
        return self
    
    def update(self, data):
        self.typ = data["type"]
        if not self.typ in TYPES:
            logging.error(f"animation tpye, does not exist: {data['type']}, using default  {TYPE_STILL}")
            self.typ = TYPE_STILL
        self.speed = data["speed"]
        self.fps = data["fps"]
        self.wait = data["wait"]
        self.updated = True
        logging.info(f"Update: {self}")

    def __str__(self):
        return f"AniProps(typ={self.typ}, speed={self.speed}, fps={self.fps}, wait={self.wait})"

class Animation:

    def __init__(self, screen, aniprops):
        self.screen = screen

        self.done = True
        self.aniprops = aniprops

        self.text = None
        self.textRect = None
        self.clock_rect = None
        self.info = 0

    def clear(self):
        draw.rect(self.screen,black,self.clock_rect)
        
    def start(self, text):
        self.text = text
        self.textRect = text.get_rect()
        self.center_text()

    def get_fps(self):
        return self.aniprops.fps
    
    def center_text(self):
        # horizontal center
        self.textRect.x = COR + self.clock_rect.x + int((self.clock_rect.width - self.textRect.width)/2)
        # vertical center
        self.textRect.y = self.clock_rect.y + int((self.clock_rect.height - self.textRect.height)/2)
        

class StillAni(Animation):
    
    def __init__(self, screen, aniprops):
        super().__init__(screen, aniprops)
        
    def update(self):
        self.screen.blit(self.text, self.textRect)                 #show text
        self.done = time.time() > self.timeUpdate
        
    def start(self, text):
        super().start(text)
        self.clear()
        self.timeUpdate = time.time()+10
        

class RunningAni(Animation):

    def __init__(self, screen, aniprops):
        super().__init__(screen, aniprops)
    
    def update(self):
        self.textRect.x -=self.aniprops.speed
        self.screen.blit(self.text, self.textRect)                 #show text
        self.done = self.textRect.x < -self.textRect.width
    
    def start(self, text):
        super().start(text)
        # horizontal center
        self.textRect.x = self.clock_rect.right

class ExplodeAni(Animation):
    
    def __init__(self, screen, aniprops, ref):
        super().__init__(screen, aniprops)
        self.ref = Vector(ref)
        self.stillTime = 2
        self.wait_until = 0
        self.fac_gen = FactorGenerator()
        self.__update_steps()
        
    def start(self, text):
        super().start(text)
        if(self.aniprops.updated):
            self.aniprops.updated = False
            self.__update_steps()
        t = Timelog("1")
        self.pixels = []
        #analyse the text
        ref = self.ref if self.ref else Vector(self.clock_rect.centerx,self.clock_rect.centery)
        first = True
        for x in range(self.textRect.width):
            for y in range(self.textRect.height):
                v = self.text.get_at((x,y))
                if(v == white):
                    self.pixels.append(Pix(self.textRect.x+x, self.textRect.y+y, ref, first))
                    first = False
        t.out(f"done analyse, pixelcount={len(self.pixels)}")
        self.step = -1
        self.done = False
        #print(f"first=",self.pixels[0])

    def update(self):
        self.step += 1
        if(self.step < len(self.steps)):
            super().clear()
            fac = self.steps[self.step]
            facAbs = abs(fac)          # abs here saves time at the vector calculations!
            #self.info=f"{round(fac,2)}"
            for p in self.pixels:
                self.screen.set_at(p.out(fac, facAbs), white)
            self.wait_until = time.time() + self.aniprops.wait
        else:
            # sit and wait...
            self.done = self.wait_until < time.time()

    def __update_steps(self):
        self.steps =  self.fac_gen.get(time=self.aniprops.speed, fps=self.aniprops.fps)
        
class Pix:
    """
    BE CAREFUL this is a very CPU intensive Task, espiacially on an Raspberry Pi Zero
    Know what you do in this class!!!!
    """
    def __init__(self, orgX, orgY, ref, debug):
        self.orgX = orgX
        self.orgY = orgY
        vecX = orgX - ref.x
        vecY = orgY - ref.y
        speedGrow   = 0.0 + random.random()*0.9
        speedShrink = 0.6 + random.random()*0.4
        self.growX = vecX * speedGrow
        self.growY = vecY * speedGrow
        self.shrinkX = vecX * speedShrink
        self.shrinkY = vecY * speedShrink
        self.debug = debug
        
    def debug(self, text):
        if(self.debug):
            print(text)
    
    def out(self, fac, facAbs):
        if(fac < 0):
            return (int(self.orgX - self.shrinkX * facAbs),
                    int(self.orgY - self.shrinkY * facAbs))
        else:
            return (int(self.orgX + self.growX * fac),
                    int(self.orgY + self.growY * fac))
    
    def __str__(self):
        deb = 'DEB' if self.debug else '-'
        return f"Vector(org={self.orgX}/{self.orgY} {deb})"
    
class FactorGenerator():
    def __init__(self):
        pass
    
    def get(self, time, fps):
        self.time = time
        self.fps = fps
        result = self.__getPulse_start0()
        # append first as last...
        return numpy.flip(numpy.append(result, result[0]))
        
    def __getGrow_start0(self):    
        step = numpy.pi/(self.time*self.fps)
        steps_raw = numpy.arange(0,numpy.pi,step)
        return numpy.sin(steps_raw)
    def __getGrow_start1(self):    
        step = numpy.pi/(self.time*self.fps)
        steps_raw = numpy.arange(-numpy.pi/2,numpy.pi/2,step)
        return numpy.cos(steps_raw)
    def __getPulse_start0(self):    
        step = numpy.pi*2/(self.time*self.fps)
        steps_raw = numpy.arange(0,numpy.pi*2,step)
        return numpy.sin(steps_raw)
    def __getPulse_start1(self):    
        step = numpy.pi*2/(self.time*self.fps)
        steps_raw = numpy.arange(0,numpy.pi*2,step)
        return numpy.cos(steps_raw)
        


    