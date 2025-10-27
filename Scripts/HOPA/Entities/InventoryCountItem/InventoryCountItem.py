from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager

InventoryItem = Mengine.importEntity("InventoryItem")

class InventoryCountItem(InventoryItem):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction("FoundItems",
                       Update=InventoryItem._restoreFoundItems,
                       Append=InventoryCountItem._appendFoundItems,
                       Remove=InventoryItem._removeFoundItems)

        Type.addAction("SpriteResourceName")
        Type.addAction("ArrowPoint")
        Type.addAction("SlotPoint")
        Type.addAction("FontName")

    def __init__(self):
        super(InventoryCountItem, self).__init__()
        self.tc = None
        self.Movie = None

    def _onInitialize(self, obj):
        super(InventoryCountItem, self)._onInitialize(obj)

        self.textField = Mengine.createNode("TextField")
        self.textField.setPixelsnap(False)

        DefaultTextID = DefaultManager.getDefault('DefaultInventoryCountItemTextID', None)
        if DefaultTextID is not None:
            self.textField.setTextId(DefaultTextID)
        else:
            if self.FontName is not None:
                self.textField.setFontName(self.FontName)

            self.textField.setTextId("ID_InventoryCountItem")
            self.textField.setFontColor((1, 1, 1, 1))

        if self.text_Atach(obj) is False:
            self.addChild(self.textField)  # self.addChild(self.textField)

    def _onFinalize(self):
        super(InventoryCountItem, self)._onFinalize()

        Mengine.destroyNode(self.textField)
        self.textField = None

        self.Full_Clean()

        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

    def Full_Clean(self):
        if self.Movie is not None:
            self.Movie.returnToParent()
            self.Movie.onDestroy()
            self.Movie = None

    def text_Atach(self, obj):
        if GroupManager.hasGroup("ItemPlusData") is False:
            return False

        groupSpesial = GroupManager.getGroup("ItemPlusData")
        if groupSpesial.isActive() is False:
            return False

        if groupSpesial.hasPrototype("Movie2_Item_Count") is False:
            return False

        self.Movie = groupSpesial.generateObject("Plus_%s" % (obj.getName()), "Movie2_Item_Count")
        if self.Movie is not None:
            node = self.Movie.getEntityNode()
            self.addChild(node)

            Center = self.getSpriteCenter()
            node.setLocalPosition(Center)

            slot = self.Movie.getMovieSlot("slot")
            slot.addChild(self.textField)
            return True

        return False

    def _getProgressTotal(self):
        return self.object._getProgressTotal()

    def checkCount(self):
        return self.object.checkCount()

    def _appendFoundItems(self, id, element):
        super(InventoryCountItem, self)._appendFoundItems(id, element)
        progress, total = self._getProgressTotal()
        if progress == total:
            Notification.notify(Notificator.onInventoryItemCountComplete, self.object)

    def _updateCount(self):
        self.textField.enable()

        progress, total = self._getProgressTotal()

        self.tc = TaskManager.createTaskChain(Repeat=False)

        with self.tc as tc_light:
            tc_light.addFunction(self.Func_updateCount, progress, total)

    def Func_updateCount(self, progress, total):
        if self.textField is None:
            return

        CountItemDisableTextWhenFull = DefaultManager.getDefaultBool("CountItemDisableTextWhenFull", False)
        if progress == total and CountItemDisableTextWhenFull:
            self.textField.disable()
        self.textField.setTextFormatArgs(progress, total)
