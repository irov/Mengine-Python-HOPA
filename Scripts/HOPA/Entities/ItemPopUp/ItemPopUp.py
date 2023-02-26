from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.TaskManager import TaskManager
from HOPA.PopUpItemManager import PopUpItemManager
from Notification import Notification

class ItemPopUp(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "ItemName")
        Type.addAction(Type, "Open", Update=ItemPopUp._updateOpen)

    def _updateOpen(self, value):
        if value is not True:
            return

        self.InventoryItem = PopUpItemManager.getItemInventoryItem(self.ItemName)
        if self.InventoryItem is not None and self.InventoryItem.isActive() is False:
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

        self.InventoryItem = PopUpItemManager.getItemInventoryItem(self.ItemName)

        if self.InventoryItem is None:
            Trace.log("Entity", 0, "ItemPopUp._openItemPopUp: not found item %s" % (self.ItemName))
            return

        if not self.InventoryItem.isActive():
            Trace.log("Entity", 0, "ItemPopUp._openItemPopUp: not active item %s" % (self.ItemName))
            return

        InventoryItemNode = self.InventoryItem.getEntityNode()
        InventoryItemNode.enable()
        Point_Item.attach(InventoryItemNode)

        pos = self.getItemOffset()
        self.InventoryItem.setPosition(pos)

        ItemName_TextID = PopUpItemManager.getItemTextID(self.ItemName)
        ItemNameText = Mengine.getTextFromID(ItemName_TextID)
        text = self.object.getObject("Text_ItemName")
        textEn = text.getEntity()
        textField = textEn.getTextField()
        textField.setTextID("ID_ITEM_POPUP_Descriptions")
        textField.setTextFormatArgs(ItemNameText)

        self.Socket_Back = self.object.getObject("Socket_Back")
        PopUpItemEscClose = DefaultManager.getDefaultBool("PopUpItemEscClose", False)
        PopUpItemBackClose = DefaultManager.getDefaultBool("PopUpItemBackClose", False)

        with TaskManager.createTaskChain(Name="ItemPopUp", Group=self.object, Cb=self.__notifyEnd) as tc:
            tc.addScope(self.scopeOpen, "ItemPopUp")
            tc.addTask("TaskEnable", Object=self.Socket_Back, Value=True)
            tc.addTask("TaskInteractive", Object=self.Socket_Back, Value=True)
            tc.addTask("TaskEnable", Object=self.InventoryItem)
            tc.addTask("TaskNotify", ID=Notificator.onItemPopUpOpen, Args=(self.ItemName,))

            with tc.addRaceTask(4) as (tc_scene, tc_button, tc_esc, tc_back):
                tc_scene.addListener(Notificator.onTransitionBegin)
                tc_button.addTask("TaskMovie2ButtonClick", Movie2ButtonName="Movie2Button_Ok")

                if PopUpItemEscClose is True:
                    tc_esc.addTask("TaskActiveLayerEsc", LayerName="ItemPopUp")
                else:
                    tc_esc.addBlock()

                if PopUpItemBackClose is True:
                    tc_back.addTask("TaskSocketClick", Socket=self.Socket_Back)
                else:
                    tc_back.addBlock()

            tc.addTask("TaskSetParam", Object=self.object, Param="Open", Value=False)
            tc.addTask("TaskEnable", Object=self.InventoryItem, Value=False)
            tc.addTask("TaskObjectReturn", Object=self.InventoryItem)
            tc.addTask("TaskEnable", Object=self.Socket_Back, Value=False)
            tc.addTask("TaskInteractive", Object=self.Socket_Back, Value=False)
            tc.addNotify(Notificator.onItemPopUpEnd, self.ItemName)

            tc.addScope(self.scopeClose, "ItemPopUp")

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
                guard_source_movie.addTask("TaskEnable", Object=Movie, Value=True)
                guard_source_movie.addTask("TaskMovie2Play", Movie2=Movie, Wait=True)
                guard_source_movie.addTask("TaskEnable", Object=Movie, Value=False)

    def __notifyEnd(self, isSkip):
        Notification.notify(Notificator.onItemPopUpClose, self.ItemName)

    def _onDeactivate(self):
        if TaskManager.existTaskChain("ItemPopUp") is True:
            TaskManager.cancelTaskChain("ItemPopUp")

        if self.Open is True:
            self.InventoryItem.returnToParent()