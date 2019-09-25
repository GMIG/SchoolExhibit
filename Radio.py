
from Scene import Scene
import millis
from twisted.internet import reactor
import pygame
from ResourcesPaths import mediaPath
import logging

class Radio(Scene):
    def __init__(self):
        super().__init__()
        self.active = False
        self.sound = pygame.mixer.Sound(file = mediaPath + "radio.wav")
        self.sound_dos = pygame.mixer.Sound(file = mediaPath + "dos.wav")
        reactor.callInThread(lambda : self.sound_dos.play(loops = -1))
        reactor.callInThread(lambda : self.sound.play(loops = -1))
        #self.decrease_volume_looper = LoopingCall(self.decrease_volume)
        self.lastTuneTime = 0
        self.gapThreshold = 0.8
        self.dosFreq = 300
        self.threshold = 200
        self.stop_radio()
        self.stopper = reactor.callLater(5, self.stop_radio)

    def stop_radio(self, *args, **kwargs):
        self.sound.set_volume(0)
        self.sound_dos.set_volume(0)
    
    def set_frequency(self, freqs: str):
        freq = int(freqs)
        delta = abs(self.dosFreq - freq)
        logging.debug("delta:" + str(delta))
        if delta < self.threshold:
            val = 1 - delta/self.threshold
            logging.debug("val:" + str(val))
            self.sound_dos.set_volume(val)
            self.sound.set_volume(1.2 - val)
        else:
            self.sound.set_volume(1)
            
        if self.stopper.active():
            self.stopper.reset(5)
        else:
            self.stopper = reactor.callLater(5, self.stop_radio)
        
    def activate(self, *args, **kwargs):
        self.stop_radio()
        self.say("activated")
        self.active = True

    def deactivate(self, fade=0.01, *args, **kwargs):
        self.stop_radio()
        self.say("deactivated")
        self.active = False


