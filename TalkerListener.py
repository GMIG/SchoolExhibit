"""Talker Listener mechanism

This script consists of vasic building blocks of Talker-lIstener mechanism
which is a modified Observer pattern
"""
import functools
import logging
import typing
from types import MappingProxyType
from typing import Callable, List, NoReturn, Mapping, FrozenSet, Any, TypeVar

Listener = Callable

def compose(*functions: Callable):
    E = TypeVar('E')

    def compose2(f: Callable[[Any], E], g: Callable[[E], Any]):
        return lambda x: f(g(x))
    return functools.reduce(compose2, functions, lambda x: x)

class Announcer(object):
    def __init__(self, listeners: typing.Set[Listener] = None):
        if listeners is None:
            self.__listeners = set()
        else:
            self.__listeners = listeners

    def add_listener(self, listener: Listener) -> NoReturn:
        self.__listeners.add(listener)

    def announce(self, phrase: str) -> NoReturn:
        for n in self.__listeners:
            try:
                n(phrase)
            except Exception as e:
                n(e)

    def get_listeners(self) -> FrozenSet[Listener]:
        return frozenset(self.__listeners)


class Talker(object):
    def __init__(self, listeners: typing.Dict[str, Listener] = None, eavesdrop: typing.Set[Listener] = None):
        if listeners is None:
            self.__listeners = {}
        else:
            self.__listeners = listeners

        if eavesdrop is None:
            self.__eavesdrop = set()
        else:
            self.__eavesdrop = eavesdrop
        self.addEmptyIfAbsent = False

    def say(self, listener_name: str, *args, **kwargs) -> NoReturn:
        [val(listener_name + ":" + str(args) + str(kwargs)) for val in self.__eavesdrop]
        logging.debug("on " + self.__class__.__name__ + "." + str(listener_name) + ":" + str(args).strip("(,)") + str(kwargs).strip("{}"))
        if listener_name not in self.__listeners:
            if self.addEmptyIfAbsent:
                self.add_listener(listener_name, lambda x: "")
        else:
            try:
                self.__listeners[listener_name](*args, **kwargs)
            except Exception as e:
                logging.debug(e)

    def say_array(self, array_phrase: List[str]) -> NoReturn:
        if len(array_phrase) < 2:
            raise ValueError("Array phrase error:" + str(array_phrase))
        else:
            self.say(array_phrase[0], array_phrase[1])

    def add_listener(self, listener_name: str, listener: Listener) -> NoReturn:
        self.__listeners[listener_name] = listener

    def add_eavesdrop(self, listener: Listener) -> NoReturn:
        self.__eavesdrop.add(listener)

    def remove_listener(self, listener_name: str) -> NoReturn:
        self.__listeners.pop(listener_name)

    def get_listeners(self) -> Mapping[str, Listener]:
        return MappingProxyType(self.__listeners)

    # if on_NAME(Listener) is accessed, under NAME listener is added
    def __getattr__(self, name: str):
        if name[0:3] == "on_":
            def listener_name(listener: Listener) -> NoReturn:
                self.add_listener(name[3:], listener)
            return listener_name
        else:
            raise AttributeError("Attribute not found: " + name)

"""
class ExternalProducer(LineReceiver, Producer):
    def __init__(self):
        super().__init__()
        self.setLineMode()

    def rawDataReceived(self, data):
        pass

    def lineReceived(self, data):
        self.produce(str(data, 'utf-8'))

    def connectionMade(self):
        LineReceiver.connectionMade(self)


class NamedPrinter(Callable):
    def __init__(self, name: str):
        self.name = name

    def __call__(self, arg: str) -> str:
        print(self.name + ':' + arg)
        return ''
"""
