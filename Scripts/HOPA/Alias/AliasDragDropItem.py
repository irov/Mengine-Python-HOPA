from Event import Event
from Foundation.Notificator import Notificator
from Foundation.Task.TaskAlias import TaskAlias

SCALE_TO = 1.1
SCALE_TIME = 250.0


class AliasDragDropItem(TaskAlias):
    def _onParams(self, params):
        super(AliasDragDropItem, self)._onParams(params)
        self.ItemName = params.get("ItemName", None)
        self.Item = params.get("Item")
        self.SocketObject = params.get("SocketObject", None)
        self.AutoAttach = params.get("AutoAttach", False)
        self.EventValidClick = Event("onDragDropValidClick")

        self.Touchpad = Mengine.hasTouchpad() is True
        self.EventEnd = Event("onDragDropItemEnd")

    def _scopeValidClick(self, source):
        socket_object_type = self.SocketObject.getType()
        if socket_object_type is "ObjectSocket":
            source.addTask("TaskSocketUseItem", Socket=self.SocketObject, Item=self.ItemObject, Taken=False)
        else:
            source.addTask("TaskItemPlaceItem", SocketItem=self.SocketObject, Item=self.ItemObject)
        if self.Touchpad is True:
            source.addFunction(self.EventEnd)
        source.addTask("AliasEnergyConsume", Action="DragDropItem", Cb=self.EventValidClick)

    def _scopeInvalidClick(self, source):
        source.addTask("TaskItemInvalidUse", Item=self.ItemObject)
        source.addDelay(0)

        if self.Touchpad is True:
            source.addFunction(self.EventEnd)
        source.addTask("AliasRemoveItemAttach", Item=self.ItemObject)

        source.addEnable(self.ItemObject)
        source.addFunction(self.ItemObject.onEntityRestore)

    def _scopeInterrupt(self, source):
        with source.addRaceTask(2) as (race_leave, race_restart):
            race_leave.addListener(Notificator.onSceneDeactivate)
            race_restart.addListener(Notificator.onSceneRestartBegin)

        if self.Touchpad is True:
            source.addFunction(self.EventEnd)
        source.addTask("AliasRemoveItemAttach", Item=self.ItemObject)

    def _onGenerate(self, source):
        if self.ItemName is not None:
            self.ItemObject = self.Group.getObject(self.ItemName)
        else:
            self.ItemObject = self.Item

        if self.AutoAttach is True:
            source.addTask("AliasItemAttach", Item=self.ItemObject, AutoAttach=True)

        with source.addRepeatTask() as (repeat, until):
            if self.Touchpad is True:
                repeat.addTask("AliasItemAttach", Item=self.ItemObject, AddArrowChild=False)
                repeat.addScope(self.forkPlayItemSelectEffect)
            else:
                repeat.addTask("AliasItemAttach", Item=self.ItemObject)
            repeat.addNotify(Notificator.onSoundEffectOnObject, self.SocketObject, "DragDropItem_PressOnItem")

            with repeat.addRaceTask(3) as (valid, invalid, leave):
                # CASE 1: valid click ----------------------------------------------
                valid.addScope(self._scopeValidClick)

                # CASE 2: invalid click --------------------------------------------
                invalid.addScope(self._scopeInvalidClick)

                # CASE 3: scene leave ----------------------------------------------
                leave.addScope(self._scopeInterrupt)

            until.addEvent(self.EventValidClick)

        source.addTask("AliasRemoveItemAttach", Item=self.ItemObject)
        source.addDisable(self.ItemObject)
        source.addFunction(self.ItemObject.onEntityRestore)

    def forkPlayItemSelectEffect(self, source):
        itemNode = self.ItemObject.getEntityNode()

        def _cbStop():
            itemNode.scaleStop()
            itemNode.setScale((1.0, 1.0, 1.0))

        with source.addFork() as tc_fork:
            with tc_fork.addRepeatTask() as (repeat, until):
                repeat.addTask("TaskNodeScaleTo", Node=itemNode, To=(SCALE_TO, SCALE_TO, 1.0), Time=SCALE_TIME)
                repeat.addTask("TaskNodeScaleTo", Node=itemNode, To=(1.0, 1.0, 1.0), Time=SCALE_TIME)
                until.addEvent(self.EventEnd)

            tc_fork.addFunction(_cbStop)
