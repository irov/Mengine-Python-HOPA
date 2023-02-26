from Foundation.GroupManager import GroupManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroOpenExtra(MacroCommand):
    def _onValues(self, values):
        self.extraName = values[0]
        pass

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        Extras = GroupManager.getGroup("Extras")
        Demon_Extras = Extras.getObject("Demon_Extras")
        source.addTask("TaskAppendParam", Object=Demon_Extras, Param="OpenedExtraNames", Value=self.extraName)
        pass
    pass