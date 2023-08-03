from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.EnigmaManager import EnigmaManager


class TaskEnigmaComplete(MixinObserver, Task):
    Skip = False

    def _onParams(self, params):
        super(TaskEnigmaComplete, self)._onParams(params)
        self.EnigmaName = params.get("EnigmaName")

    def _onInitialize(self):
        super(TaskEnigmaComplete, self)._onInitialize()

    def _onRun(self):
        EnigmaObject = EnigmaManager.getEnigmaObject(self.EnigmaName)

        if EnigmaObject.getComplete() is True:
            return True

        self.addObserverFilter(Notificator.onEnigmaComplete, self._onEnigmaComplete, EnigmaObject)

        return False

    def _onEnigmaComplete(self, Enigma):
        return True
