from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.ScenarioManager import ScenarioManager
from Notification import Notification

class SystemExtras(System):
    def __init__(self):
        super(SystemExtras, self).__init__()
        pass

    def _onRun(self):
        self.onExtraEnigmaPlayObserver = Notification.addObserver(Notificator.onExtraEnigmaPlay, self._playExtraEnigma)
        pass

    def _onStop(self):
        pass

    def _playExtraEnigma(self, enigmaName, scenarioID):
        sceneName = EnigmaManager.getEnigmaSceneName(enigmaName)
        if scenarioID in ScenarioManager.s_scenarios.iterkeys():
            with TaskManager.createTaskChain() as tc:
                tc.addTask("AliasTransition", SceneName=sceneName)
                tc.addTask("TaskScenarioRun", ScenarioID=scenarioID)
                with tc.addRaceTask(2) as (tc_1, tc_2):
                    tc_1.addTask("TaskListener", ID=Notificator.onEnigmaComplete)
                    tc_2.addTask("TaskButtonClick", GroupName="ExtraToolbar", ButtonName="Button_Menu")
                    tc_2.addTask("TaskNotify", ID=Notificator.onEnigmaSkip)
                    pass
                tc.addTask("TaskScenarioCancel", ScenarioID=scenarioID)
                tc.addTask("AliasTransition", SceneName="Extras")
                pass
            pass
        pass

        return False
        pass

    pass