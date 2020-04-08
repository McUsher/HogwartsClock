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
        
        

    def __str__(self):
        return f"AniProps(typ={self.typ}, speed={self.speed}, fps={self.fps})"

class Animation:

    def __init__(self, screen):
        self.screen = screen

        self.done = True
        self.aniprops = None

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

    def updateAniProps(self, aniprops):
        self.aniprops = aniprops
        
    def get_fps(self):
        return self.aniprops.fps
    
    def center_text(self):
        # horizontal center
        self.textRect.x = COR + self.clock_rect.x + int((self.clock_rect.width - self.textRect.width)/2)
        # vertical center
        self.textRect.y = self.clock_rect.y + int((self.clock_rect.height - self.textRect.height)/2)
        

class StillAni(Animation):
    
    def __init__(self, screen):
        super().__init__(screen)
        
    def update(self):
        self.screen.blit(self.text, self.textRect)                 #show text
        self.done = time.time() > self.timeUpdate
        
    def start(self, text):
        super().start(text)
        self.clear()
        self.timeUpdate = time.time()+10
        

class RunningAni(Animation):

    def __init__(self, screen):
        super().__init__(screen)
    
    def update(self):
        self.textRect.x -=self.aniprops.speed
        self.screen.blit(self.text, self.textRect)                 #show text
        self.done = self.textRect.x < -self.textRect.width
    
    def start(self, text):
        super().start(text)
        # horizontal center
        self.textRect.x = self.clock_rect.right

class ExplodeAni(Animation):
    
    def __init__(self, screen):
        super().__init__(screen)
        self.stillTime = 2
        self.wait_until = 0
        self.fac_gen = FactorGenerator()
        
    def updateAniProps(self, aniprops):
        super().updateAniProps(aniprops)
        self.steps =  self.fac_gen.get(time=self.aniprops.speed, fps=self.aniprops.fps)
        
    def start(self, text):
        super().start(text)
        t = Timelog("1")
        self.pixels = []
        #analyse the text
        ref = Vector(self.clock_rect.centerx,self.clock_rect.centery)
        first = True
        for x in range(self.textRect.width):
            for y in range(self.textRect.height):
                v = self.text.get_at((x,y))
                if(v == white):
                    self.pixels.append(Pix(self.textRect.x+x, self.textRect.y+y, ref, first))
                    first = False
        t.out("done analyse")
        self.step = -1
        self.done = False
        #print(f"first=",self.pixels[0])

    def update(self):
        self.step += 1
        if(self.step < len(self.steps)):
            super().clear()
            fac = self.steps[self.step]
            #self.info=f"{round(fac,2)}"
            self.drawWithFac(fac)
            self.wait_until = time.time() + self.aniprops.wait
             
        else:
            # sit and wait...
            self.done = self.wait_until < time.time()

    def drawWithFac(self, fac):
        #ref = self.pixels[0].refC()
        #draw.circle(self.screen, white, ref, max(1, int(80*self.steps[self.step])), 1)
        for p in self.pixels:
            out = p.out(fac)
            self.screen.set_at(out, white)
class Pix:
    def __init__(self, orgX, orgY, ref, debug):
        self.orgPos = Vector(orgX, orgY)
        self.ref = ref
        self.vec = self.orgPos - ref
        self.speedGrow = random.random()*0.5
        self.speedShrink = 0.2+random.random()*0.5
        self.debug = debug
        
    def debug(self, text):
        if(self.debug):
            print(text)
    
    def out(self, fac):
        if(fac >= 0):
            pos = self.orgPos + self.vec * fac * self.speedGrow
        else:
            pos = self.orgPos - self.vec * abs(fac) * self.speedShrink
        return (int(pos.x), int(pos.y))
    
    def refC(self):
        return (int(self.ref.x), int(self.ref.y))
    
    def __str__(self):
        deb = 'DEB' if self.debug else '-'
        return f"Vector(org={self.orgPos},ref={self.ref} vec={self.vec} {deb})"
    
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
        


    