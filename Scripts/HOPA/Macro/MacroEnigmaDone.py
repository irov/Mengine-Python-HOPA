from Foundation.SceneManager import SceneManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroEnigmaDone(MacroCommand):

    def _onGenerate(self, source):
        with source.addRaceTask(2) as (complete, skip):
            complete.addListener(Notificator.onEnigmaComplete, Filter=self.__enigmaFilter)
            skip.addListener(Notificator.onEnigmaSkip, Filter=self.__enigmaFilter)

    def __enigmaFilter(self, *args):
        if self.SceneName == SceneManager.getCurrentSceneName():
            return True
        return False
