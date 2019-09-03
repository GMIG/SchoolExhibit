import logging
import ctypes


import vlc
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
        self.audio_player = VLCPlayer(vlc.Instance("--no-xlib"))
        
        self.audio_player.media_player.audio_output_set(b'alsa')
        self.audio_player.media_list_player.set_playback_mode(vlc.PlaybackMode.loop)
        self.audio_player.play_file(mediaPath + "ff.mp3")
        self.lastT = 0
        self.lastVal = 0
        self.decrease_volume_looper = LoopingCall(self.decrease_volume)
        self.audio_player.media_player.audio_set_volume(0)
        self.vol_threshold = 80
        self.step = 3

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
            vol = int(self.audio_player.media_player.audio_get_volume()) + self.step
            reactor.callInThread(self.audio_player.setvolume, vol)
            if vol > self.vol_threshold:
                self.say("volume")


    def decrease_volume(self, *args, **kwargs):
        vol = self.audio_player.media_player.audio_get_volume() - 1
        if vol <= 0:
            vol = 0
        reactor.callInThread(self.audio_player.media_player.audio_set_volume, vol)

    def activate(self, *args, **kwargs):
        if self.decrease_volume_looper.running:
            self.decrease_volume_looper.stop()
        self.decrease_volume_looper.start(0.05)
        self.say("activated")
        self.active = True

    def deactivate(self, fade=0.05, *args, **kwargs):
        self.decrease_volume_looper.stop()
        self.decrease_volume_looper.start(fade)
        self.say("deactivated")
        self.active = False


