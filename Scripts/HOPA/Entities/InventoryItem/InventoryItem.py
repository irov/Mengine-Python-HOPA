from Foundation.Entity.BaseEntity import BaseEntity

class InventoryItem(BaseEntity):
    ITEM_STORE = 0
    ITEM_INVENTORY = 1
    ITEM_PICK = 2
    ITEM_RETURN = 3
    ITEM_PLACE = 4
    ITEM_TAKE = 5
    ITEM_TRY_COMBINE = 6
    ITEM_COMBINE = 7

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "FoundItems",
                       Update=InventoryItem._restoreFoundItems,
                       Append=InventoryItem._appendFoundItems,
                       Remove=InventoryItem._removeFoundItems)

        Type.addAction(Type, "SpriteResourceName")
        Type.addAction(Type, "SlotPoint")
        Type.addAction(Type, "ArrowPoint")

    def __init__(self):
        super(InventoryItem, self).__init__()

        self.state = InventoryItem.ITEM_STORE
        self.effect = None
        self.sprite = None

    def getSprite(self):
        return self.sprite

    def getSpriteCenter(self):
        return self._getItemCenter()

    def _getItemCenter(self):
        # - non-virtual interface, override this method if want another behavior
        # - means that item may be hold not only sprite
        imageCenter = self.sprite.getLocalImageCenter()
        return imageCenter

    def _onInitialize(self, obj):
        super(InventoryItem, self)._onInitialize(obj)

        self._createSprite()

    def _onFinalize(self):
        super(InventoryItem, self)._onFinalize()

        self.effect = None

        self._destroySprite()

    def _createSprite(self):
        if self.SpriteResourceName is None:
            return

        name = self.getName()
        self.sprite = Mengine.createSprite(name, self.SpriteResourceName)

        self.addChild(self.sprite)

    def _destroySprite(self):
        if self.sprite is None:
            return

        Mengine.destroyNode(self.sprite)
        self.sprite = None

    def inInventory(self):
        self.state = InventoryItem.ITEM_INVENTORY

    def delInventory(self):
        self.state = InventoryItem.ITEM_PLACE

    def pick(self):
        Trace.log("InventoryItem", 3, "InventoryItem %s pick" % (self.object.name))

        if self.state is not InventoryItem.ITEM_INVENTORY:
            Trace.log("InventoryItem", 1, "InventoryItem invalid pick, state %d" % (self.state))
            return

        self.state = InventoryItem.ITEM_PICK

    def invalidUse(self, clickObject):
        Notification.notify(Notificator.onInventoryItemInvalidUse, self.object, clickObject)
        Notification.notify(Notificator.onSoundEffectOnObject, self.object, "InventoryItemInvalidUse")

    def pickAfterPlace(self):
        Trace.log("InventoryItem", 3, "InventoryItem %s pick after place" % (self.object.name))

        self.state = InventoryItem.ITEM_RETURN

    def place(self):
        Trace.log("InventoryItem", 3, "InventoryItem %s place" % (self.object.name))

        Notification.notify(Notificator.onInventoryItemPlace, self.object)

        self.state = InventoryItem.ITEM_PLACE

    def take(self):
        Trace.log("InventoryItem", 3, "InventoryItem %s take" % (self.object.name))

        Notification.notify(Notificator.onInventoryItemTake, self.object)

        self.state = InventoryItem.ITEM_TAKE

    def takeItem(self, itemName):
        Trace.log("InventoryItem", 3, "InventoryItem %s take" % (self.object.name))
        self.state = InventoryItem.ITEM_RETURN

        foundItems = self.object.getParam("FoundItems")

        self.object.delParam("FoundItems", itemName)

        if len(foundItems) == 0:
            self.state = InventoryItem.ITEM_TAKE

    def tryCombine(self):
        Trace.log("InventoryItem", 3, "InventoryItem %s try combine" % (self.object.name))
        self.state = InventoryItem.ITEM_TRY_COMBINE

    def combine(self):
        Trace.log("InventoryItem", 3, "InventoryItem %s combine" % (self.object.name))
        self.state = InventoryItem.ITEM_COMBINE

    def store(self):
        self.state = InventoryItem.ITEM_STORE

    def _appendFoundItems(self, id, element):
        # - fix for CountItem ----------------------
        # - append FoundItems can be called twice
        # - this produce found item duplicating
        # ------------------------------------------
        if self.FoundItems.count(element) > 1:
            self.object.delParam("FoundItems", element)
        # ------------------------------------------
        self._updateCount()

    def _removeFoundItems(self, id, element, oldElements):
        self._updateCount()

    def _restoreFoundItems(self, foundItems):
        self._updateCount()

    def getState(self):
        return self.state

    def setState(self, _state):
        self.state = _state

    def _updateCount(self):
        pass

    def checkCount(self):
        return self.object.checkCount()
