from Foundation.DefaultManager import DefaultManager
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.Entities.InventoryBase import InventoryBase
from HOPA.HOGManager import HOGManager

InventoryBase = Mengine.importEntity("InventoryBase")

HOGROLLING_MOVIE_SLOT_TEXTALIAS = "$text"

class HOGInventorySlot(object):
    def __init__(self):
        self.textID = None
        self.count = 0
        self.found = False
        self.movie = None
        self.hogItemName = []

    def appendHOGItemName(self, name):
        self.hogItemName.append(name)

    def isEmpty(self):
        return self.textID is None

    def getHOGItemNames(self):
        return self.hogItemName

    def setMovie(self, movie):
        if self.movie is not None:
            self.movie.onDestroy()

        self.movie = movie

    def getMovie(self):
        return self.movie

    def getTextID(self):
        return self.textID

    def setTextID(self, textID):
        self.textID = textID

    def incref(self):
        self.count += 1

    def decref(self):
        self.count -= 1

        if self.count == 0:
            self.found = True

    def isFound(self):
        return self.found

    def getPoint(self):
        return self.movie.getEntityNode().getWorldPosition()

    def getTextField(self):
        return self.movie.getEntity().getMovieText(HOGROLLING_MOVIE_SLOT_TEXTALIAS)

    def getCount(self):
        return self.count

    def release(self):
        if self.movie is not None:
            self.movie.onDestroy()
            self.movie = None

        self.textID = None
        self.count = 0
        self.found = False
        self.movie = None
        self.hogItemName = []


