from Foundation.DefaultManager import DefaultManager
from Foundation.TaskManager import TaskManager
from HOPA.HOGManager import HOGManager
from Notification import Notification


Enigma = Mengine.importEntity("Enigma")


class HOGFXPartsGathering(Enigma):
    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)

        Type.addAction(Type, "FoundItems",
                       Append=Type._appendFoundItems,
                       Update=Type._updateFoundItems)

    def __init__(self):
        super(HOGFXPartsGathering, self).__init__()

        self.ItemsGroup = None
        self.HOGInventory = None
        self.items = []
        self.completeCheck = False
        self.isHOG = True

    def _onActivate(self):
        super(HOGFXPartsGathering, self)._onActivate()

        self.HOGInventory = HOGManager.getInventory(self.EnigmaName)
        self.HOGInventory.setParams(HOG=self.object)

        self.items = HOGManager.getHOGItems(self.EnigmaName)
        for item in self.items:
            self.HOGInventory.appendParam('FindItems', item.name)
        for elem in self.FoundItems:
            self.HOGInventory.appendParam('FoundItems', elem)

        HOGItemsInDemon = DefaultManager.getDefaultBool("HOGItemsInDemon", True)

        if HOGItemsInDemon is True:
            self.ItemsGroup = self.object
            return
            pass

        self.ItemsGroup = self.object.getGroup()

    def Setup(self):
        for item in self.items:
            item_Movie = self.object.getObject('Movie2_' + item.name)
            item_Group_Movie = self.object.getObject('Movie2_' + item.group.movieName)
            item_Movie.setEnable(True)
            item_Group_Movie.setEnable(False)

    def _playEnigma(self):
        self.Setup()
        self._AllWork()

    def _AllWork(self):
        for item in self.items:
            with TaskManager.createTaskChain(Name="HOGFindItem%s" % item.name, Group=self.ItemsGroup) as tc:
                if item.name not in self.HOGInventory.getFoundItems():
                    tc.addTask("AliasHOGFXPartsGatheringFindItem", HOG=self.object,
                               HOGItemName=item.name, EnigmaName=self.EnigmaName)
                else:
                    tc.addTask("TaskDummy")

    def _appendFoundItems(self, id, itemName):
        self.HOGInventory.appendParam("FoundItems", itemName)

    def _updateFoundItems(self, itemList):
        pass

    def _restoreEnigma(self):
        self._AllWork()

    def _resetEnigma(self):
        self._playEnigma()

    def _stopEnigma(self):
        Notification.notify(Notificator.onHOGStop, self.object)

    def _skipEnigma(self):
        Notification.notify(Notificator.onHOGSkip, self.object)

    def _onDeactivate(self):
        super(HOGFXPartsGathering, self)._onDeactivate()

        for item in self.items:
            if TaskManager.existTaskChain("HOGFindItem%s" % item.name) is True:
                TaskManager.cancelTaskChain("HOGFindItem%s" % item.name)

        self.HOGInventory.setParams(FindItems=[], FoundItems=[], HOG=None)
        self.items = []
