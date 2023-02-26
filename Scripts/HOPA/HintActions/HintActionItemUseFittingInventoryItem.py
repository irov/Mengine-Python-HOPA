from Foundation.DemonManager import DemonManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Task.MixinObjectTemplate import MixinItem
from Foundation.TaskManager import TaskManager
from HOPA.HintAction import HintAction
from HOPA.ItemManager import ItemManager

class HintActionItemUseFittingInventoryItem(MixinItem, HintAction):
    def __init__(self):
        super(HintActionItemUseFittingInventoryItem, self).__init__()

        self.InventoryItem = None
        self.SocketName = None

        self.Inventory = DemonManager.getDemon("FittingInventory")
        pass

    def _onParams(self, params):
        super(HintActionItemUseFittingInventoryItem, self)._onParams(params)

        self.InventoryItem = params["InventoryItem"]
        pass

    def _getHintObject(self):
        return self.Item
        pass

    def _onCheck(self):
        if self.Inventory.hasInventoryItem(self.InventoryItem) is False:
            return False
            pass

        return True
        pass

    def _onAction(self, hint):
        Inventory = DemonManager.getDemon("FittingInventory")

        CurrentSlotIndex = Inventory.getParam("CurrentSlotIndex")
        SlotCount = Inventory.getParam("SlotCount")

        InventoryItemIndex = Inventory.getInventoryItemIndex(self.InventoryItem)
        NewSlotIndex = int(InventoryItemIndex / SlotCount) * SlotCount

        Point = hint.getPoint()

        with TaskManager.createTaskChain() as tc:
            if CurrentSlotIndex != NewSlotIndex:
                with GuardBlockInput(tc) as guard_tc:
                    guard_tc.addTask("TaskInventorySlotsHideInventoryItem", Inventory=Inventory)
                    guard_tc.addTask("TaskInventoryCurrentSlotIndex", Inventory=Inventory, Value=NewSlotIndex)
                    pass
                pass

            tc.addTask("TaskSceneLayerGroupEnable", LayerName="HintEffect", Value=True)

            tc.addTask("TaskSoundEffect", SoundName="SparklesCircle", Wait=False)

            tc.addTask("TaskObjectSetPosition", GroupName="HintEffect", ObjectName="Movie_HintWay", Value=Point)
            tc.addTask("TaskMoviePlay", GroupName="HintEffect", MovieName="Movie_HintWay", Loop=True, Wait=False)

            P0 = Point

            InventoryItem = ItemManager.findItemInventoryItem(self.InventoryItem)
            InventoryItemEntity = InventoryItem.getEntity()
            Sprite = InventoryItemEntity.getSprite()

            P2 = Sprite.getWorldImageCenter()

            p1x = P0[0] if P0[1] > P2[1] else P2[0]
            p1y = P2[1] if P0[1] > P2[1] else P0[1]

            P1 = (p1x, p1y)

            tc.addTask("AliasObjectBezier2To", GroupName="HintEffect", ObjectName="Movie_HintWay", Point1=P1, To=P2, Speed=600 * 0.001)  # speed fix

            tc.addTask("TaskObjectSetPosition", GroupName="HintEffect", ObjectName="Movie_HintInventory", Value=P2)
            tc.addTask("TaskMoviePlay", GroupName="HintEffect", MovieName="Movie_HintInventory", Loop=True, Wait=False)

            NP0 = P2

            ItemEntity = self.Item.getEntity()
            Sprite = ItemEntity.getSprite()

            NP2 = Sprite.getWorldImageCenter()

            np1x = NP0[0] if NP0[1] > NP2[1] else NP2[0]
            np1y = NP2[1] if NP0[1] > NP2[1] else NP0[1]

            NP1 = (np1x, np1y)

            tc.addTask("AliasObjectBezier2To", GroupName="HintEffect", ObjectName="Movie_HintWay", Point1=NP1, To=NP2, Speed=600 * 0.001)  # speed fix
            tc.addTask("TaskMovieInterrupt", GroupName="HintEffect", MovieName="Movie_HintWay")

            tc.addTask("TaskObjectSetPosition", GroupName="HintEffect", ObjectName="Movie_HintTarget", Value=NP2)
            tc.addTask("TaskMoviePlay", GroupName="HintEffect", MovieName="Movie_HintTarget", Loop=True, Wait=False)

            tc.addTask("TaskSoundEffect", SoundName="Sparklesdisappear", Wait=False, Important=False)

            pass
        pass

    def _onEnd(self):
        with TaskManager.createTaskChain() as tc:
            tc.addTask("TaskMovieInterrupt", GroupName="HintEffect", MovieName="Movie_HintInventory")
            tc.addTask("TaskMovieInterrupt", GroupName="HintEffect", MovieName="Movie_HintTarget")
            pass
        pass
    pass