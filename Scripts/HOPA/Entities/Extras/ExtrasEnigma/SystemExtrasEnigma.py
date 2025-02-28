from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from Notification import Notification


class SystemExtrasEnigma(System):
    def __init__(self):
        super(SystemExtrasEnigma, self).__init__()
        self.onExtraEnigmaPlayObserver = None
        pass

    def _onRun(self):
        self.onExtraEnigmaPlayObserver = Notification.addObserver(Notificator.onExtraEnigmaPlay, self._playExtraEnigma)
        return True
        pass

    def _onStop(self):
        Notification.removeObserver(self.onExtraEnigmaPlayObserver)
        self.onExtraEnigmaPlayObserver = None
        pass

    def _playExtraEnigma(self, enigmaName, sceneName):
        enigma = EnigmaManager.getEnigmaObject(enigmaName)
        enigmaType = enigma.getType()
        with TaskManager.createTaskChain() as tc:
            tc.addTask("AliasTransition", SceneName=sceneName)
            with tc.addRaceTask(2) as (tc1, tc2):
                tc1.addTask("AliasEnigmaPlay", EnigmaName=enigmaName)

                tc2.addTask("TaskButtonClick", GroupName="ExtraToolbar", ButtonName="Button_Menu")
                tc2.addParam(enigma, "Play", False)
                pass
            if enigmaType == "ObjectHOGRolling":
                tc.addTask("AliasTransition", SceneName="ExtrasHOG")
                pass
            else:
                tc.addTask("AliasTransition", SceneName="ExtrasPuzzle")
                pass
            pass
        return False
        pass

    pass
