from HOPA.Macro.MacroCommand import MacroCommand

class MacroItemCollect(MacroCommand):
    def _onValues(self, values):
        self.SocketName = values[0]
        self.ItemsList = values[1:]

    def _onInitialize(self):
        FinderType, self.Socket = self.findObject(self.SocketName)
        pass

    def __filter(self, socket, items_list):
        if socket == self.Socket and self.ItemsList == items_list:
            return True
        return False

    def _onGenerate(self, source):
        source.addNotify(Notificator.onItemCollectInit, self.Socket, self.ItemsList, self.SceneName, self.SocketName)

        # for finding item collect from other scene, coz itemCollect onCheck from other scene will return False

        QuestLocator = self.addQuest(source, "ItemCollectOpenLocator", SceneName=self.SceneName, GroupName=self.GroupName)

        Quest = self.addQuest(source, "ItemCollect", SceneName=self.SceneName, GroupName=self.GroupName, ItemList=self.ItemsList, Object=self.Socket)

        with Quest as tc_quest:
            tc_quest.addListener(Notificator.onItemCollectComplete, Filter=self.__filter)

        with QuestLocator as tc_quest:
            pass