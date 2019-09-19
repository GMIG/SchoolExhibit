import logging
import ctypes


import vlc
import pygame
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

from Scene import Scene
from TalkerListener import Talker
from VLCPlayer import VLCPlayer
from millis import millis
from vlc import EventType,EventManager
from ResourcesPaths import mediaPath

class VolumeNaidenov(Scene):

    def __init__(self):
        super().__init__()
        self.active = False
        self.sound = pygame.mixer.Sound(file = mediaPath + "ff.wav")
        reactor.callInThread(lambda : self.sound.play(loops = -1))
        self.decrease_volume_looper = LoopingCall(self.decrease_volume)
        self.lastT = 0
        self.lastVal = 0
        self.vol_threshold = 0.8
        self.step = 0.04

    def absolute_rotation(self, x: str, *args, **kwargs):
        if self.active:
            val = int(float(x)/900. * 100)
            if self.lastVal == 0 or self.lastT == 0:
                self.lastT = millis()
                self.lastVal = val
                return
            dt = millis() - self.lastT
            dVal = val - self.lastVal
            velocity = abs(dVal/dt)
            self.lastVal = val
            self.lastT = millis()
            logging.debug(velocity)
            vol = int(self.audio_player.media_player.audio_get_volume()) + 7
            reactor.callInThread(self.audio_player.setvolume, vol)
            if vol > self.vol_threshold:
                self.say("volume")
                
    def dynamic_rotation(self, x: str, *args, **kwargs):
        if self.active:
            vol = self.sound.get_volume() + self.step
            self.sound.set_volume(vol)
            #reactor.callInThread(self.audio_player.setvolume, vol)
            if vol > self.vol_threshold:
                self.say("volume")


    def decrease_volume(self, *args, **kwargs):
        vol = (self.sound.get_volume() - 0.0007)
        if vol <= 0:
            vol = 0
        self.sound.set_volume(vol)

    def activate(self, *args, **kwargs):
        if self.decrease_volume_looper.running:
            self.decrease_volume_looper.stop()
        self.decrease_volume_looper.start(0.01)
        self.say("activated")
        self.active = True

    def deactivate(self, fade=0.01, *args, **kwargs):
        self.decrease_volume_looper.stop()
        self.decrease_volume_looper.start(fade)
        self.say("deactivated")
        self.active = False


