from Foundation.DemonManager import DemonManager
from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.TutorialManager import TutorialManager


class MacroPlaceRespectSlot(MacroCommand):
    def _onValues(self, values):
        self.ItemName = values[1]
        self.ObjectName = values[0]
        pass

    def _onInitialize(self, **params):
        if _DEVELOPMENT is True:
            if TutorialManager.hasEntry(self.ObjectName) is False:
                self.initializeFailed("MacroPlaceRespectSlot: self.ItemName is None or self.ObjectName is None")
        pass

    def _onGenerate(self, source):
        DemonObject = DemonManager.getDemon("Tutorial")
        DemonEn = DemonObject.getEntity()
        Object = DemonEn.getMovieObject(self.ObjectName)
        source.addTask("TaskPlaceRespectSlot", Object=Object, Item=self.ItemName)
        pass
