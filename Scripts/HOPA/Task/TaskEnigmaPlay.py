from Foundation.Task.Task import Task

from HOPA.EnigmaManager import EnigmaManager


class TaskEnigmaPlay(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskEnigmaPlay, self)._onParams(params)

        self.EnigmaName = params.get("EnigmaName")
        self.EnigmaParams = params.get("EnigmaParams")
        pass

    def _onRun(self):
        EnigmaObject = EnigmaManager.getEnigmaObject(self.EnigmaName)
        EnigmaObject.setEnigmaName(self.EnigmaName)
        EnigmaObject.setEnigmaParams(self.EnigmaParams)
        EnigmaObject.setPlay(True)

        return True
        pass

    pass
