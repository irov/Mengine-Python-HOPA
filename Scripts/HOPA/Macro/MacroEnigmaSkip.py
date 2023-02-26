from Foundation.SceneManager import SceneManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroEnigmaSkip(MacroCommand):
    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        source.addListener(Notificator.onEnigmaSkip, Filter=self.__onEnigmaSkip)
        pass

    def __onEnigmaSkip(self):
        if self.SceneName == SceneManager.getCurrentSceneName():
            return True

        return False