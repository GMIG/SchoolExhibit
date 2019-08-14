import abc
import functools
from functools import partial

from TalkerListener import Talker


class Scene(Talker):

    @abc.abstractmethod
    def activate(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def deactivate(self, *args, **kwargs):
        pass


