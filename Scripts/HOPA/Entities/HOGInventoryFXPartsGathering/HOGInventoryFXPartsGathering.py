from Foundation.Task.Semaphore import Semaphore
from HOPA.Entities.InventoryBase import InventoryBase
from HOPA.HOGManager import HOGManager


InventoryBase = Mengine.importEntity("InventoryBase")


class HOGInventorySlot(object):
    HOG = None
    Groups = {}

    @staticmethod
    def setGroups(groups):
        HOGInventorySlot.Groups = {}
        for group in groups:
            HOGInventorySlot.Groups[group] = dict(items_count=0, parts=[], movie=None,
                                                  semaphore=Semaphore(0, group.name))

    def __init__(self, item):
        self.item = item
        self.item_Movie = HOGInventorySlot.HOG.getObject('Movie2_' + item.name)
        self.group = item.group
        self.groupMovie = HOGInventorySlot.HOG.getObject('Movie2_' + self.group.movieName)
        HOGInventorySlot.Groups[self.group]["parts"].append(self.item_Movie)
        HOGInventorySlot.Groups[self.group]["movie"] = self.groupMovie
        self.node = self.item_Movie.getEntityNode()

    def getPoint(self):
        # box = self.node.getBoundingBox()
        # return Mengine.vec2f((box.minimum.x + box.maximum.x)/2, (box.minimum.y + box.maximum.y)/2)
        slot = self.item_Movie.getMovieSlot("slot")
        if slot is None:
            node = self.item_Movie.getEntityNode()
            pos = node.getWorldPosition()
        else:
            pos = slot.getWorldPosition()
        return pos

    def getGroup(self):
        return self.group

    def getPart_Movie(self):
        return self.item_Movie

    def getMovie(self):
        return self.groupMovie

    def getNode(self):
        return self.node

    def getSemaphore(self):
        return HOGInventorySlot.Groups[self.group]['semaphore']

    def incref(self):
        HOGInventorySlot.Groups[self.group]['items_count'] += 1

    def isGathered(self):
        return HOGInventorySlot.Groups[self.group]['items_count'] == self.group.items_amount

    @staticmethod
    def getSemaphores():
        return (group['semaphore'] for group in HOGInventorySlot.Groups.itervalues())

    @staticmethod
    def isAllGathered():
        for key, group in HOGInventorySlot.Groups.iteritems():
            if group['items_count'] < key.items_amount:
                return False
        return True

    @staticmethod
    def disableGroupsMovies():
        for group in HOGInventorySlot.Groups.itervalues():
            group['movie'].setEnable(False)

    @staticmethod
    def disableItemMovies(group):
        movies = HOGInventorySlot.Groups[group]['parts']
        for elem in movies:
            elem.setEnable(False)


class HOGInventoryFXPartsGathering(InventoryBase):
    @staticmethod
    def declareORM(Type):
        InventoryBase.declareORM(Type)

        Type.addAction(Type, "HOG", Update=HOGInventoryFXPartsGathering._updateHOG)
        Type.addActionActivate(Type, "FindItems",
                               Append=HOGInventoryFXPartsGathering._appendFindItems,
                               Update=HOGInventoryFXPartsGathering._updateFindItems)
        Type.addActionActivate(Type, "FoundItems",
                               Append=HOGInventoryFXPartsGathering._appendFoundItems,
                               Update=HOGInventoryFXPartsGathering._updateFoundItems)

    def __init__(self):
        super(HOGInventoryFXPartsGathering, self).__init__()

        self.slots = None
        self.movie_gathering = None

    def _onActivate(self):
        super(HOGInventoryFXPartsGathering, self)._onActivate()
        # print '%s._onActivate():' % type(self).__name__
        pass

    def _onDeactivate(self):
        super(HOGInventoryFXPartsGathering, self)._onDeactivate()

    def _updateHOG(self, hog):
        HOGInventorySlot.HOG = hog
        if hog is not None:
            self.movie_gathering = hog.getObject('Movie2_Gathering')

            self.addChild(self.movie_gathering.getEntityNode())
            self.movie_gathering.setEnable(False)

    def getMovieGathering(self):
        return self.movie_gathering

    def getSlotByName(self, name):
        for slot in self.slots:
            if slot.item.name == name:
                return slot

        return None

    def _appendFindItems(self, id, itemName):
        pass

    def _updateFindItems(self, itemsList):
        items = []
        groups = set()
        for itemName in itemsList:
            item = HOGManager.getHOGItem(self.HOG.getEnigmaName(), itemName)
            items.append(item)
            groups.add(item.group)

        HOGInventorySlot.setGroups(groups)

        self.slots = []
        for item in items:
            self.slots.append(HOGInventorySlot(item))
            self.addChild(self.HOG.getObject('Movie2_' + item.name).getEntityNode())

        for group in groups:
            Movie = self.HOG.getObject('Movie2_' + group.movieName)
            node = Movie.getEntityNode()
            self.addChild(node)

    def _appendFoundItems(self, id, itemName):
        slot = self.getSlotByName(itemName)
        slot.incref()
        pass

    def _updateFoundItems(self, itemList):
        for item in itemList:
            slot = self.getSlotByName(item)
            slot.incref()
        pass
