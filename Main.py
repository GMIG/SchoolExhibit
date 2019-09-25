import html
import logging
import sys
import time
import traceback

#import ctypes
#x11 = ctypes.cdll.LoadLibrary("libX11.so")
#x11.XInitThreads()

from pynput import keyboard
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
from Radio import Radio

from millis import millis
from ResourcesPaths import sitePath
import pygame
from Trigger import Trigger
from functools import partial

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
        pygame.init()
        pygame.mixer.init()

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

            main_scene = MainScene(root.tk_instance, "500x500+0+0", vlc_instance)
            
            def transition_to_main(num:int, ledName:str, *vargs, **kwargs):
                main_scene.start_video(num)
                arduino.outs.on(ledName)
                        
            def setupTrigger(name:str,num:int,led_name:str):
                trg = Trigger(name,arduino)
                trg.on_event(partial(transition_to_main,num,led_name))
                return trg
                        
            scenes = []
            scenes.append(setupTrigger("shl",1,"shl"))
            scenes.append(setupTrigger("vkl",2,"vkl"))
            scenes.append(setupTrigger("bor",3,"bo"))
            scenes.append(setupTrigger("alb",4,"alb"))
            scenes.append(setupTrigger("bin",5,"bin"))
            
            naidenov = VolumeNaidenov()
            naidenov.on_volume(partial(transition_to_main,6,"vol"))
            arduino.on_vol(naidenov.dynamic_rotation)
            scenes.append(naidenov)

            ringer = Ringer()
            ringer.on_ring_end(partial(transition_to_main,7,"rin"))
            arduino.on_rin(ringer.button)
            scenes.append(ringer)

            scenes.append(setupTrigger("box",8,"box"))
            radio = Radio()
            arduino.on_rad(radio.set_frequency)
            radio.activate()
            #9 - mazus
            scenes.append(setupTrigger("tel",10,"tel"))
            scenes.append(setupTrigger("fot",11,"fot"))
            scenes.append(setupTrigger("kom",12,"kom"))
            scenes.append(setupTrigger("lif",13,"lif"))
            scenes.append(setupTrigger("fan",14,"fan"))
            
            golubeva = ScreenGolubeva()
            golubeva.on_sign(partial(transition_to_main,15,"sig"))
            scenes.append(golubeva)
            
            [scene.activate() for scene in scenes] 
            def switch_all_off(*args, **kwargs):
                [scene.deactivate() for scene in scenes]

            def switch_all_on(*args, **kwargs):
                [scene.activate() for scene in scenes]                
                arduino.outs.allOff()
                
            main_scene.on_started_video(switch_all_off)
            main_scene.on_started_titles(switch_all_on)
            
            def on_press(key):
                if key == keyboard.Key.space:
                    main_scene.stop_video()
            listener = keyboard.Listener(on_press=on_press)
            listener.start()

            # try:
            #     a = player.media_player.audio_output_device_enum()
            #     while a:
            #         print(str(a[0].device, 'utf-8'))
            #         print(str(a[0].description, 'utf-8'))
            #         a = a[0].next
            # except Exception as e:
            #     print(e)

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

