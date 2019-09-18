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

from Trigger import Trigger

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
            #arduino.ang.alpha(0.9)
            #arduino.rot.alpha(0.2)

            #arduino.ang.stop()
            #arduino.rot.stop()
            root = BaseTkContainer()
            tksupport.install(root.tk_instance)
            vlc_instance: vlc.Instance = vlc.Instance()
            print(vlc_instance.audio_output_enumerate_devices())
            def switch(x):
                if x.name == 'space':
                    arduino.outs.on("grn")
                    arduino.outs.on("red")

            main_scene = MainScene(root.tk_instance, "1500x1080+0+0", vlc_instance)            
            
            def transition(led: str,videoNum:int,*vargs, **kwargs):
                arduino.outs.on(led)
                main_scene.start_video(videoNum)
            
            def setupTrigger(name:str, num:int):
                trg = Trigger(name,arduino)
                def f(*vargs, **kwargs):
                    main_scene.start_video(num)
                trg.on_event(f)
                return trg
            """
            shelTrig = Trigger("shl",arduino)
            def shel(*vargs, **kwargs):
                main_scene.start_video(0)
            shelTrig.on_event(shel)
            
            lightTrig = Trigger("vkl",arduino)
            def vkl(*vargs, **kwargs):
                main_scene.start_video(1)
            lightTrig.on_event(vkl)
"""
            """
            naidenov = VolumeNaidenov()
            def volume_changed(*vargs, **kwargs):
                arduino.outs.on("grn")
                main_scene.start_video(5)
            naidenov.on_volume(volume_changed)
            arduino.on_vol(naidenov.dynamic_rotation)
"""
            ringer = Ringer()
            def ring_ended(*vargs, **kwargs):
                main_scene.start_video(6)
                arduino.outs.on("red")
            ringer.on_ring_end(ring_ended)
            arduino.on_rin(ringer.button)

            golubeva = ScreenGolubeva()
            def signed(*vargs, **kwargs):
                 main_scene.start_video(14)
                 arduino.outs.on("red")
            golubeva.on_sign(signed)
            
            belikov = Belikov()
            def pushed(*vargs, **kwargs):
                 main_scene.start_video(1)
                 arduino.outs.on("red")
            belikov.on_pushed(pushed)
            arduino.on_lif(belikov.button)
            
            scenes = [ringer,golubeva,belikov]
            scenes.append(setupTrigger("shl",0))
            scenes.append(setupTrigger("vkl",1))
            scenes.append(setupTrigger("bor",2))
            scenes.append(setupTrigger("alb",3))
            scenes.append(setupTrigger("bin",4))
            scenes.append(setupTrigger("box",7))
            scenes.append(setupTrigger("rad",8))
            scenes.append(setupTrigger("tel",9))
            scenes.append(setupTrigger("fot",10))
            scenes.append(setupTrigger("kom",11))
            scenes.append(setupTrigger("lif",12))

            
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

        arduino = ArduinoUniversal("/dev/ttyACM0")
        def arduinoLoaded(x: str):
            if int(x) == 1:
                begin(a)
        reactor.callLater(4, begin, arduino)
        #a.on_sys(arduinoLoaded)
        arduino.addEmptyIfAbsent = True
        arduino.start()
        reactor.run()
    except Exception as e:
        traceback.print_exc()

