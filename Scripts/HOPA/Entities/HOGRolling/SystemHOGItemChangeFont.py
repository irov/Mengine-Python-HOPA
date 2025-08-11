from Foundation.DefaultManager import DefaultManager
from Foundation.System import System
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGManager import HOGManager

class SystemHOGItemChangeFont(System):
    def _onParams(self, params):
        super(SystemHOGItemChangeFont, self)._onParams(params)
        self.onEnigmaPlayObserver = None
        self.onEnigmaCompleteObserver = None
        self.onEnigmaStopObserver = None
        self.ItemEnablingObserver = None
        self.onHOGInventoryAppendItem = None
        self.EnigmaName = None
        self.items = {}
        pass

    def _onSave(self):
        return self.items
        pass

    def _onLoad(self, data_save):
        self.items = data_save
        pass

    def _onRun(self):
        self.onEnigmaPlayObserver = Notification.addObserver(Notificator.onEnigmaStart, self.__onEnigmaPlay)
        self.onEnigmaStopObserver = Notification.addObserver(Notificator.onEnigmaStop, self.__onEnigmaStop)
        self.onEnigmaCompleteObserver = Notification.addObserver(Notificator.onEnigmaComplete, self.__onEnigmaComplete)
        return True
        pass

    def __onEnigmaPlay(self, enigmaObject):
        EnigmaName = EnigmaManager.getEnigmaName(enigmaObject)
        Enigma = EnigmaManager.getEnigma(EnigmaName)
        EnigmaType = Enigma.getType()
        if EnigmaType != "HOGRolling":
            return False
            pass

        self.EnigmaName = EnigmaName
        self.ItemEnablingObserver = Notification.addObserver(Notificator.onItemChangeEnable, self.__onItemChangeEnable)
        self.onHOGInventoryAppendItem = Notification.addObserver(Notificator.onHOGInventoryAppendItem, self.__onHOGInventoryAppendItem)

        return False
        pass

    def __onHOGInventoryAppendItem(self, hogItemName):
        if self.EnigmaName in self.items.keys():
            enigmaItems = self.items[self.EnigmaName]
            if hogItemName in enigmaItems:
                self.__changeFont(hogItemName)
                pass
            pass
        return False
        pass

    def __onItemChangeEnable(self, objectItem):
        if self.EnigmaName is None:
            return False
            pass

        enable = objectItem.getEnable()
        if enable is False:
            return False
            pass

        currentItemName = objectItem.getName()

        hogItems = HOGManager.getHOGItems(self.EnigmaName)

        for hogItem in hogItems:
            if hogItem.objectName == currentItemName:
                self.__changeFont(hogItem.itemName)
                self.items.setdefault(self.EnigmaName, []).append(hogItem.itemName)
                break
            pass
        return False
        pass

    def __changeFont(self, hogItemName):
        font = DefaultManager.getDefault("HogEnableItemFont", None)
        if font is None:
            return
            pass

        HOGInventory = HOGManager.getInventory(self.EnigmaName)
        if HOGInventory.isActive() is False:
            return
            pass

        InventoryEntity = HOGInventory.getEntity()
        textID = HOGManager.getHOGItemTextID(self.EnigmaName, hogItemName)
        slot = InventoryEntity.findSlot(textID)
        if slot is None:
            return
            pass

        Field = slot.getTextField()
        Field.setFontName(font)
        pass

    def __onEnigmaStop(self, enigmaObject):
        EnigmaName = EnigmaManager.getEnigmaName(enigmaObject)
        Enigma = EnigmaManager.getEnigma(EnigmaName)
        EnigmaType = Enigma.getType()
        if EnigmaType != "HOGRolling":
            return False
            pass

        self.HOG = None
        Notification.removeObserver(self.ItemEnablingObserver)
        Notification.removeObserver(self.onHOGInventoryAppendItem)
        return False
        pass

    def __onEnigmaComplete(self, enigmaObject):
        EnigmaName = EnigmaManager.getEnigmaName(enigmaObject)
        if EnigmaName in self.items.keys():
            del self.items[EnigmaName]
            pass
        return False
        pass

    def _onStop(self):
        Notification.removeObserver(self.onEnigmaPlayObserver)
        Notification.removeObserver(self.onEnigmaCompleteObserver)
        Notification.removeObserver(self.onEnigmaStopObserver)
        self.onEnigmaPlayObserver = None
        self.onEnigmaCompleteObserver = None
        self.onEnigmaStopObserver = None
        self.ItemEnablingObserver = None
        self.onHOGInventoryAppendItem = None
        self.EnigmaName = None
        self.items = {}
