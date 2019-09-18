

from Scene import Scene
import ArduinoUniversal

class Trigger(Scene):

    def __init__(self,name:str, arduino: ArduinoUniversal):
        super().__init__()
        self.active = False
        arduino.add_listener(name,self.sense_listener)
    
    def sense_listener(self, x: str):
        val:int = int(x)
        if self.active:
            self.say("event", val)
            self.say(x)
    
    def activate(self):
        self.active = True
        self.say("activated")

    def deactivate(self):
        self.active = False
        self.say("deactivated")
