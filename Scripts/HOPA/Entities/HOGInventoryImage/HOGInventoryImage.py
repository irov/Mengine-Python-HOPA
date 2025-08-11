from Foundation import Utils
from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGImageManager import HOGImageManager
from HOPA.HOGManager import HOGManager

class HOGInventorySlot(object):
    def __init__(self):
        self.item = None
        self.movie = None
        self.hogItemName = None
        self.count = 1
        pass

    def getCount(self):
        return self.count
        pass

    def setMovie(self, movie):
        self.movie = movie
        pass

    def setHOGItemName(self, name):
        self.hogItemName = name
        pass

    def getHOGItemName(self):
        return self.hogItemName
        pass

    def isEmpty(self):
        return self.hogItemName is None
        pass

    def setItem(self, item):
        self.item = item
        self.item.setEnable(True)

        itemEntity = self.item.getEntity()
        itemEntity.inInventory()
        self.item.setPosition((0, 0))

        InventoryItemScale = DefaultManager.getDefaultFloat("HOGInventoryItemScale", 1.0)
        item.setScale((InventoryItemScale, InventoryItemScale, 1.0))

        slotItem = self.getItemSlot()
        self.point = slotItem.getWorldPosition()
        slotItem.addChild(itemEntity)

        self.movie.setEnable(True)
        self.item.setEnable(True)
        pass

    def getSprite(self):
        return self.movie
        pass

    def getItemSlot(self):
        movieEntity = self.movie.getEntity()

        slotItem = movieEntity.getMovieSlot("item")
        return slotItem
        pass

    def getPoint(self):
        return self.point
        pass

    def release(self):
        if self.item is not None:
            self.item.setEnable(False)
            removeItemEntity = self.item.getEntity()
            removeItemEntity.removeFromParent()
            self.item = None
            pass

        if self.movie is not None:
            spriteEntity = self.movie.getEntity()
            spriteEntity.removeFromParent()
            self.movie.removeFromParent()
            self.movie = None
            pass

        self.hogItemName = None


