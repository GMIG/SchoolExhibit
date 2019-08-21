import cgi
import html
import logging
import sys
import time
import traceback

#import keyboard
import txaio
import vlc
from twisted.internet import reactor, tksupport, endpoints
from twisted.internet.task import LoopingCall
from twisted.web import resource, server
from twisted.web.server import Site
from twisted.web.static import File

from ArduinoUniversal import ArduinoUniversal
from MainScene import MainScene
from Ringer import Ringer
from ScreenGolubeva import ScreenGolubeva
from VLCPlayer import VLCPlayer
from VLCPlayerTK import BaseTkContainer, VLCPlayerTK

import tkinter as tk

from VolumeNaidenov import VolumeNaidenov
from millis import millis
from ResourcesPaths import sitePath



class Simple(File):
    pass

btn = False
if __name__ == '__main__':
    try:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        rootLog = logging.getLogger()
        hdlr = rootLog.handlers[0]
        fmt = logging.Formatter('[%(asctime)s.%(msecs)02d] (%(funcName)s) %(message)s', "%H:%M:%S")
        hdlr.setFormatter(fmt)

        factory = Site(Simple(sitePath))
        endpoint = endpoints.TCP4ServerEndpoint(reactor, 8080)
        endpoint.listen(factory)

        def begin(arduino: ArduinoUniversal):
            arduino.ang.alpha(0.9)
            arduino.rot.alpha(0.7)

            arduino.ang.stop()
            #arduino.rot.stop()
            root = BaseTkContainer()
            tksupport.install(root.tk_instance)
            vlc_instance: vlc.Instance = vlc.Instance()
            print(vlc_instance.audio_output_enumerate_devices())
            def switch(x):
                if x.name == 'space':
                    arduino.outs.on("grn")
                    arduino.outs.on("red")
            #keyboard.on_press(switch)

            main_scene = MainScene(root.tk_instance, "500x500+0+0", vlc_instance)

            vn = VolumeNaidenov()
            def volume_changed(*vargs, **kwargs):
                arduino.outs.on("grn")
                main_scene.start_video(2)
            vn.on_volume(volume_changed)
            arduino.on_rot(vn.dynamic_rotation)
            vn.activate()

            ringer = Ringer(vlc_instance)
            def ring_ended(*vargs, **kwargs):
                main_scene.start_video(1)
                arduino.outs.on("red")
            ringer.on_ring_end(ring_ended)
            arduino.on_but(ringer.button)
            ringer.activate()

            sg1 = ScreenGolubeva()
            def signed(*vargs, **kwargs):
                 main_scene.start_video(2)
                 arduino.outs.on("red")
            sg1.on_sign(signed)
            sg1.activate()

            def switch_all_off(*args, **kwargs):
                vn.deactivate()
                ringer.deactivate()
                sg1.deactivate()

            def switch_all_on(*args, **kwargs):
                vn.activate()
                ringer.activate()
                sg1.activate()
                arduino.outs.off("grn")
                arduino.outs.off("red")

            main_scene.on_started_video(switch_all_off)
            main_scene.on_started_titles(switch_all_on)

            # try:
            #     a = player.media_player.audio_output_device_enum()
            #     while a:
            #         print(str(a[0].device, 'utf-8'))
            #         print(str(a[0].description, 'utf-8'))
            #         a = a[0].next
            # except Exception as e:
            #     print(e)

            print(arduino)

        a = ArduinoUniversal("/dev/ttyACM0")
        def arduinoLoaded(x: str):
            if int(x) == 1:
                begin(a)
        a.on_sys(arduinoLoaded)
        a.addEmptyIfAbsent = True
        a.start()
        reactor.run()
    except Exception as e:
        traceback.print_exc()

