from Foundation.DefaultManager import DefaultManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasInventorySlotsMoveLeft(TaskAlias):
    def _onParams(self, params):
        super(AliasInventorySlotsMoveLeft, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.SpeedFactor = params.get("SpeedFactor", 1)
        self.StartSlotIndex = params.get("StartSlotIndex", 0)
        self.Exceptions = params.get("Exceptions", [])
        self.genMovies = []
        pass

    def __destroyGenMovies(self):
        for movie in self.genMovies:
            movie.onDestroy()
            pass

        self.genMovies = []
        pass

    def attachSlotLeftRemove(self, leftSlot):
        movie = self.Inventory.getObject("Movie_SlotLeftRemove")

        if leftSlot.item is None or leftSlot.item in self.Exceptions:
            return None, None
            pass

        invItem = leftSlot.returnItem()
        if invItem is None:
            return None, None
            pass

        invItemEntity = invItem.getEntity()
        invItemEntityNode = invItem.getEntityNode()
        movieEntity = movie.getEntity()
        movieSlot = movieEntity.getMovieSlot("point")

        movieSlot.addChild(invItemEntityNode)

        return movie, invItem
        pass

    def attachSlotRightAdd(self, newItemNum):
        InventoryItems = self.Inventory.getParam("InventoryItems")
        SlotCount = self.Inventory.getSlotCount()
        if len(InventoryItems) <= newItemNum:
            return None, None
            pass

        invItem = InventoryItems[newItemNum]
        if invItem is None or invItem in self.Exceptions:
            return None, None
            pass

        movie = self.Inventory.getObject("Movie_SlotRightAdd")

        invItem.setPosition((0, 0))
        invItem.setEnable(True)

        invItemEntity = invItem.getEntity()
        invItemEntityNode = invItem.getEntityNode()
        movieEntity = movie.getEntity()
        movieSlot = movieEntity.getMovieSlot("point")

        movieSlot.addChild(invItemEntityNode)

        return movie, invItem
        pass

    def attachSlot(self, slot):
        slotId = slot.slotId

        if slot.item is None or slot.item in self.Exceptions:
            return None, None
            pass

        invItem = slot.returnItem()

        if invItem is None:
            return None, None
            pass

        movie = self.Inventory.generateObject("Movie_SlotLeft%d" % (slotId,), "Movie_SlotLeft")
        movie.setPosition((0, 0))

        pointSlot = slot.getPoint()

        invItemEntity = invItem.getEntity()
        invItemEntityNode = invItem.getEntityNode()
        movieEntity = movie.getEntity()
        movieEntityNode = movie.getEntityNode()
        movieSlot = movieEntity.getMovieSlot("point")

        movieSlot.addChild(invItemEntityNode)
        pointSlot.addChild(movieEntityNode)

        self.genMovies.append(movie)

        return movie, invItem
        pass

    def _onGenerate(self, source):
        InventoryEntity = self.Inventory.getEntity()
        slots = InventoryEntity.getSlots()

        for slot in slots:
            slot.hotspot.disable()
            pass

        InventoryItems = self.Inventory.getParam("InventoryItems")
        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        SlotCount = self.Inventory.getParam("SlotCount")

        InventoryItemsCount = len(InventoryItems)

        activeSlots = min(len(InventoryItems) - CurrentSlotIndex, SlotCount)

        tempMovies = []

        NewSlotIndex = CurrentSlotIndex

        if activeSlots >= 1 and InventoryItemsCount > SlotCount:
            leftSlot = slots[0]
            movieLeft, leftInvItem = self.attachSlotLeftRemove(leftSlot)

            if leftInvItem is not None:
                NewSlotIndex = CurrentSlotIndex + 1
                pass

            tempMovies.append(movieLeft)
            pass

        if activeSlots >= 1:
            idleInvItems = []
            idleInvMovies = []
            lastSlotIndex = min(activeSlots, SlotCount)
            if InventoryItemsCount > SlotCount:
                lastSlotIndex -= 1
                pass
            if self.StartSlotIndex == 0:
                startIndex = 1
                pass
            else:
                startIndex = self.StartSlotIndex
                pass

            if startIndex == lastSlotIndex + 1 == 1:
                slot = slots[1]
                movie, invItem = self.attachSlot(slot)

                tempMovies.append(movie)
                idleInvItems.append(invItem)
                idleInvMovies.append(movie)
                pass
            else:
                for slot in slots[startIndex: lastSlotIndex + 1]:
                    movie, invItem = self.attachSlot(slot)

                    tempMovies.append(movie)
                    idleInvItems.append(invItem)
                    idleInvMovies.append(movie)
                    pass
                pass
            pass

        rightInvItem = None
        if activeSlots == SlotCount and InventoryItemsCount >= CurrentSlotIndex + SlotCount:
            newItemNum = CurrentSlotIndex + SlotCount  # for scroll
            if self.StartSlotIndex != 0:
                newItemNum -= 1  # for remove item
                pass

            movieRight, rightInvItem = self.attachSlotRightAdd(newItemNum)

            tempMovies.append(movieRight)
            pass

        moviesCount = len(tempMovies)
        with source.addParallelTask(moviesCount) as tc_movies:
            for tc_movie, movie in zip(tc_movies, tempMovies):
                if movie is None:
                    continue
                    pass

                DefaultMoveTime = DefaultManager.getDefaultFloat("InventorySlotsMoveTime", 0.5)
                DefaultMoveTime *= 1000  # speed fix
                DefaultSpeedFactor = 1  # * 0.001  # speed fix

                MovieDuration = movie.getDuration()

                if MovieDuration != DefaultMoveTime:
                    DefaultSpeedFactor = MovieDuration / DefaultMoveTime
                    pass

                speedFactor = DefaultSpeedFactor * self.SpeedFactor
                tc_movie.addTask("TaskMoviePlay", Movie=movie, SpeedFactor=speedFactor, DefaultSpeedFactor=1)
                pass
            pass

        if activeSlots >= 1 and InventoryItemsCount > SlotCount:
            if leftInvItem is not None:
                leftInvItemEntity = leftInvItem.getEntity()
                leftInvItemEntityNode = leftInvItem.getEntityNode()
                source.addTask("TaskNodeRemoveFromParent", Node=leftInvItemEntityNode)
                pass
            pass

        if activeSlots >= 1:
            for invItem, tempMovie in zip(idleInvItems, idleInvMovies):
                if invItem is None or tempMovie is None:
                    continue
                    pass

                invItemEntity = invItem.getEntity()
                invItemEntityNode = invItem.getEntityNode()
                tempMovieEntity = tempMovie.getEntity()
                tempMovieEntityNode = tempMovie.getEntityNode()
                source.addTask("TaskNodeRemoveFromParent", Node=invItemEntityNode)
                source.addTask("TaskNodeRemoveFromParent", Node=tempMovieEntityNode)
                pass
            pass

        if activeSlots == SlotCount and InventoryItemsCount > CurrentSlotIndex + SlotCount:
            if rightInvItem is not None:
                rightInvItemEntityNode = rightInvItem.getEntityNode()
                source.addTask("TaskNodeRemoveFromParent", Node=rightInvItemEntityNode)
                pass
            pass

        source.addFunction(InventoryEntity.removeSlots)
        source.addFunction(InventoryEntity.setupPoints)
        source.addTask("TaskInventoryCurrentSlotIndex", Inventory=self.Inventory, Value=NewSlotIndex)
        source.addFunction(InventoryEntity.updateSlots)
        source.addFunction(self.__destroyGenMovies)
        source.addNotify(Notificator.onInventorySlotsShiftEnd)
