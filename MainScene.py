import threading

import vlc

from Scene import Scene
from TalkerListener import Talker
from VLCPlayer import VLCPlayer
from VLCPlayerTK import VLCPlayerTK
from ResourcesPaths import mediaPath

class MainScene(Talker):

    def __init__(self, tk_instance, geometry: str, vlc_instance):
        super().__init__()
        self.player = VLCPlayerTK(tk_instance, geometry, vlc_instance)
        self.default_track_num = 3
        self.player.media_player.audio_output_set(b'mmdevice')
        self.player.media_list.lock()
        self.player.media_list.add_media(mediaPath + "1.mp4")
        self.player.media_list.add_media(mediaPath + "2.mp4")
        self.player.media_list.add_media(mediaPath + "3.mp4")
        self.player.media_list.add_media(mediaPath + "4.mp4")
        self.player.media_list.add_media(mediaPath + "5.mp4")
        self.player.media_list.unlock()
        self.player.media_list_player.set_playback_mode(vlc.PlaybackMode.repeat)
        self.player.media_list_player.play_item_at_index(self.default_track_num)
        self.player.add_listener("end", self.__on_end)
        self.mainPlaying = True

    def start_video(self, num, *args, **kwargs):
        self.mainPlaying = False
        self.player.media_list_player.play_item_at_index(num)
        #self.player.setbrightness(0)
        #self.player.unfade(0.3)
        self.say("started_video", num)

    # For debug only
    def stop_video(self, *args, **kwargs):
        self.__on_end(*args, **kwargs)

    def __on_end(self, *args, **kwargs):
        if not self.mainPlaying:
            self.player.media_list_player.play_item_at_index(self.default_track_num)
            self.say("started_titles")
            self.mainPlaying = True
        else:
            self.say("restarted_titles")
                


