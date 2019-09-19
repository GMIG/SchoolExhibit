


class Radio(Scene):

    def __init__(self):
        super().__init__()
        self.active = False
        self.sound = pygame.mixer.Sound(file = mediaPath + "ff.wav")
        reactor.callInThread(lambda : self.sound.play(loops = -1))
        self.decrease_volume_looper = LoopingCall(self.decrease_volume)
        self.lastT = 0
        self.lastVal = 0
        self.vol_threshold = 0.8
        self.step = 0.04
