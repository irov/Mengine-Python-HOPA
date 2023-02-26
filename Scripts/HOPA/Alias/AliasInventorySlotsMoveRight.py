from Foundation.DefaultManager import DefaultManager
from Foundation.Task.TaskAlias import TaskAlias

class AliasInventorySlotsMoveRight(TaskAlias):
    def _onParams(self, params):
        super(AliasInventorySlotsMoveRight, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.SpeedFactor = params.get("SpeedFactor", 1)
        self.Exceptions = params.get("Exceptions", ())
        self.genMovies = []
        pass

    def __destroyGenMovies(self):
        for movie in self.genMovies:
            movie.onDestroy()
            pass

        self.genMovies = []
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

        movie = self.Inventory.generateObject("Movie_SlotRight%d" % (slotId,), "Movie_SlotRight")
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

    def attachSlotRightRemove(self, leftSlot):
        if leftSlot.item is None or leftSlot.item in self.Exceptions:
            return None, None
            pass

        invItem = leftSlot.returnItem()
        if invItem is None:
            return None, None
            pass

        movie = self.Inventory.getObject("Movie_SlotRightRemove")

        invItemEntity = invItem.getEntity()
        invItemEntityNode = invItem.getEntityNode()
        movieEntity = movie.getEntity()
        movieSlot = movieEntity.getMovieSlot("point")

        movieSlot.addChild(invItemEntityNode)

        return movie, invItem
        pass

    def attachSlotLeftAdd(self, slot, newItemNum):
        InventoryItems = self.Inventory.getParam("InventoryItems")

        invItem = InventoryItems[newItemNum]
        if invItem is None or invItem in self.Exceptions:
            return None, None
            pass
        invItem.setPosition((0, 0))
        invItem.setEnable(True)

        movie = self.Inventory.getObject("Movie_SlotLeftAdd")

        invItemEntity = invItem.getEntity()
        invItemEntityNode = invItem.getEntityNode()
        movieEntity = movie.getEntity()
        movieSlot = movieEntity.getMovieSlot("point")

        movieSlot.addChild(invItemEntityNode)

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

        activeSlots = min(len(InventoryItems) - CurrentSlotIndex, SlotCount)

        tempMovies = []

        if activeSlots == SlotCount:
            rightSlot = slots[SlotCount - 1]
            movieRight, rightInvItem = self.attachSlotRightRemove(rightSlot)

            tempMovies.append(movieRight)
            pass

        if activeSlots > 0:
            idleInvItems = []
            idleInvMovies = []
            lastSlotIndex = min(activeSlots, SlotCount - 1) - 1
            for slot in slots[0:lastSlotIndex + 1]:
                movie, invItem = self.attachSlot(slot)

                tempMovies.append(movie)
                idleInvItems.append(invItem)
                idleInvMovies.append(movie)
                pass
            pass

        newItemNum = CurrentSlotIndex - 1
        movieLeft, leftInvItem = self.attachSlotLeftAdd(slot, newItemNum)
        tempMovies.append(movieLeft)

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
                tc_movie.addTask("TaskMoviePlay", Movie=movie, SpeedFactor=speedFactor, DefaultSpeedFactor=1)  # speed fix
                pass
            pass
        # source.addTask("TaskPrint", Value = "_______1")

        if activeSlots > 1:
            if leftInvItem is not None:
                leftInvItemEntity = leftInvItem.getEntity()
                leftInvItemEntityNode = leftInvItem.getEntityNode()
                source.addTask("TaskNodeRemoveFromParent", Node=leftInvItemEntityNode)
                pass
            pass

        if activeSlots > 2:
            for invItem, tempMovie in zip(idleInvItems, idleInvMovies):
                if invItem is None or tempMovie is None:
                    continue
                    pass

                invItemEntityNode = invItem.getEntityNode()
                tempMovieEntityNode = tempMovie.getEntityNode()
                source.addTask("TaskNodeRemoveFromParent", Node=invItemEntityNode)
                source.addTask("TaskNodeRemoveFromParent", Node=tempMovieEntityNode)
                pass
            pass

        if activeSlots == SlotCount:
            if rightInvItem is not None:
                rightInvItemEntityNode = rightInvItem.getEntityNode()
                source.addTask("TaskNodeRemoveFromParent", Node=rightInvItemEntityNode)
                pass
            pass

        NewSlotIndex = CurrentSlotIndex - 1

        source.addTask("TaskFunction", Fn=InventoryEntity.removeSlots)
        source.addTask("TaskFunction", Fn=InventoryEntity.setupPoints)
        source.addTask("TaskInventoryCurrentSlotIndex", Inventory=self.Inventory, Value=NewSlotIndex)
        source.addTask("TaskFunction", Fn=InventoryEntity.updateSlots)
        source.addTask("TaskFunction", Fn=self.__destroyGenMovies)
        source.addNotify(Notificator.onInventorySlotsShiftEnd)
        pass

    pass