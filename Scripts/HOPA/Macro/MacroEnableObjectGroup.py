from Foundation.GroupManager import GroupManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroEnableObjectGroup(MacroCommand):
    def _onValues(self, values):
        self.GroupObjectName = values[0]
        self.ObjectName = values[1]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if GroupManager.hasObject(self.GroupObjectName, self.ObjectName) is False:
                self.initializeFailed("MacroEnableObjectGroup not found Object %s in group %s" % (self.ObjectName, self.GroupObjectName))

    def _onGenerate(self, source):
        Object = GroupManager.getObject(self.GroupObjectName, self.ObjectName)

        source.addEnable(Object)
