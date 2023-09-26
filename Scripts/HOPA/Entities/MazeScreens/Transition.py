from Foundation.Initializer import Initializer
from Foundation.TaskManager import TaskManager


class Transition(Initializer):

    def __init__(self):
        super(Transition, self).__init__()
        self.params = None
        self.__owner = None

    def _onInitialize(self, *args, **kwds):
        pass

    def _onFinalize(self):
        self.onDeactivate()

    def onActivate(self):
        pass

    def runTaskChain(self):
        pass

    def onDeactivate(self):
        pass
