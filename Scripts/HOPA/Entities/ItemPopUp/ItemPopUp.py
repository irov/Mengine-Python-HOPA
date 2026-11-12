from Foundation.DefaultManager import DefaultManager
from Foundation.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.TaskManager import TaskManager
from HOPA.PopUpItemManager import PopUpItemManager

class ItemPopUp(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction("ItemName")
        Type.addAction("Open", Update=ItemPopUp._updateOpen)

    def __init__(self):
        super(ItemPopUp, self).__init__()

        self.InventoryItem = None
        self.itemPopUpChain = None

    def _updateOpen(self, value):
        if value is not True:
            return

        # Shared popup layers can remain active while the game scene restarts.
        if TaskManager.existTaskChain("ItemPopUp") is True:
            return

        self._openItemPopUp()

    def getItemOffset(self):
        itemEntity = self.InventoryItem.getEntity()

        spriteCenter = itemEntity.getSpriteCenter()

        x = - spriteCenter[0]
        y = - spriteCenter[1]

        return x, y

    def _openItemPopUp(self):
        Point_Item = self.getSubEntity("Point_Item")

        inventoryItem = PopUpItemManager.getItemInventoryItem(self.ItemName)

        if inventoryItem is None:
            Trace.log("Entity", 0, "ItemPopUp._openItemPopUp: not found item %s" % (self.ItemName))
            return

        if inventoryItem.isActive() is False:
            return

        self.InventoryItem = inventoryItem
        InventoryItemNode = inventoryItem.getEntityNode()
        InventoryItemNode.enable()
        Point_Item.attach(InventoryItemNode)

        pos = self.getItemOffset()
        self.InventoryItem.setPosition(pos)

        ItemName_TextID = PopUpItemManager.getItemTextID(self.ItemName)
        ItemNameText = Mengine.getTextFromId(ItemName_TextID)
        text = self.object.getObject("Text_ItemName")
        textEn = text.getEntity()
        textField = textEn.getTextField()
        textField.setTextId("ID_ITEM_POPUP_Descriptions")
        textField.setTextFormatArgs(ItemNameText)

        self.Socket_Back = self.object.getObject("Socket_Back")
        PopUpItemEscClose = DefaultManager.getDefaultBool("PopUpItemEscClose", False)
        PopUpItemBackClose = DefaultManager.getDefaultBool("PopUpItemBackClose", False)

        self.itemPopUpChain = TaskManager.createTaskChain(Name="ItemPopUp", Group=self.object, Cb=self.__notifyEnd)
        with self.itemPopUpChain as tc:
            tc.addScope(self.scopeOpen, "ItemPopUp")
            tc.addEnable(self.Socket_Back)
            tc.addTask("TaskInteractive", Object=self.Socket_Back, Value=True)
            tc.addEnable(self.InventoryItem)
            tc.addNotify(Notificator.onItemPopUpOpen, self.ItemName)

            with tc.addRaceTask(4) as (tc_scene, tc_button, tc_esc, tc_back):
                tc_scene.addListener(Notificator.onTransitionBegin)

                tc_button.addScope(self._scopeClickOk)

                if PopUpItemEscClose is True:
                    tc_esc.addTask("TaskActiveLayerEsc", LayerName="ItemPopUp")
                else:
                    tc_esc.addBlock()

                if PopUpItemBackClose is True:
                    tc_back.addTask("TaskSocketClick", Socket=self.Socket_Back)
                else:
                    tc_back.addBlock()

            tc.addParam(self.object, "Open", False)
            tc.addDisable(self.InventoryItem)
            tc.addFunction(self.__returnInventoryItem)
            tc.addDisable(self.Socket_Back)
            tc.addTask("TaskInteractive", Object=self.Socket_Back, Value=False)
            tc.addNotify(Notificator.onItemPopUpEnd, self.ItemName)

            tc.addScope(self.scopeClose, "ItemPopUp")

    def _scopeClickOk(self, source):
        if self.object.hasObject("Movie2Button_Ok"):
            source.addTask("TaskMovie2ButtonClick", Movie2ButtonName="Movie2Button_Ok")
        elif self.object.hasObject("Button_Ok"):
            source.addTask("TaskButtonClick", ButtonName="Button_Ok")
            if _DEVELOPMENT is True:
                Trace.msg_err("ItemPopUp: Button_Ok is deprecated, use Movie2Button_Ok instead")
        else:
            source.addDelay(1000)
            Trace.log("Entity", 0, "ItemPopUp._openItemPopUp: not found button Movie2Button_Ok")

    def scopeOpen(self, source, GropName):
        MovieName = "Movie2_Open"
        source.addScope(self.SceneEffect, GropName, MovieName)

    def scopeClose(self, source, GropName):
        MovieName = "Movie2_Close"
        source.addScope(self.SceneEffect, GropName, MovieName)

    def SceneEffect(self, source, GropName, MovieName):
        if GroupManager.hasObject(GropName, MovieName) is False:
            return
        if GroupManager.getGroup(GropName).getEnable() is False:
            return

        Movie = GroupManager.getObject(GropName, MovieName)
        with GuardBlockInput(source) as guard_source:
            with guard_source.addParallelTask(2) as (guard_source_movie, guard_source_fade):
                guard_source_movie.addEnable(Movie)
                guard_source_movie.addTask("TaskMovie2Play", Movie2=Movie, Wait=True)
                guard_source_movie.addDisable(Movie)

    def __returnInventoryItem(self):
        inventoryItem = self.InventoryItem
        self.InventoryItem = None

        if inventoryItem is None:
            return

        inventoryItem.returnToParent()

    def __notifyEnd(self, isSkip):
        self.itemPopUpChain = None
        Notification.notify(Notificator.onItemPopUpClose, self.ItemName)

    def _onDeactivate(self):
        tc = self.itemPopUpChain
        self.itemPopUpChain = None

        if tc is not None:
            tc.cancel()

        self.__returnInventoryItem()
