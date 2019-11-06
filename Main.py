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
import os
import tkinter as tk
import Scene
from typing import Callable

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
            #arduino.rad.stop()   
            root = BaseTkContainer()
            tksupport.install(root.tk_instance)
            vlc_instance: vlc.Instance = vlc.Instance()
            print(vlc_instance.audio_output_enumerate_devices())
            
            main_scene = MainScene(root.tk_instance, "1920x1080+0+0", vlc_instance)
            #main_scene = MainScene(root.tk_instance, "500x509+0+0", vlc_instance)
            arduino.outs.allOff()
            arduino.outs.allFad(5)
            
            step = 0.02
            def fade(dt:int,from_b:float,to_b:float):
                current_brightness = from_b
                brightness_k = (to_b - from_b)/dt
                def setLedBrightness():
                     nonlocal current_brightness, brightness_k
                     current_brightness += step*brightness_k
                     if( current_brightness < to_b + step) and (current_brightness > to_b - step ):
                         current_brightness = to_b
                         fade_looper.stop()
                     arduino.outs.allSet(int(round(current_brightness*255)))
                fade_looper = LoopingCall(setLedBrightness)
                fade_looper.start(step)
            #fade(1,0,1)
                
            def transition_to_main(num:int, led_name:str, from_scene: Scene, *vargs, **kwargs):
                main_scene.start_video(num)
                #[scene.activate() for scene in scenes]                
                #from_scene.deactivate()
                arduino.outs.allFad(0)
                arduino.outs.allOff()
                arduino.outs.setFad(led_name+",7")                
                #arduino.outs.on(led_name)
                
            def to_main(num:int, led_name:str, from_scene: Scene, *vargs, **kwargs) -> Callable:
                return partial(transition_to_main,num,led_name, from_scene, *vargs, **kwargs)
                        
            def setupTrigger(name:str,num:int,led_name:str,on_what:str = "event"):
                trg = Trigger(name,arduino)
                trg.add_listener(on_what,to_main(num,led_name, trg))
                return trg
                        
            scenes = []
            
            scenes.append(setupTrigger("shl",1,"shl"))           
            scenes.append(setupTrigger("vkl",2,"vkl"))
            scenes.append(setupTrigger("bor",3,"bo"))
            scenes.append(setupTrigger("alb",4,"alb","1"))
            scenes.append(setupTrigger("bin",5,"bin"))
            
            naidenov = VolumeNaidenov()
            naidenov.on_volume(to_main(6,"vol",naidenov))
            arduino.on_vol(naidenov.dynamic_rotation)
            scenes.append(naidenov)

            ringer = Ringer()
            ringer.on_ring_end(to_main(7,"rin",ringer))
            arduino.on_rin(ringer.button)
            scenes.append(ringer)

            scenes.append(setupTrigger("box",8,"box","1"))
            
            radio = Radio()
            arduino.on_rad(radio.set_frequency)
            radio.on_death(to_main(9,"rad",radio))
            scenes.append(radio)

            scenes.append(setupTrigger("tel",10,"tel","1"))
            scenes.append(setupTrigger("fot",11,"fot","0"))
            scenes.append(setupTrigger("kom",12,"kom"))
            scenes.append(setupTrigger("lif",13,"lif","1"))
            scenes.append(setupTrigger("fan",14,"fan","1"))
            
            golubeva = ScreenGolubeva()
            golubeva.on_sign(to_main(15,"sig",golubeva))
            scenes.append(golubeva)
            
            [scene.activate() for scene in scenes] 
            def switch_all_off(*args, **kwargs):
                [scene.deactivate() for scene in scenes]

            def switch_all_on(*args, **kwargs):
                [scene.activate() for scene in scenes]                
                arduino.outs.allFad(5)
                
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
        def on_press1(key):
            if key == keyboard.Key.f2:
                os._exit(1)
        listener1 = keyboard.Listener(on_press=on_press1)
        listener1.start()

        arduino = ArduinoUniversal("/dev/ttyACM0")
        def arduinoLoaded(x: str):
            if int(x) == 1:
                begin(a)
        reactor.callLater(7, begin, arduino)
        #a.on_sys(arduinoLoaded)
        arduino.addEmptyIfAbsent = True
        arduino.start()
        reactor.run()
    except Exception as e:
        traceback.print_exc()

