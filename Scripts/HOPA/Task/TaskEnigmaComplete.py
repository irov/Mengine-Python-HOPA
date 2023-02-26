from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.EnigmaManager import EnigmaManager

class TaskEnigmaComplete(MixinObserver, Task):
    Skip = False

    def _onParams(self, params):
        super(TaskEnigmaComplete, self)._onParams(params)

        self.EnigmaName = params.get("EnigmaName")
        pass

    def _onInitialize(self):
        super(TaskEnigmaComplete, self)._onInitialize()
        pass

    def _onRun(self):
        EnigmaObject = EnigmaManager.getEnigmaObject(self.EnigmaName)

        self.addObserverFilter(Notificator.onEnigmaComplete, self._onEnigmaComplete, EnigmaObject)

        return False
        pass

    def _onEnigmaComplete(self, Enigma):
        return True
        pass
    pass