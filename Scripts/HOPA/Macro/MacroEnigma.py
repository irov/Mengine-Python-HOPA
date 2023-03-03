from HOPA.EnigmaManager import EnigmaManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroEnigma(MacroCommand):
    def _onValues(self, values):
        self.EnigmaName = values[0]

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if EnigmaManager.hasEnigma(self.EnigmaName) is False:
                self.initializeFailed("Enigma %s not found!!!!!!!!" % self.EnigmaName)

    def _onGenerate(self, source):
        Quest = self.addQuest(source, "Enigma", SceneName=self.SceneName, GroupName=self.GroupName,
                              EnigmaName=self.EnigmaName)

        with Quest as tc_quest:
            tc_quest.addTask("AliasEnigmaPlay", EnigmaName=self.EnigmaName)
