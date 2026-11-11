from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.ScenarioManager import ScenarioManager

class SystemExtras(System):
    def __init__(self):
        super(SystemExtras, self).__init__()
        self._playTaskChains = []
        pass

    def _onRun(self):
        self.addObserver(Notificator.onExtraEnigmaPlay, self._playExtraEnigma)
        return True

    def _onStop(self):
        chains = self._playTaskChains
        self._playTaskChains = []
        for chain in chains:
            chain.cancel()

    def _playExtraEnigma(self, enigmaName, scenarioID):
        sceneName = EnigmaManager.getEnigmaSceneName(enigmaName)
        if scenarioID in ScenarioManager.s_scenarios.iterkeys():
            # finished chains are finalized, keep only the ones still running
            self._playTaskChains = [tc for tc in self._playTaskChains if tc.isInitialized() is True]

            chain = TaskManager.createTaskChain()
            self._playTaskChains.append(chain)
            with chain as tc:
                tc.addTask("AliasTransition", SceneName=sceneName)
                tc.addTask("TaskScenarioRun", ScenarioID=scenarioID)
                with tc.addRaceTask(2) as (tc_1, tc_2):
                    tc_1.addListener(Notificator.onEnigmaComplete)
                    tc_2.addTask("TaskButtonClick", GroupName="ExtraToolbar", ButtonName="Button_Menu")
                    tc_2.addNotify(Notificator.onEnigmaSkip)
                tc.addTask("TaskScenarioCancel", ScenarioID=scenarioID)
                tc.addTask("AliasTransition", SceneName="Extras")

        return False
