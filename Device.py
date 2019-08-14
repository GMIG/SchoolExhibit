import abc
import logging
from typing import Callable

from twisted.internet import defer
from TalkerListener import Talker


Command = Callable[[str], defer.Deferred]

class Commandable:
    def __init__(self, _parent, _name):
        self.parent = _parent
        self.name = _name

    def __getattr__(self, cmd_name: str, *args):
        def command(*args1) -> defer.Deferred:
            logging.debug("command issued:" + str(self.parent) + "." + self.name + "." + cmd_name + str(args1))
            a = self.parent.exec_command(self.name, cmd_name, args1)
            return a
        return command


class Device(Talker):

    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def exec_command(self, part_name: str, cmd_name: str, args) -> defer.Deferred:
        pass

    def __getattr__(self, name: str):
        try:
            return super().__getattr__(name)
        except AttributeError:
            part = Commandable(self, name)
            self.__setattr__(name, part)
            return part

