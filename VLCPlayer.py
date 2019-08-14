import logging
import time

from twisted.internet import reactor
from twisted.internet.task import LoopingCall

from TalkerListener import Talker
from vlc import MediaPlayer, MediaListPlayer, MediaList, Media, PlaybackMode, EventType, VideoAdjustOption


class VLCPlayer(Talker):

    def __init__(self, vlc_instance):
        Talker.__init__(self)
        self.vlc_instance = vlc_instance
        self.media_player: MediaPlayer = MediaPlayer(self.vlc_instance)
        self.media_list_player: MediaListPlayer = MediaListPlayer(self.vlc_instance)
        self.media_list_player.set_media_player(self.media_player)
        self.media_list: MediaList = MediaList(self.vlc_instance)
        self.media_list_player.set_media_list(self.media_list)

        self.vlc_events = self.media_player.event_manager()
        self.vlc_events.event_attach(EventType.MediaPlayerEndReached, self.__on_end_event)
        self.vlc_events.event_attach(EventType.MediaPlayerStopped, self.__on_stop_event)
        self.vlc_events.event_attach(EventType.MediaPlayerPlaying,  self.__on_play_event)

    def play_file(self, path: str):
        self.media_list_player.set_playback_mode(PlaybackMode.default)
        self.media_list.lock()
        for i in range(0, self.media_list.count() - 1):
            media: Media = self.media_list.item_at_index(i)
            self.media_list.remove_index(i)
            media.release()
        media: Media = Media(self.vlc_instance, path)
        self.media_list.add_media(media)
        self.media_list.unlock()
        self.media_list_player.play_item_at_index(0)

    def fade(self, dt: float):
        delta_brightness = 0.05

        def decrease_and_set():
            current = self.media_player.video_get_adjust_float(VideoAdjustOption.Brightness)
            self.setbrightness(current - delta_brightness)
            curmillis = int(round(time.time() * 1000))
            if current <= 0 or (curmillis - startmillis) > dt*1000:
                self.setbrightness(0)
                lc.stop()
        startmillis = int(round(time.time() * 1000))
        brightness = self.media_player.video_get_adjust_float(VideoAdjustOption.Brightness)
        if brightness <= 0:
            return
        lc = LoopingCall(decrease_and_set)
        cur = dt/(brightness/delta_brightness)
        lc.start(cur)

    def unfade(self, dt: float):
        delta_brightness = 0.1

        def decrease_and_set():
            current = self.media_player.video_get_adjust_float(VideoAdjustOption.Brightness)
            self.setbrightness(current + delta_brightness)
            curmillis = int(round(time.time() * 1000))
            if current >= 1 or (curmillis - startmillis) > dt*1000:
                self.setbrightness(1)
                lc.stop()
        startmillis = int(round(time.time() * 1000))
        brightness = self.media_player.video_get_adjust_float(VideoAdjustOption.Brightness)
        if brightness >= 1:
            return
        lc = LoopingCall(decrease_and_set)
        cur = dt/((1 - brightness)/delta_brightness)
        lc.start(cur)

    def __on_stop_event(self, *args, **kwargs):
        reactor.callFromThread(self.say, "stop")

    def __on_end_event(self, *args, **kwargs):
        reactor.callFromThread(self.say, "end")

    def __on_play_event(self, *args, **kwargs):
        reactor.callFromThread(self.say, "play")

    def setbrightness(self, val: float):
        self.media_player.video_set_adjust_int(VideoAdjustOption.Enable, 1)
        self.media_player.video_set_adjust_float(VideoAdjustOption.Brightness, val)

    def setvolume(self, val: int):
        self.media_player.audio_set_volume(val)
