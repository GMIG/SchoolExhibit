import logging
import re
import traceback

from twisted.internet import reactor, defer
from twisted.protocols.basic import LineReceiver
from twisted.python.failure import Failure

from Codec import codec
from Device import Device
from TalkerListener import Announcer, compose, Talker
from twisted.internet.serialport import SerialPort

class ArduinoUniversal(LineReceiver, Device):
    def __init__(self, port: str):
        super().__init__()
        self.__port = port
        self.setLineMode()
        self.decoding_talker = compose(self.say_array, self.codec)
        self.add_listener("cmd", self.process_result)
        self.__current_command_id: int = 3
        self.__issued_command_storage = {}
        self.__commandRE = re.compile('\[(\S+)\]([^\t\n\r\f\v]*)')

    def __str__(self):
        return self.__class__.__name__ + "(" + self.__port + ")"

    def start(self):
        self.__serialPort = SerialPort(self, self.__port, reactor, baudrate=57600)


    def rawDataReceived(self, data):
        pass

    def lineReceived(self, data):
        try:
            string = codec(str(data, 'ascii'))
        except ValueError as err:
            logging.error(err, exc_info=True)
            return
        else:
            self.say_array(string)
            return

            #traceback.print_exc()

    def connectionMade(self):
        LineReceiver.connectionMade(self)

    def process_result(self, res: str):
        match = self.__commandRE.match(res)
        if len(match.group()) < 2:
            print("Processing error")
            return
        deferred = self.__issued_command_storage.get(match.group(1), defer.Deferred())
        if match.group(2) != "ok":
            deferred.errback(Exception(match.group(2)))
        else:
            deferred.callback(match.group(2))

    def exec_command(self, part_name: str, cmd_name: str, args) -> defer.Deferred:
        self.__current_command_id += 1
        if self.__current_command_id > 9999:
            self.__current_command_id = 3
        argument = ""
        if len(args):
            argument = args[0]
        try:
            string = "[" + str(self.__current_command_id) + "]" + part_name + "." + \
                     cmd_name + "(" + str(argument) + ")" + "\n"
            logging.debug("sending to arduino:" + string)
            self.transport.write(bytes(string, 'utf-8'))
        except AttributeError as err:
            logging.error(err, exc_info=True)
            return defer.fail(Exception("Attempting to write to uninitialized port"))
        deferred = defer.Deferred()
        deferred.addTimeout(2, reactor)
        self.__issued_command_storage[str(self.__current_command_id)] = deferred
        return deferred
"""
class ArduinoUniversal(LineReceiver, Talker):
    def __init__(self):
        super().__init__()
        #self.talker = Talker()
        self.setLineMode()
        self.decoding_talker = compose(self.talker.say_array, self.codec)
        self.add_listener("cmd", self.process_result)
        self.current_command_id: int = 3
        self.command_storage = {}
        self.commandRE = re.compile('\[(\S+)\]([^\t\n\r\f\v]*)')

    def start(self, port: str):
        SerialPort(self, port, reactor, baudrate=57600)

    @staticmethod
    def codec(phrase: str):
        array = phrase.split(':', 1)
        if len(array) < 2:
            raise ValueError("Decoding error. Could not split '" + phrase + "' with a ':' ")
        return array

    def rawDataReceived(self, data):
        pass

    def lineReceived(self, data):
        try:
            string = self.codec(str(data, 'utf-8'))
            self.say_array(string)
        except TypeError as err:
            print(err)

    def connectionMade(self):
        LineReceiver.connectionMade(self)

    def process_result(self, res: str):
        match = self.commandRE.match(res)
        if len(match.group()) < 2:
            print("Processing error")
            return
        deferred = self.command_storage.get(match.group(1), defer.Deferred())
        deferred.callback(match.group(2))

    def __getattr__(self, name):
        if name[0:3] == "on_":
            def method(*args):
                self.add_listener(name[3:], args[0])
            return method

        class Part:
            def __init__(self, _parent: LineReceiver):
                self.parent = _parent

            def __getattr__(self, name1):
                def method(*args) -> defer.Deferred:
                    print("tried to handle unknown method " + name1)
                    self.parent.current_command_id += 1
                    if self.parent.current_command_id > 9999:
                        self.parent.current_command_id = 3
                    if args:
                        print("it had arguments: " + str(args))
                        self.parent.transport.write(bytes("[" + str(self.parent.current_command_id) + "]" + name + "." + \
                                                          name1 + "(" + str(args[0]) + ")", 'ascii'))
                    deferred = defer.Deferred()
                    deferred.addTimeout(1, reactor)
                    self.parent.command_storage[str(self.parent.current_command_id)] = deferred
                    return deferred
                return method
        return Part(self)
"""
