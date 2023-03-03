from Foundation.ArrowManager import ArrowManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasDragDropPuzzle(TaskAlias):
    def _onParams(self, params):
        super(AliasDragDropPuzzle, self)._onParams(params)
        self.ItemName = params.get("ItemName")
        self.SocketItemName = params.get("SocketItemName", None)
        self.SocketName = params.get("SocketName", None)
        self.ItemObject = None
        self.Position = None
        self.offset = (0, 0)

        pass

    def _onGenerate(self, source):
        self.ItemObject = self.Group.getObject(self.ItemName)
        ItemPos = self.ItemObject.getPosition()

        ItemEntity = self.ItemObject.getEntity()
        Image = ItemEntity.getSprite()
        origin = Image.getLocalImageCenter()

        self.ItemObject.setOrigin(origin)

        self.Position = (ItemPos[0] + origin.x, ItemPos[1] + origin.y)
        self.ItemObject.setPosition(self.Position)
        #        print self.ItemObject.setAlpha(0.3)

        with source.addRepeatTask() as (tc_do, tc_until):
            tc_do.addTask("TaskItemClick", Item=self.ItemObject, Trade=True)

            tc_do.addTask("TaskFanItemInHand", FanItem=self.ItemObject)

            tc_do.addTask("TaskFunction", Fn=self.__setItemOffset)
            tc_do.addTask("TaskFunction", Fn=self.ItemObject.setAlpha, Args=(0.75,))
            tc_do.addTask("TaskArrowAttach2", Offset=False, Origin=True, Object=self.ItemObject)

            with tc_do.addRaceTask(2) as (tc_iu, tc_no):
                tc_no.addTask("TaskListener", ID=Notificator.onAttachTrade)

                tc_iu.addTask("TaskItemInvalidUse", Item=self.ItemObject)
                pass

            tc_do.addTask("TaskRemoveArrowAttach")
            tc_do.addTask("TaskFunction", Fn=self.ItemObject.setAlpha, Args=(1,))
            tc_do.addTask("TaskFunction", Fn=self.__calcPosition)

            tc_do.addTask("TaskFanItemInNone", FanItem=self.ItemObject)
            tc_do.addTask("TaskObjectReturn", Object=self.ItemObject)
            tc_do.addTask("TaskNotify", ID=Notificator.onPuzzleOutPlaced, Args=(self.ItemName,))
            tc_do.addTask("TaskSceneLayerAddEntity", LayerName="PuzzleDragDrop", Object=self.ItemObject)

            if self.SocketItemName is not None:
                tc_until.addTask("TaskItemPlaceItem", SocketItemName=self.SocketItemName, Item=self.ItemObject, Accuracy=35)
                tc_until.addTask("TaskFunction", Fn=self.ItemObject.setAlpha, Args=(1,))
                pass
            else:
                tc_until.addTask("TaskSocketUseItem", SocketName=self.SocketName, Item=self.ItemObject, Taken=True)
                pass
            pass

        source.addTask("TaskFunction", Fn=self.__resetOrigin)
        source.addTask("TaskRemoveArrowAttach")
        source.addTask("TaskFanItemInNone", FanItem=self.ItemObject)
        source.addTask("TaskObjectSetPosition", Object=self.ItemObject, Value=self.Position)
        source.addTask("TaskSceneLayerAddEntity", LayerName="PuzzleDragDrop", Object=self.ItemObject)
        pass

    def __resetOrigin(self):
        self.ItemObject.setOrigin((0, 0))
        pass

    def __setItemOffset(self):
        itemPos = self.ItemObject.getPosition()
        arrow = ArrowManager.getArrow()
        arrowPos = arrow.getLocalPosition()

        self.offset = (arrowPos.x - itemPos[0], arrowPos.y - itemPos[1])
        pass

    def __calcPosition(self):
        arrow = ArrowManager.getArrow()
        arrowPos = arrow.getLocalPosition()

        self.Position = (arrowPos.x - self.offset[0], arrowPos.y - self.offset[1])

        self.ItemObject.setPosition(self.Position)
        pass

    pass
