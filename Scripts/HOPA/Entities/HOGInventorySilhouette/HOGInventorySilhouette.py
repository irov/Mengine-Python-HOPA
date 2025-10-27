from Foundation.DefaultManager import DefaultManager
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.Entities.InventoryBase import InventoryBase
from HOPA.HOGManager import HOGManager


InventoryBase = Mengine.importEntity("InventoryBase")


class InventorySilhouetteSlot(object):
    def __init__(self, movieSlot):
        self.movieSlot = movieSlot

        self.hogItemName = None

        self.itemObject = None
        pass

    def isEmpty(self):
        return self.hogItemName is None

    def setHOGItemName(self, hogItemName):
        self.hogItemName = hogItemName

    def getItemObject(self):
        return self.itemObject

    def getHOGItemName(self):
        return self.hogItemName

    def attachItemObject(self, itemObject):
        if itemObject is None:
            return

        self.itemObject = itemObject

        size = self.itemObject.getEntity().getSize()
        newPosition = (size[0] * -0.5, size[1] * -0.5)

        self.itemObject.setPosition(newPosition)

        entityNode = itemObject.getEntityNode()

        self.movieSlot.addChild(entityNode)

    def deattachItemObject(self):
        if self.itemObject is None:
            return None
        itemObject = self.itemObject
        self.itemObject = None

        itemObject.returnToParent()
        return itemObject

    def getPoint(self):
        return self.movieSlot.getWorldPosition()
        pass

    def release(self):
        self.hogItemName = None

        if self.itemObject is not None:
            self.deattachItemObject()


class HOGInventorySilhouette(InventoryBase):

    def __init__(self):
        super(HOGInventorySilhouette, self).__init__()

        self.slots = []

    @staticmethod
    def declareORM(Type):
        InventoryBase.declareORM(Type)

        Type.addAction("HOG")

        Type.addAction("SlotCount")

        Type.addActionActivate("FindItems", Update=Type.__updateFindItems, Append=Type.__appendFindItems)
        Type.addActionActivate("FoundItems", Update=Type.__updateFoundItems, Append=Type.__appendFoundItems)

    def __updateFindItems(self, list):
        if len(list) == 0:
            return

        for itemName in list:
            self.__updateHOGSlot(itemName)

    def __appendFindItems(self, index, itemName):
        self.__updateHOGSlot(itemName)

    def __updateFoundItems(self, list):
        if len(list) == 0:
            return

        if len(self.slots) == 0:
            self.setupSlots()

        for itemName in list:
            self.__updateFound(itemName)

    def __appendFoundItems(self, index, itemName):
        self.__updateFound(itemName)

    def _onPreparation(self):
        super(HOGInventorySilhouette, self)._onPreparation()
        if self.object.hasObject("Movie2_SlotPoints"):
            self.Movie = self.object.getObject("Movie2_SlotPoints")
        elif self.object.hasObject("Movie_SlotPoints"):
            self.Movie = self.object.getObject("Movie_SlotPoints")
        elif _DEVELOPMENT is True:
            Trace.log("Entity", 0, "%s HOGInventorySilhouette missing Movie(2)_SlotPoints" % self.object.getGroupName())

        self.setupSlots()

    def setupSlots(self):
        slotCount = self.object.getSlotCount()

        for slotID in range(slotCount):
            movieSlot = self._getMovieSlot(slotID)
            slot = InventorySilhouetteSlot(movieSlot)

            self.slots.append(slot)

    def __updateHOGSlot(self, itemName):
        if self.HOG is None:
            return

        if self.HOG.getPlay() is False:
            return

        EnigmaName = EnigmaManager.getEnigmaName(self.HOG)

        hogItem = HOGManager.getHOGItem(EnigmaName, itemName)

        slot = self.findNewSlot()
        if slot is None:
            return

        itemObject = hogItem.getStoreObject()

        itemObject.setEnable(True)

        slot.attachItemObject(itemObject)

        slot.setHOGItemName(itemName)

        alpha_to_time = DefaultManager.getDefaultFloat("HOGItemAlphaToTime", 500.0)
        with TaskManager.createTaskChain() as tc:
            tc.addTask("AliasObjectAlphaTo", Object=itemObject, Time=alpha_to_time, From=0.0, To=1.0)

    def __updateFound(self, itemName):
        slot = self.getSlotByName(itemName)
        if slot is None:
            return

        slot.setHOGItemName(None)

        itemObject = slot.deattachItemObject()
        if itemObject is not None:
            itemObject.setEnable(False)

    def findSlot(self, itemName):
        for slot in self.slots:
            slotItemName = slot.getHOGItemName()
            if slotItemName is None:
                continue
            if slotItemName == itemName:
                return slot

        return None

    def findNewSlot(self):
        for slot in self.slots:
            if slot.isEmpty() is False:
                continue
            return slot
        return None

    def _getMovieSlot(self, slotID):
        slotName = "slot_{}".format(slotID)
        movieSlot = self.Movie.getMovieSlot(slotName)
        return movieSlot

    def getSlotByName(self, itemName):
        for slot in self.slots:
            slotItemName = slot.getHOGItemName()
            if itemName == slotItemName:
                return slot
        return None

    def _onDeactivate(self):
        super(HOGInventorySilhouette, self)._onDeactivate()

        self.__cleanup()

    def __cleanup(self):
        for slot in self.slots:
            itemObject = slot.deattachItemObject()
            if itemObject is not None:
                itemObject.setEnable(False)
            slot.release()

        self.slots = []
