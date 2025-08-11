from HOPA.HOGManager import HOGManager

Enigma = Mengine.importEntity("Enigma")

class HOG2(Enigma):
    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addActionActivate(Type, "FoundItems",
                               Append=HOG2._appendFoundItems,
                               Update=HOG2._updateFoundItems)
        Type.addActionActivate(Type, "PrepareItems",
                               Update=HOG2._updatePrepareItems,
                               Append=HOG2._appendPrepareItems)
        pass

    def __init__(self):
        super(HOG2, self).__init__()
        self.HOGInventory = None
        # this is minihog so:
        self.isMiniHOG = True

    def _updateFoundItems(self, list):
        for item in list:
            if item not in self.HOGInventory.getFoundItems():
                self.HOGInventory.appendParam("FoundItems", item)
        self.HOGInventory.setItemsCount(len(self.HOGItems))

    def _appendFoundItems(self, id, name):
        Notification.notify(Notificator.onAppendFoundItemsHOG2)
        self.HOGInventory.delParam("FindItems", [name, ])
        self.HOGInventory.appendParam("FoundItems", name)
        self.object.delParam("PrepareItems", name)

    def _updatePrepareItems(self, list):
        for item in list:
            if item in self.FoundItems:
                continue
            if [item, ] not in self.HOGInventory.getFindItems():
                self.HOGInventory.appendParam("FindItems", [item, ])
        pass

    def _appendPrepareItems(self, key, name):
        self.HOGInventory.appendParam("FindItems", [name, ])

        pass

    def _onPreparation(self):
        super(HOG2, self)._onPreparation()

    def _onActivate(self):
        super(HOG2, self)._onActivate()
        self.HOGInventory = HOGManager.getInventory(self.EnigmaName)
        self.HOGInventory.setEnable(True)
        self.HOGItems = HOGManager.getHOGItems(self.EnigmaName)
        self.HOGInventory.setParams(HOG=self.object, ItemsCount=len(self.HOGItems))
        pass

    def _playEnigma(self):
        pass

    def _restoreEnigma(self):
        self._playEnigma()
        pass

    def _stopEnigma(self):
        self.HOGInventory.setParams(FindItems=[], FoundItems=[], HOG=None)

        Notification.notify(Notificator.onHOGStop, self.object)
        pass

    def _pauseEnigma(self):
        pass

    def _onDeactivate(self):
        super(HOG2, self)._onDeactivate()
        self.HOGInventory.setParams(FindItems=[], FoundItems=[], HOG=None)
        self.HOGInventory.setEnable(False)
