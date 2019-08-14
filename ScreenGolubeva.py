import logging

from autobahn.twisted import WebSocketServerProtocol, WebSocketServerFactory
from twisted.internet import reactor, endpoints

from Codec import codec
from Scene import Scene

class MyServerProtocol(WebSocketServerProtocol):

    def __init__(self, screen):
        super().__init__()
        self.screen = screen

    def onConnect(self, response):
        super().onConnect(response)

    def onOpen(self):
        self.screen.protinst = self
        self.sendMessage(payload=b"sign.unblock()")

    def onMessage(self, payload, isBinary):
        logging.debug(payload)
        string = codec(str(payload, 'utf-8'))
        self.screen.say_array(string)

    def onClose(self, wasClean, code, reason):
        super().onClose(wasClean, code, reason)
        self.screen.protinst = None


class ToScreenFactory(WebSocketServerFactory):

    def buildProtocol(self, addr):
        protocol = MyServerProtocol(self.screen)
        protocol.factory = self
        return protocol

    def __init__(self, screen):
        super().__init__()
        self.screen = screen

class ScreenGolubeva(Scene):

    def activate(self, *args, **kwargs):
        if self.protinst is not None:
            self.protinst.sendMessage(payload=b"sign.unblock()")

    def deactivate(self, *args, **kwargs):
        if self.protinst is not None:
            self.protinst.sendMessage(payload=b"sign.block()")

    def __init__(self):
        super().__init__()
        self.active = False
        self.factoryws = ToScreenFactory(self)
        self.protinst = None
        endpoint = endpoints.TCP4ServerEndpoint(reactor, 8000)
        endpoint.listen(self.factoryws)
