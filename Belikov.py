

import vlc

from Scene import Scene


class Belikov(Scene):

    def __init__(self):
        super().__init__()
        self.active = False

    def activate(self):
        self.active = True
        self.say("activated")

    def deactivate(self):
        self.active = False
        self.say("deactivated")

    def button(self, x):
        val = int(x)
        if self.active and val == 0:
             self.say("pushed")
