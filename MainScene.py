import threading

import vlc

from Scene import Scene
from TalkerListener import Talker
from VLCPlayer import VLCPlayer
from VLCPlayerTK import VLCPlayerTK


class MainScene(Talker):

    def __init__(self, tk_instance, geometry: str, vlc_instance):
        super().__init__()
        self.player = VLCPlayerTK(tk_instance, geometry, vlc_instance)

        self.player.media_player.audio_output_set(b'mmdevice')
        self.player.media_list_player.set_playback_mode(vlc.PlaybackMode.default)
        self.player.media_list.lock()
        self.player.media_list.add_media("D:\\SCEXIB\\01.mp4")
        self.player.media_list.add_media("D:\\SCEXIB\\00.mp4")
        self.player.media_list.add_media("D:\\SCEXIB\\2.mp4")
        self.player.media_list.add_media("D:\\SCEXIB\\3.mp4")
        self.player.media_list.add_media("D:\\SCEXIB\\4o.mp4")
        self.player.media_list.unlock()
        self.player.media_list_player.play_item_at_index(0)
        self.player.media_list_player.set_playback_mode(vlc.PlaybackMode.repeat)
        self.player.add_listener("end", self.__on_end)
        self.mainPlaying = True

    def start_video(self, num, *args, **kwargs):
        self.mainPlaying = False
        self.player.media_list_player.play_item_at_index(num)
        self.player.setbrightness(0)
        self.player.unfade(0.3)
        self.say("started_video", num)

    # For debug only
    def stop_video(self, *args, **kwargs):
        self.__on_end(*args, **kwargs)

    def __on_end(self, *args, **kwargs):
        if not self.mainPlaying:
            self.player.media_list_player.play_item_at_index(0)
            self.say("started_titles")
            self.mainPlaying = True


