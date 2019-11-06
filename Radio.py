
from Scene import Scene
import millis
from twisted.internet import reactor
import pygame
from ResourcesPaths import mediaPath
import logging
from twisted.internet.task import LoopingCall
import math
import random

from TalkerListener import Talker
import random
import time

class Freq(Talker):
    def __init__(self, freq:int, halfwidth:int, filename:str, endEventNum = 0):
        logging.debug(freq)
        self.freq = freq
        self.halfwidth = halfwidth
        self.sound = pygame.mixer.Sound(file = mediaPath + filename)
        self.channel = pygame.mixer.find_channel()
        if endEventNum == 0:
            self.channel.play(self.sound, loops=-1)
        else:
            self.channel.play(self.sound)
            self.channel.set_endevent(pygame.USEREVENT+1)
        self.channel.set_volume(0)

    def setFreq(self, curFreq:int):
        self.lastDelta = abs(self.freq - curFreq)
        vol = 1 - self.lastDelta/self.halfwidth
        if vol <= 0:
            vol = 0
        #logging.debug(vol)
        self.channel.set_volume(vol) 

class Radio(Scene):
    def __init__(self):
        super().__init__()
        self.active = True
        self.numNoiseFreqs = 5
        self.minfreq = 178
        self.maxfreq = 1020
        self.df = (self.maxfreq - self.minfreq)/(self.numNoiseFreqs + 1)
        self.frqValues = [self.minfreq + i*self.df for i in range(0,self.numNoiseFreqs + 1)]
        self.noiseFreqs = [Freq(self.minfreq + i*self.df, self.df, "f" + str(i+1) + ".wav") for i in range(0,self.numNoiseFreqs)]
        [frq.sound.set_volume(0.3) for frq in self.noiseFreqs]
        self.dosFreq = Freq(self.minfreq + self.numNoiseFreqs*self.df,150,"stalin2-short.wav", endEventNum = 1)
        self.beginTime = time.time()
        self.allFreqs = self.noiseFreqs.copy()
        self.allFreqs.append(self.dosFreq)
        self.initFrqs()
        self.eventThr = 120
        self.turnOffTime = 5
        
        def game_tick():
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.USEREVENT+1:
                    if self.active and self.dosFreq.lastDelta < self.eventThr and self.dosFreq.channel.get_volume() > 0.1 and time.time() - self.beginTime > 4:
                        self.say("death")
                        self.initFrqs()
                    self.dosFreq.channel.play(self.dosFreq.sound)
                    self.beginTime = time.time()

        self.tick = LoopingCall(game_tick)
        self.tick.start(0.2)
        self.stopper = reactor.callLater(self.turnOffTime, self.stop_radio)

        
    def stop_radio(self, *args, **kwargs):
        [freqobj.channel.set_volume(0) for freqobj in self.allFreqs]

        
    def initFrqs(self):
        frqsNum = len(self.allFreqs)
        lastDosFrq = self.dosFreq.freq
        rand = random.sample(range(0,frqsNum), frqsNum)
        while lastDosFrq == self.frqValues[rand[frqsNum - 1]] or rand[frqsNum - 1] == 0 or rand[frqsNum - 1] == frqsNum - 1:
            rand = random.sample(range(0,frqsNum), frqsNum)
        
        for i in range(0,frqsNum):
            f = self.allFreqs[i]
            f.freq = self.frqValues[rand[i]]
        
    def set_frequency(self, freq: str):
        if self.active:
            [freqobj.setFreq(int(freq)) for freqobj in self.allFreqs]

        if self.dosFreq.lastDelta > self.eventThr:
            if self.stopper.active():
                self.stopper.reset(self.turnOffTime)
            else:
                self.stopper = reactor.callLater(self.turnOffTime, self.stop_radio)
        elif self.stopper.active():
            self.stopper.cancel()

    def activate(self, *args, **kwargs):
        self.stop_radio()
        self.say("activated")
        self.active = True

    def deactivate(self, fade=0.01, *args, **kwargs):
        self.stop_radio()
        self.say("deactivated")
        self.active = False


        

class Radio1(Scene):
    def __init__(self):
        super().__init__()
        self.active = False
        self.numFrq = 5
        self.sound = pygame.mixer.Sound(file = mediaPath + "f1.wav")
        self.sound_dos = pygame.mixer.Sound(file = mediaPath + "stalin2-short.wav")
        def setChannel(num:int):
            sound = pygame.mixer.Sound(file = mediaPath + "f"+str(num) +".wav")
            channel = pygame.mixer.find_channel()
            return channel
        self.frqChannels = [setChannel(i) for i in range(1,self.numFrq)]
        self.channel_dos = pygame.mixer.find_channel()
        self.channel_dos.play(self.sound_dos)
        self.channel_dos.set_endevent(pygame.USEREVENT+1)
        self.sound.play(loops = -1)

        def game_tick():
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.USEREVENT+1:
                    if self.active and self.lastDelta < self.eventThreshold and self.channel_dos.get_volume() > 0.4:
                        self.say("death")
                        self.dosFreq = random.randint(300, 900)#self.frqs[random.randint(0, self.numFrq-1)]
                    self.channel_dos.play(self.sound_dos)
        self.tick = LoopingCall(game_tick)
        self.tick.start(0.2)
        self.lastTuneTime = 0
        self.gapThreshold = 0.8
        self.minfrq = 178
        self.maxfrq = 1020
        self.dFrq = self.maxfrq - self.minfrq
        self.frqs = list(range(self.minfrq,self.maxfrq,int(self.dFrq/self.numFrq)))
        logging.debug(self.frqs)
        self.dosFreq = self.frqs[random.randint(0, self.numFrq-1)]

        self.lastDelta = self.dosFreq
        self.threshold = 300
        self.eventThreshold = 150
        self.stop_radio()
        self.stopper = reactor.callLater(5, self.stop_radio)

    def stop_radio(self, *args, **kwargs):
        self.sound.set_volume(0)
        self.channel_dos.set_volume(0)
    
    def set_frequency(self, freqs: str):
        if self.active:
            freq = int(freqs)
            self.lastDelta = abs(self.dosFreq - freq)
            logging.debug("delta:" + str(self.lastDelta))
            if self.lastDelta < self.threshold:
                val = 1 - self.lastDelta/self.threshold
                logging.debug("val:" + str(val))
                self.channel_dos.set_volume(val)
                self.sound.set_volume(1.2 - val)#differ
            else:
                ind = self.dFrq/freq
                neardown = int(math.floor(ind))
                nearup = int(math.ceil(ind))
                #[self.frqs[i].set_volume(0) for i in range(neardown-1,0,-1)]
                #[self.frqs[i].set_volume(0) for i in range(nearup,self.numFrq,1)]
                #######frqChannels[neardown].set_volume(freq - self.frqs[neardown]
                self.frqs[nearup] - freq
                self.sound.set_volume(1)
                
        if self.lastDelta > self.eventThreshold:	
            if self.stopper.active():
                self.stopper.reset(5)
            else:
                self.stopper = reactor.callLater(5, self.stop_radio)
        elif self.stopper.active():
            self.stopper.cancel()
        
    def activate(self, *args, **kwargs):
        self.stop_radio()
        self.say("activated")
        self.active = True

    def deactivate(self, fade=0.01, *args, **kwargs):
        self.stop_radio()
        self.say("deactivated")
        self.active = False


