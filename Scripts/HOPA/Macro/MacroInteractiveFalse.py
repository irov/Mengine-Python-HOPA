from HOPA.Macro.MacroCommand import MacroCommand

class MacroInteractiveFalse(MacroCommand):
    def _onValues(self, values):
        self.ObjectName = values[0]
        self.ObjectTypeFilter = ["ObjectSocket", "ObjectZoom", "ObjectTransition", "ObjectItem"]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            FinderType, Object = self.findObject(self.ObjectName)

            if self.hasObject(Object.name) is False:
                self.initializeFailed("MacroInteractiveTrue not found Object %s in group %s" % (Object.name, self.GroupName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        FinderType, Object = self.findObject(self.ObjectName)
        ObjectType = Object.getType()

        if ObjectType not in self.ObjectTypeFilter:
            source.addTask("TaskInteractive", Object=Object, Value=False)
            return
            pass

        Quest = self.addQuest(source, "Enable", SceneName=self.SceneName, GroupName=self.GroupName, Object=Object)

        with Quest as tc_quest:
            tc_quest.addTask("TaskInteractive", Object=Object, Value=False)
            pass
        pass
    pass