from Foundation.Task.MixinObjectTemplate import MixinSocket
from Foundation.Task.TaskAlias import TaskAlias


class AliasApplyInventoryItem(MixinSocket, TaskAlias):
    def _onParams(self, params):
        super(AliasApplyInventoryItem, self)._onParams(params)
        self.taken = params.get("Taken", True)
        self.pick = params.get("Pick", False)
        self.tipID = params.get("TipID", None)
        self.InventoryItem = params.get("InventoryItem")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskSocketPlaceInventoryItem", SocketName=self.SocketName, InventoryItem=self.InventoryItem,
                       Taken=self.taken, Pick=self.pick)

        if self.pick is True:
            source.addTask("TaskStateMutex", ID="StateAddItem", From=False, To=True)
            source.addListener(Notificator.onInventoryReturnInventoryItem)
            source.addTask("TaskStateChange", ID="StateAddItem", Value=False)
            pass

        #        source.addTask( "TaskPrint" , Value = "after TaskSocketPlaceInventoryItem in Alias %s %s"%(self.SocketName, self.InventoryItem.name))
        #        source.addTask( "TaskStateMutex", ID = "StateAddItem", From = False, To = True)
        #        source.addTask( "TaskEffectInventoryAddItem", ItemName = self.ItemName, EffectName = "Movie_HintWay", Front = False)
        #        source.addTask( "TaskEffectInventorySlotAdd", ItemName = self.ItemName, EffectName = "Movie_HOGPickItem")
        #        source.addTask( "TaskInventoryAddItem", ItemName = self.ItemName )
        #        source.addTask( "TaskStateChange", ID = "StateAddItem", Value = False)
        pass

    pass
