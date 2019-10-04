import vlc

from Scene import Scene
from VLCPlayer import VLCPlayer
from ResourcesPaths import mediaPath


class Ringer(Scene):

    def __init__(self, instance = vlc.Instance()):
        super().__init__()
        self.audio_player = VLCPlayer(instance)
        self.audio_player.media_player.audio_output_set(b'sndio')
        self.audio_player.media_list_player.set_playback_mode(vlc.PlaybackMode.default)
        self.audio_player.media_list.add_media(mediaPath + "doorbell.mp3")
        self.audio_player.add_listener("stop", self.__stop_event)
        self.active = False
        self.was_pressed_during_active = False

    def __stop_event(self, *args, **kwargs):
        self.active = False
        self.say("ring_end")
        self.was_pressed_during_active = False

    def activate(self):
        self.active = True
        self.say("activated")

    def deactivate(self):
        if self.audio_player.media_list_player.is_playing():
            self.audio_player.media_list_player.stop()
        self.active = False
        self.say("deactivated")

    def button(self, x):
        val = int(x)
        if self.active:
            if val == 0:
                self.was_pressed_during_active = True
                self.audio_player.media_list_player.play_item_at_index(0)
            else:
                if self.was_pressed_during_active:
                    self.audio_player.media_list_player.stop()
