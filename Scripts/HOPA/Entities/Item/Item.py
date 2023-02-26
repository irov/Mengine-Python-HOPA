from Foundation.ArrowManager import ArrowManager
from Notification import Notification

Interaction = Mengine.importEntity("Interaction")

class Item(Interaction):
    ITEM_SCENE = 0
    ITEM_HAND = 1

    @staticmethod
    def declareORM(Type):
        Interaction.declareORM(Type)

        Type.addAction(Type, "PureOffset")

        Type.addAction(Type, "SpriteResourceNamePure")
        Type.addAction(Type, "SpriteResourceNameFull")

        Type.addAction(Type, "HotspotImageResourceName")
        Type.addAction(Type, "PickOffset")
        Type.addAction(Type, "ArrowPoint")
        Type.addAction(Type, "SlotPoint")

    def __init__(self):
        super(Item, self).__init__()

        self.state = Item.ITEM_SCENE
        self.sprite = None
        self.staticPure = None

        self.MouseButtonHandlerID = None

    def generatePure(self):
        name = self.getName()
        if self.SpriteResourceNamePure is not None:
            pure = Mengine.createSprite(name, self.SpriteResourceNamePure)
        else:
            pure = Mengine.createSprite(name, self.SpriteResourceNameFull)

        pure.setLocalPosition(self.PureOffset)

        return pure

    def getSpriteCenter(self):
        imageSize = self.sprite.getSurfaceSize()
        imageCenter = (imageSize.x * 0.5, imageSize.y * 0.5)
        return imageCenter

    def generateStaticPure(self):
        name = self.getName()
        if self.SpriteResourceNamePure is not None:
            self.staticPure = Mengine.createSprite(name, self.SpriteResourceNamePure)
        else:
            self.staticPure = Mengine.createSprite(name, self.SpriteResourceNameFull)

        self.staticPure.setLocalPosition(self.PureOffset)

        return self.staticPure

    def destroyStaticPure(self):
        if self.staticPure is None:
            return

        self.staticPure.removeFromParent()
        Mengine.destroyNode(self.staticPure)
        self.staticPure = None

    def tryCombine(self):
        # fix for https://wonderland-games.atlassian.net/browse/HO2-683
        return False

    def onDestroyStaticPure(self):
        self.sprite.enable()

    def generateFull(self):
        name = self.getName()
        full = Mengine.createSprite(name, self.SpriteResourceNameFull)

        return full

    def cleanSprite(self):
        self.sprite.removeFromParent()
        Mengine.destroyNode(self.sprite)
        self.sprite = None

    def attachSprite(self, sprite):
        if self.sprite is not None:
            self.cleanSprite()

        self.sprite = sprite
        self.addChild(self.sprite)

    def getSize(self):
        return self.sprite.getSurfaceSize()

    def getSprite(self):
        return self.sprite

    def _onInitialize(self, obj):
        super(Item, self)._onInitialize(obj)

        full = self.generateFull()
        self.attachSprite(full)

    def _onFinalize(self):
        super(Item, self)._onFinalize()
        self.cleanSprite()

    def _onUpdateEnable(self, value):
        Notification.notify(Notificator.onItemChangeEnable, self.object)

    def _onCreateHotSpot(self):
        if self.object.getPolygon() is not None:
            hotspot = super(Item, self)._onCreateHotSpot()

            # adjust position
            item_pos = self.object.getPosition()
            adjusted_pos = [-pos for pos in item_pos]
            hotspot.setLocalPosition(adjusted_pos)

            return hotspot

        imageHotspot = self.createChild("HotSpotImage")

        imageHotspot.setResourceTestPick(self.HotspotImageResourceName)

        imageHotspot.setLocalPosition(self.PickOffset)
        imageHotspot.setAlphaTest(0.1)

        name = self.getName()
        imageHotspot.setName(name)
        imageHotspot.enable()

        return imageHotspot

    def _onActivate(self):
        super(Item, self)._onActivate()

        self.MouseButtonHandlerID = Mengine.addMouseButtonHandler(self.__onGlobalHandleMouseButtonEventEnd)
        self.itemGlobalMouseEvent(False)

        if self.state == self.ITEM_HAND:
            self.inHand()

        # Mengine.enableGlobalHandler(self.MouseButtonHandlerID, False)

    def _onDeactivate(self):
        super(Item, self)._onDeactivate()

        if self.MouseButtonHandlerID is not None:
            Mengine.removeGlobalHandler(self.MouseButtonHandlerID)
            self.MouseButtonHandlerID = None

    def __onGlobalHandleMouseButtonEventEnd(self, event):
        # print " - isDown:", isDown, "isPressed:", isPressed

        if event.button != 0 or event.isDown is False:
            return

        if ArrowManager.emptyArrowAttach() is True:
            self.itemGlobalMouseEvent(False)
            return

        if self.state is Item.ITEM_HAND:
            Notification.notify(Notificator.onItemInvalidUse, self.object)

    def _mouseEnter(self):
        Notification.notify(Notificator.onItemMouseEnter, self.object)

    def _mouseLeave(self):
        Notification.notify(Notificator.onItemMouseLeave, self.object)

    def _mouseClickBegin(self):
        Notification.notify(Notificator.onItemClickBegin, self.object)

    def _mouseClick(self):
        Notification.notify(Notificator.onItemClick, self.object)

    def itemGlobalMouseEvent(self, value):
        if self.MouseButtonHandlerID is not None:
            # print " -- itemGlobalMouseEvent", value
            Mengine.enableGlobalHandler(self.MouseButtonHandlerID, value)

    def inNone(self):
        # print " -- {!r} inNone".format(self.getName())
        self.state = Item.ITEM_SCENE

        self.itemGlobalMouseEvent(False)

        self.cleanSprite()
        full = self.generateFull()
        self.attachSprite(full)

    def inHand(self):
        # print " -- {!r} inHand".format(self.getName())
        self.state = Item.ITEM_HAND

        self.cleanSprite()
        pure = self.generatePure()
        self.attachSprite(pure)

        self.itemGlobalMouseEvent(True)