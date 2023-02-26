from Foundation.Entity.BaseEntity import BaseEntity
from Notification import Notification

class InventoryItemAccumulate(BaseEntity):
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
        Type.addAction(Type, "FoundItems", Update=InventoryItemAccumulate._restoreFoundItems, Append=InventoryItemAccumulate._appendFoundItems, Remove=InventoryItemAccumulate._removeFoundItems)

        Type.addActionActivate(Type, "Value", Update=InventoryItemAccumulate.__updateValue)
        pass

    def __init__(self):
        super(InventoryItemAccumulate, self).__init__()

        self.state = InventoryItemAccumulate.ITEM_STORE
        self.sprite = None
        pass

    def __updateValue(self, value):
        self.textField.enable()
        pass

    def getSprite(self):
        sprite = self.object.getObject("Sprite_Image")
        spriteEntity = sprite.getEntity()
        resource = spriteEntity.getSprite()
        return resource
        pass

    def getSpriteCenter(self):
        sprite = self.object.getObject("Sprite_Image")
        spriteEntity = sprite.getEntity()
        imageSize = spriteEntity.getSize()
        imageCenter = (imageSize.x * 0.5, imageSize.y * 0.5)
        return imageCenter
        pass

    def _onInitialize(self, obj):
        super(InventoryItemAccumulate, self)._onInitialize(obj)

        pass

    def _onPreparation(self):
        super(InventoryItemAccumulate, self)._onPreparation()

        sprite = self.object.getObject("Sprite_Image")
        self.textField = Mengine.createNode("TextField")

        self.textField.setTextID("ID_InventoryCountItem")

        self.textField.setLocalColor((1, 0, 0, 1))

        spriteEntity = sprite.getEntity()
        spriteEntity.addChild(self.textField)

        pass

    def _onDeactivate(self):
        super(InventoryItemAccumulate, self)._onDeactivate()
        self.textField.removeFromParent()
        pass

    def _onFinalize(self):
        super(InventoryItemAccumulate, self)._onFinalize()

        Mengine.destroyNode(self.textField)
        self.textField = None

        self.sprite = None
        pass

    def inInventory(self):
        self.state = InventoryItemAccumulate.ITEM_INVENTORY
        pass

    def delInventory(self):
        self.state = InventoryItemAccumulate.ITEM_PLACE
        pass

    def pick(self):
        Trace.log("InventoryItem", 3, "InventoryItem %s pick" % (self.object.name))

        if self.state is not InventoryItemAccumulate.ITEM_INVENTORY:
            Trace.log("InventoryItem", 1, "InventoryItem invalid pick, state %d" % (self.state))
            return
            pass

        self.state = InventoryItemAccumulate.ITEM_PICK
        pass

    def invalidUse(self, clickObject):
        Notification.notify(Notificator.onInventoryItemInvalidUse, self.object, clickObject)
        pass

    def pickAfterPlace(self):
        Trace.log("InventoryItem", 3, "InventoryItem %s pick after place" % (self.object.name))

        self.state = InventoryItemAccumulate.ITEM_RETURN
        pass

    def place(self):
        Trace.log("InventoryItem", 3, "InventoryItem %s place" % (self.object.name))

        Notification.notify(Notificator.onInventoryItemPlace, self.object)

        self.state = InventoryItemAccumulate.ITEM_PLACE
        pass

    def take(self):
        Trace.log("InventoryItem", 3, "InventoryItem %s take" % (self.object.name))

        Notification.notify(Notificator.onInventoryItemTake, self.object)

        self.state = InventoryItemAccumulate.ITEM_TAKE
        pass

    def takeItem(self, itemName):
        Trace.log("InventoryItem", 3, "InventoryItem %s take" % (self.object.name))
        self.state = InventoryItemAccumulate.ITEM_RETURN

        foundItems = self.object.getParam("FoundItems")

        self.object.delParam("FoundItems", itemName)

        if len(foundItems) == 0:
            self.state = InventoryItemAccumulate.ITEM_TAKE
            pass
        pass

    def tryCombine(self):
        Trace.log("InventoryItem", 3, "InventoryItem %s try combine" % (self.object.name))
        self.state = InventoryItemAccumulate.ITEM_TRY_COMBINE
        pass

    def combine(self):
        Trace.log("InventoryItem", 3, "InventoryItem %s combine" % (self.object.name))
        self.state = InventoryItemAccumulate.ITEM_COMBINE
        pass

    def store(self):
        self.state = InventoryItemAccumulate.ITEM_STORE
        pass

    def getState(self):
        return self.state
        pass

    def setState(self, _state):
        self.state = _state
        pass

    def _appendFoundItems(self, id, element):
        self._updateCount()
        pass

    def _removeFoundItems(self, id, element, oldElements):
        self._updateCount()
        pass

    def _restoreFoundItems(self, foundItems):
        self._updateCount()
        pass

    def _updateCount(self):
        pass

    pass