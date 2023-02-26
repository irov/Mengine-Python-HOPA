from HOPA.EnigmaManager import EnigmaManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroEnigmaComplete(MacroCommand):
    def _onValues(self, values):
        self.EnigmaName = values[0]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if EnigmaManager.hasEnigma(self.EnigmaName) is False:
                self.initializeFailed("Enigma %s not found!!!!!!!!" % (self.EnigmaName))
                pass
        pass

    def _onGenerate(self, source):
        Enigma = EnigmaManager.getEnigmaObject(self.EnigmaName)
        # source.addTask("TaskNotify", ID = Notificator.onEnigmaComplete, Args = (Enigma, ))
        # source.addTask("TaskFunction", Fn = Enigma.setPlay, Args = (False, ))

        def _complete(enigmaObject):
            enigmaEntity = enigmaObject.getEntity()
            enigmaEntity.enigmaComplete()

        source.addFunction(_complete, Enigma)
        pass
    pass