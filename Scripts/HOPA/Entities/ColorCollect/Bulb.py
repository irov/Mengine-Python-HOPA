from Foundation.TaskManager import TaskManager


class Bulb(object):
    END_SLOT_ID = 5
    BEGIN_SLOT_ID = 1

    def __init__(self, enigma, name, dataPack, itemsData, size):
        self.enigmaObject = enigma
        self.name = name
        self.movie = None
        self.itemsBySlots = {}
        self.size = size
        self.hasItemToAttach = False
        self.preparation(dataPack, itemsData)
        pass

    def getName(self):
        return self.name
        pass

    def preparation(self, data, itemsData):
        itemNames = data.getItemNames()
        if len(itemNames) > self.size:
            self.hasItemToAttach = True
            pass

        movieName = data.getMovieName()
        self.movie = self.enigmaObject.getObject(movieName)
        self.movie.setEnable(True)

        for itemName in itemNames:
            slotID = itemsData[itemName]

            MovieEntity = self.movie.getEntity()
            MovieSlot = MovieEntity.getMovieSlot("%s" % (slotID))

            itemObject = self.enigmaObject.getObject(itemName)
            itemObject.setPosition((0, 0))

            itemEntityNode = itemObject.getEntityNode()
            MovieSlot.addChild(itemEntityNode)
            self.itemsBySlots[slotID] = itemObject
        pass

    def isItemToAttach(self):
        return self.hasItemToAttach
        pass

    def removeAttachItem(self):
        itemObject = self.itemsBySlots[Bulb.END_SLOT_ID]
        self.hasItemToAttach = False
        del self.itemsBySlots[Bulb.END_SLOT_ID]
        return itemObject
        pass

    def attachItemToEnd(self, itemObject):
        MovieEntity = self.movie.getEntity()
        MovieSlot = MovieEntity.getMovieSlot("%s" % (Bulb.END_SLOT_ID))
        itemObject.setEnable(True)
        itemObject.setPosition((0, 0))
        itemEntityNode = itemObject.getEntityNode()
        MovieSlot.addChild(itemEntityNode)
        self.itemsBySlots[Bulb.END_SLOT_ID] = itemObject
        self.hasItemToAttach = True
        pass

    def attachItemToBegin(self, itemObject):
        MovieEntity = self.movie.getEntity()
        MovieSlot = MovieEntity.getMovieSlot("%s" % (Bulb.BEGIN_SLOT_ID))
        itemObject.setEnable(True)
        itemObject.setPosition((0, 0))
        itemEntityNode = itemObject.getEntityNode()
        MovieSlot.addChild(itemEntityNode)
        self.itemsBySlots[Bulb.BEGIN_SLOT_ID] = itemObject
        self.hasItemToAttach = True
        pass

    def updateMovie(self):
        with TaskManager.createTaskChain() as tc:
            tc.addTask("TaskMoviePlay", Movie=self.movie)
            tc.addTask("TaskFunction", Fn=self.refreshValues)
            tc.addTask("TaskMovieLastFrame", Movie=self.movie, Value=False)
            tc.addTask("TaskFunction", Fn=self.bulbAction)
            pass
        pass

    def bulbAction(self):
        self.enigmaObject.setBulbAction(True)
        pass

    def refreshValues(self):
        for slotID in reversed(self.itemsBySlots.keys()):
            currentItem = self.itemsBySlots[slotID]
            newSlotID = slotID + 1
            MovieEntity = self.movie.getEntity()
            MovieSlot = MovieEntity.getMovieSlot("%s" % (newSlotID))
            itemEntityNode = currentItem.getEntityNode()
            MovieSlot.addChild(itemEntityNode)
            self.itemsBySlots[newSlotID] = currentItem
            pass
        del self.itemsBySlots[Bulb.BEGIN_SLOT_ID]
        pass

    def finalise(self):
        for item in self.itemsBySlots.values():
            itemEntity = item.getEntity()
            itemEntity.removeFromParent()
            pass
        pass

    def getItems(self):
        items = []
        for slot, item in self.itemsBySlots.iteritems():
            if slot == Bulb.END_SLOT_ID:
                continue
                pass
            name = item.getName()
            items.append(name)
            pass
        return items