class HOGInventoryRolling(InventoryBase):

    @staticmethod
    def declareORM(Type):
        InventoryBase.declareORM(Type)

        Type.addAction(Type, "SlotCount")
        Type.addAction(Type, "ItemsCount")

        Type.addAction(Type, "HOG")
        Type.addActionActivate(Type, "FindItems",
                               Append=HOGInventoryRolling._appendFindItems,
                               Update=HOGInventoryRolling._updateFindItems)
        Type.addActionActivate(Type, "FoundItems",
                               Append=HOGInventoryRolling._appendFoundItems,
                               Update=HOGInventoryRolling._updateFoundItems)

    def __init__(self):
        super(HOGInventoryRolling, self).__init__()

        self.slots = []
        self.slot_appear_time = DefaultManager.getDefaultFloat("DefaultHOGInventoryRollingSlotAppearTime", 200.0)

    def getSlotCount(self):
        return self.SlotCount

    def getSlots(self):
        return self.slots

    def _onPreparation(self):
        super(HOGInventoryRolling, self)._onPreparation()

        if _DEVELOPMENT:
            if not self.object.hasObject("Movie2_SlotPoints"):
                Trace.log("Entity", 0, "%s HOGInventoryRolling missed Movie2_SlotPoints " % self.object.getGroupName())

            if not self.object.hasPrototype("Movie2_Slot"):
                Trace.log("Entity", 0, "%s HOGInventoryRolling missed prototype Movie2_Slot" % self.object.getGroupName())

            if not self.object.hasPrototype("Movie2_CheckMark"):
                Trace.log("Entity", 0, "%s HOGInventoryRolling missed prototype Movie2_CheckMark" % self.object.getGroupName())

            if not self.object.hasPrototype("Movie2_ItemTips"):
                Trace.log("Entity", 0, "%s HOGInventoryRolling missed prototype Movie2_ItemTips" % self.object.getGroupName())

        slots_movie = self.object.getObject("Movie2_SlotPoints")
        movie_slots = slots_movie.getSlots()
        if movie_slots == False:
            Trace.log("Entity", 0, "HOGInventoryRolling Movie2_SlotPoints has zero slots!!! please add slot:slot_0, ... slot:slot_n")
            return

        self.object.setSlotCount(len(movie_slots))

    def _onActivate(self):
        super(HOGInventoryRolling, self)._onActivate()
        if len(self.slots) == 0:
            self.setupPoints()

    def _onDeactivate(self):
        super(HOGInventoryRolling, self)._onDeactivate()

        self.object.setItemsCount(None)

        self.__cleanup()

    def __cleanup(self):
        for slot in self.slots:
            slot.release()

        self.slots = []

        return True

    def setupPoints(self):
        slotCount = self.getSlotCount()
        for index in range(slotCount):
            slot = HOGInventorySlot()
            self.slots.append(slot)

    def getSlotByName(self, name):
        for slot in self.slots:
            slotItemNames = slot.getHOGItemNames()
            if name in slotItemNames:
                return slot

    def _updateFindItems(self, list):
        if len(list) == 0:
            return

        for listNames in list:
            for name in listNames:
                self.__updateHOGSlot(name)

    def _appendFindItems(self, id, listNames):
        for name in listNames:
            self.__updateHOGSlot(name)

    def __updateHOGSlot(self, name):
        if self.HOG is None:
            return

        if self.HOG.getPlay() is False:
            return

        enigma_name = EnigmaManager.getEnigmaName(self.HOG)
        text_id = HOGManager.getHOGItemTextID(enigma_name, name)
        slot = self.findSlot(text_id)

        hog_item = HOGManager.getHOGItem(enigma_name, name)

        if slot is not None:
            slot.incref()
            slot.appendHOGItemName(name)
            Notification.notify(Notificator.onHOGInventoryAppendItem, name)
            return

        slot = self.findNewSlot()
        if slot is None:
            return

        slot_id = self.slots.index(slot)
        movie_slot = self.object.generateObject("Movie2_Slot_%s" % slot_id, "Movie2_Slot")

        movie_slot_entity = movie_slot.getEntityNode()

        """ Set text """
        alias_env = movie_slot_entity.getName()
        movie_slot.setTextAliasEnvironment(alias_env)
        Mengine.setTextAlias(alias_env, HOGROLLING_MOVIE_SLOT_TEXTALIAS, text_id)

        movie_slot.setEnable(True)

        movie_slot_points = self.object.getObject("Movie2_SlotPoints")

        movie_slot_points_entity = movie_slot_points.getEntity()

        slot_name = hog_item.getSlotBind()
        if slot_name is None:
            slot_name = "slot_{}".format(slot_id)

        current_slot = movie_slot_points_entity.getMovieSlot(slot_name)
        current_slot.addChild(movie_slot_entity)

        movie_slot.setPosition((0.0, 0.0))

        slot.appendHOGItemName(name)
        slot.setMovie(movie_slot)
        slot.setTextID(text_id)
        slot.incref()

        # todo: dirty hack, need separate state for this in inv slot FixMe
        with TaskManager.createTaskChain() as tc:
            tc.addTask("AliasObjectAlphaTo", Object=movie_slot, Time=self.slot_appear_time, From=0.0, To=1.0)

        Notification.notify(Notificator.onHOGInventoryAppendItem, name)

    def _createTextField(self):
        textField = Mengine.createNode("TextField")
        textField.setHorizontalCenterAlign()
        textField.setVerticalCenterAlign()
        ### fix size

        self.addChild(textField)

        return textField

    def findSlot(self, textID):
        for slot in self.slots:
            slotTextID = slot.getTextID()
            if slotTextID is None:
                continue
            if slotTextID == textID:
                return slot

    def findNewSlot(self):
        for slot in self.slots:
            if slot.isEmpty() is True:
                return slot

    def _updateFoundItems(self, list):
        if len(list) == 0:
            return

        if len(self.slots) == 0:
            self.setupPoints()

        for name in list:
            self._updateFound(name)

    def _appendFoundItems(self, id, value):
        self._updateFound(value)

    def _updateFound(self, value):
        slot = self.getSlotByName(value)
        if slot is None:
            return

        slot.decref()

        Notification.notify(Notificator.onHOGInventoryFoundItem, value, slot.isFound())

        if slot.getCount() == 0:
            slot.release()