class HOGInventoryImage(BaseEntity):
    HOG_TEXT_COLOR_OFF = (0.3, 0.3, 0.3, 1)

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "SlotCount")
        Type.addAction(Type, "Slots")

        Type.addAction(Type, "HOG")
        Type.addActionActivate(Type, "FindItems",
                               Append=HOGInventoryImage._appendFindItems,
                               Update=HOGInventoryImage._updateFindItems)
        Type.addAction(Type, "ItemsCount", Update=HOGInventoryImage._updateItemsAllCount)

        Type.addActionActivate(Type, "FoundItems",
                               Append=HOGInventoryImage._appendFoundItems,
                               Update=HOGInventoryImage._updateFoundItems)
        pass

    def __init__(self):
        super(HOGInventoryImage, self).__init__()
        self.slots = []

        # Only if DB value is present inscribe inventory image in this size.
        self.inventoryImageMaxSize = None
        inventoryImageMaxSize = DefaultManager.getDefault("HOGInventoryImageMaxSize")
        if inventoryImageMaxSize:
            inventoryImageMaxSize = inventoryImageMaxSize.split(",")
            self.inventoryImageMaxSize = (int(inventoryImageMaxSize[0]), int(inventoryImageMaxSize[1]))
            pass

        # Only if DB value is present decolorize image and fill it with given color.
        self.inventoryImageColor = None
        inventoryImageColor = DefaultManager.getDefault("HOGInventoryImageColor")
        if inventoryImageColor:
            inventoryImageColor = inventoryImageColor.split(",")
            self.inventoryImageColor = (
            float(inventoryImageColor[0]), float(inventoryImageColor[1]), float(inventoryImageColor[2]),
            float(inventoryImageColor[3]))
            pass
        pass

    def getSlotCount(self):
        return self.SlotCount
        pass

    def getSlots(self):
        return self.slots
        pass

    def _onActivate(self):
        super(HOGInventoryImage, self)._onActivate()
        self.setupPoints()
        pass

    def _onDeactivate(self):
        super(HOGInventoryImage, self)._onDeactivate()
        self.object.setItemsCount(None)

        self.__cleanup()
        pass

    def __cleanup(self):
        for slot in self.slots:
            slot.release()
            pass

        self.slots = []

        return True
        pass

    def setupPoints(self):
        slotCount = self.getSlotCount()
        for index in range(slotCount):
            slot = HOGInventorySlot()
            self.slots.append(slot)
            pass
        pass

    def getSlotByName(self, name):
        for slot in self.slots:
            if slot.getHOGItemName() is name:
                return slot
                pass
            pass

        return None
        pass

    def findNewSlot(self):
        for slot in self.slots:
            if slot.isEmpty() is True:
                return slot
                pass
            pass
        return None
        pass

    def _updateFindItems(self, list):
        if len(list) == 0:
            return
            pass

        for listNames in list:
            for name in listNames:
                self.__updateHOGSlot(name)
                pass
            pass
        pass

    def _appendFindItems(self, id, itemList):
        for name in itemList:
            self.__updateHOGSlot(name)
            pass
        pass

    def __updateHOGSlot(self, name):
        slot = self.findNewSlot()
        if slot is None:
            return
            pass

        slotId = self.slots.index(slot)

        enigmaName = EnigmaManager.getEnigmaName(self.HOG)
        items = HOGManager.getHOGItems(enigmaName)
        for item in items:
            if item.itemName == name:
                hog_item = item
                break
            pass

        slotType = hog_item.getSlot()
        movieName = self.Slots[slotType]

        Movie_Slot = self.object.generateObject("%s%d" % (movieName, slotId), movieName)
        Movie_Slot.setEnable(True)
        Movie_SlotEntity = Movie_Slot.getEntity()

        MovieSlotPointsObject = self.object.getObject("Movie_SlotPointsImage")
        MovieSlotPointsEntity = MovieSlotPointsObject.getEntity()

        id = "slot_%d" % (slotId)
        CurrentSlot = MovieSlotPointsEntity.getMovieSlot(id)
        CurrentSlot.addChild(Movie_SlotEntity)

        Movie_Slot.setPosition((0, 0))

        slot.setHOGItemName(name)
        slot.setMovie(Movie_Slot)

        EnigmaName = EnigmaManager.getEnigmaName(self.HOG)

        item = HOGImageManager.getHOGInventoryImage(EnigmaName, name)

        itemEntity = item.getEntity()
        sprite = itemEntity.getSprite()
        center = sprite.getLocalImageCenter()
        offset = (0, 0)

        if self.inventoryImageMaxSize:
            orgSize = sprite.getSurfaceSize()
            size = Utils.calculateBoundedSize(orgSize, self.inventoryImageMaxSize)
            sprite.setSpriteSize(size)
            offset = ((orgSize[0] - size[0]) / 2.0, (orgSize[1] - size[1]) / 2.0)
            pass

        if self.inventoryImageColor:
            sprite.disableTextureColor(True)
            sprite.setLocalColor(self.inventoryImageColor)
            pass

        sprite.setOrigin((center[0] - offset[0], center[1] - offset[1]))

        slot.setItem(item)
        pass

    def _updateItemsAllCount(self, value):
        self.__updateItemsCount()
        pass

    def __updateItemsCount(self):
        if self.object.hasObject("Text_Count") is False:
            return
            pass
        Text_Count = self.object.getObject("Text_Count")
        if self.ItemsCount is None:
            Text_Count.setEnable(False)
            return
            pass
        Text_Count.setTextID("ID_HOGImageCount")
        Text_Count.setTextArgs(len(self.FoundItems), self.ItemsCount)
        Text_Count.setEnable(True)
        pass

    def _updateFoundItems(self, list):
        if len(list) == 0:
            return
            pass
        if len(self.slots) == 0:
            self.setupPoints()
            pass
        for name in list:
            self._updateFound(name)
            pass
        pass

    def _appendFoundItems(self, id, value):
        self._updateFound(value)
        pass

    def _updateFound(self, value):
        slot = self.getSlotByName(value)
        if slot is None:
            return
            pass

        Notification.notify(Notificator.onHOGInventoryFoundItem, value, True)
        slot.release()
        pass

    pass
