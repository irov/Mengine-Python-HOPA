from Foundation.Notificator import Notificator
from HOPA.Macro.MacroCommand import MacroCommand

class MacroDragDropItem(MacroCommand):
    def _onValues(self, values):
        self.ItemsQueue = values[1::2]
        self.SocketQueue = values[0::2]

    def _onInitialize(self):
        self.SocketQueueObjects = []

        for i in range(len(self.SocketQueue)):
            finder_type, socket_object = self.findObject(self.SocketQueue[i])
            self.SocketQueueObjects.append(socket_object)

    def _onGenerate(self, source):
        if len(self.ItemsQueue) > 0:
            for item_name, socket_object in zip(self.ItemsQueue, self.SocketQueueObjects):
                item_index = self.ItemsQueue.index(item_name)

                auto_attach = False
                if item_index != 0:
                    auto_attach = True

                source.addNotify(Notificator.onDragDropItemCreate, self.GroupName, item_name, False)

                quest = self.addQuest(source, "DragDropItem", SceneName=self.SceneName, GroupName=self.GroupName, Object=socket_object, ItemName=item_name)
                with quest as tc_quest:
                    finder_type, object_ = self.findObject(item_name)
                    tc_quest.addTask("AliasDragDropItem", Item=object_, SocketObject=socket_object, AutoAttach=auto_attach)

                source.addNotify(Notificator.onDragDropItemComplete, self.GroupName, item_name, False)