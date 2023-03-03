from HOPA.Macro.MacroCommand import MacroCommand


class MacroLeave(MacroCommand):

    def _onValues(self, values):
        self.ObjectName = values[0]
        FinderType, self.Object = self.findObject(self.ObjectName)

        self.ObjectType = self.Object.getType() if self.Object is not None else None

        self.AutoEnable = bool(values[1]) if len(values) > 1 else True

        self.ObjectMovie2SocketName = str(values[2]) if self.ObjectType == "ObjectMovie2" and len(values) > 2 else "socket"

        self.CreateQuestOnRepeat = bool(values[3]) if len(values) > 3 else False

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if self.hasObject(self.Object.name) is False:
                self.initializeFailed("Object %s not found in group %s" % (self.Object.name, self.GroupName))

    def _onGenerate(self, source):
        isRepeat = self.isRepeatScenario()

        if isRepeat is False or self.CreateQuestOnRepeat is True:
            Quest = self.addQuest(source, "Leave", SceneName=self.SceneName, GroupName=self.GroupName,
                                  Object=self.Object)

            with Quest as tc_quest:
                tc_quest.addTask("AliasObjectLeave", SceneName=self.SceneName, Object=self.Object,
                                 AutoEnable=self.AutoEnable)
        else:
            source.addTask("AliasObjectLeave", SceneName=self.SceneName, Object=self.Object, AutoEnable=self.AutoEnable)
