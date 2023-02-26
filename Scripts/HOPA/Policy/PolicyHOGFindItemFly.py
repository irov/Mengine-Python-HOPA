from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGManager import HOGManager
from HOPA.QuestManager import QuestManager

class PolicyHOGFindItemFly(TaskAlias):
    def _onParams(self, params):
        super(PolicyHOGFindItemFly, self)._onParams(params)
        self.HOG = params.get("HOG")
        self.HOGItemName = params.get("HOGItemName")
        self.EnigmaName = params.get("EnigmaName")
        pass

    def _onGenerate(self, source):
        SceneName = EnigmaManager.getEnigmaSceneName(self.EnigmaName)
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        HOGItems = HOGManager.getHOGItems(self.EnigmaName)
        self.ItemName = HOGItems[self.HOGItemName].objectName
        hogItem = HOGManager.getHOGItem(self.EnigmaName, self.HOGItemName)

        HOGInventory = DemonManager.getDemon("HOGInventory")

        InventoryEntity = HOGInventory.getEntity()
        slot = InventoryEntity.getSlotByName(self.HOGItemName)

        if slot is None:
            self.invalidTask("not found slot %s" % (self.HOGItemName))
            pass

        P2 = slot.getPoint()

        Item = self.Group.getObject(self.ItemName)
        ItemEntity = Item.getEntity()

        Camera = Mengine.getRenderCamera2D()
        tempPos = ItemEntity.getCameraPosition(Camera)

        pure = ItemEntity.generatePure()
        pure.enable()

        offset = pure.getWorldPosition()
        offsetPos = (tempPos[0] + offset.x, tempPos[1] + offset.y)
        pureCenter = pure.getLocalImageCenter()

        P0 = (offsetPos[0] + pureCenter.x, offsetPos[1] + pureCenter.y)

        P1 = (P2[0], P0[1])

        def __onClickItem():
            scene = SceneManager.getCurrentScene()
            mainLayer = scene.getSlot("HogUpEffect")
            mainLayer.addChild(pure)

            pure.setLocalPosition(P0)
            pure.setOrigin(pureCenter)
            pass

        length = Mengine.length_v2_v2(P1, P2)

        HOGItemHideEffectSpeed = DefaultManager.getDefaultFloat("HOGItemHideEffectSpeed", 1000)
        HOGItemHideEffectSpeed *= 0.001  # speed fix
        HOGItemIncreaseTime = DefaultManager.getDefaultFloat("HOGItemIncreaseTime", 1)
        HOGItemIncreaseTime *= 1000  # speed fix
        IncreaseSize = DefaultManager.getDefaultFloat("HOGItemIncreaseSize", 1.2)
        DecreaseSize = DefaultManager.getDefaultFloat("HOGItemDecreaseSize", 0.1)

        time = length / HOGItemHideEffectSpeed
        # time *= 1000  # speed fix

        Quest = QuestManager.createLocalQuest("HOGPickItem", SceneName=SceneName, GroupName=GroupName, HogGroupName=self.GroupName, ItemName=self.ItemName, HogItem=hogItem)

        with QuestManager.runQuest(source, Quest) as tc_quest:
            tc_quest.addTask("TaskItemClick", ItemName=self.ItemName)
            pass

        source.addTask("TaskFunction", Fn=__onClickItem)

        source.addTask("TaskHOGFoundItem", HOG=self.HOG, HOGItemName=self.HOGItemName)
        source.addTask("TaskNotify", ID=Notificator.onHOGFoundItem, Args=(self.HOGItemName,))
        source.addTask("TaskItemPick", ItemName=self.ItemName)

        source.addTask("TaskNodeScaleTo", Node=pure, To=(IncreaseSize, IncreaseSize, 1.0), Time=HOGItemIncreaseTime)

        with source.addParallelTask(2) as (tcp0, tcp1):
            tcp0.addTask("TaskNodeBezier2To", Node=pure, Point1=P1, To=P2, Speed=HOGItemHideEffectSpeed)

            tcp1.addTask("TaskNodeScaleTo", Node=pure, To=(DecreaseSize, DecreaseSize, 1.0), Time=time)
            pass

        source.addTask("TaskNodeRemoveFromParent", Node=pure)
        source.addTask("TaskNodeDestroy", Node=pure)
        source.addTask("TaskHOGInventoryFoundItem", HOGInventory=HOGInventory, HOGItemName=self.HOGItemName)
        source.addTask("TaskHOGInventoryCrossOut", HOGItemName=self.HOGItemName, Immediately=False)
        pass

    pass