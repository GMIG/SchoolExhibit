import html
import logging
import sys
import time
import traceback

#import ctypes
#x11 = ctypes.cdll.LoadLibrary("libX11.so")
#x11.XInitThreads()

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
import ctypes
import tkinter as tk

from VolumeNaidenov import VolumeNaidenov
from Belikov import Belikov

from millis import millis
from ResourcesPaths import sitePath



class Simple(File):
    pass

btn = False
if __name__ == '__main__':
    try:
        #x11 = ctypes.cdll.LoadLibrary("libX11.so.6")
        #x11.XInitThreads()

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
            arduino.rot.alpha(0.2)

            #arduino.ang.stop()
            #arduino.rot.stop()
            root = BaseTkContainer()
            tksupport.install(root.tk_instance)
            vlc_instance: vlc.Instance = vlc.Instance("--no-xlib")
            print(vlc_instance.audio_output_enumerate_devices())
            def switch(x):
                if x.name == 'space':
                    arduino.outs.on("grn")
                    arduino.outs.on("red")

            main_scene = MainScene(root.tk_instance, "500x500+960+0", vlc_instance)            
            
            def transition(led: str,videoNum:int,*vargs, **kwargs):
                arduino.outs.on(led)
                main_scene.start_video(videoNum)
            
            naidenov = VolumeNaidenov()
            def volume_changed(*vargs, **kwargs):
                arduino.outs.on("grn")
                main_scene.start_video(2)
            naidenov.on_volume(volume_changed)
            arduino.on_enc(naidenov.dynamic_rotation)

            ringer = Ringer(vlc_instance)
            def ring_ended(*vargs, **kwargs):
                main_scene.start_video(1)
                arduino.outs.on("red")
            ringer.on_ring_end(ring_ended)
            arduino.on_but(ringer.button)

            golubeva = ScreenGolubeva()
            def signed(*vargs, **kwargs):
                 main_scene.start_video(4)
                 arduino.outs.on("red")
            golubeva.on_sign(signed)
            
            belikov = Belikov()
            def pushed(*vargs, **kwargs):
                 main_scene.start_video(5)
                 arduino.outs.on("red")
            belikov.on_pushed(pushed)
            arduino.on_but4(belikov.button)
            
            scenes = [naidenov,ringer,golubeva,belikov]
            
            [scene.activate() for scene in scenes] 

            def switch_all_off(*args, **kwargs):
                [scene.deactivate() for scene in scenes]

            def switch_all_on(*args, **kwargs):
                [scene.activate() for scene in scenes]                
                arduino.outs.allOff()

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
        reactor.callLater(2, begin, a)
        #a.on_sys(arduinoLoaded)
        a.addEmptyIfAbsent = True
        a.start()
        reactor.run()
    except Exception as e:
        traceback.print_exc()

