from HOPA.Macro.MacroCommand import MacroCommand


class MacroTalk(MacroCommand):
    def __init__(self):
        super(MacroTalk, self).__init__()

        self.Socket = None
        pass

    def _onValues(self, values):
        self.SocketName = values[0]
        pass

    def _onInitialize(self):
        FinderType, self.Socket = self.findObject(self.SocketName)
        self.ObjectType = self.Socket.getType()
        pass

    def _onGenerate(self, source):
        Quest = self.addQuest(source, "Talk", SceneName=self.SceneName, GroupName=self.GroupName, Object=self.Socket)

        with Quest as tc_quest:
            if self.ObjectType == "ObjectSocket":
                tc_quest.addTask("TaskSocketClick", SocketName=self.SocketName)
                pass
            elif self.ObjectType == "ObjectInteraction":
                tc_quest.addTask("TaskInteraction", InteractionName=self.SocketName)
                pass
            pass
        pass

    pass
