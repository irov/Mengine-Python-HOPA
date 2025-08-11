from Foundation.TaskManager import TaskManager

from Field import Field
from PlumberManager import PlumberManager

Enigma = Mengine.importEntity("Enigma")

class Plumber(Enigma):
    def __init__(self):
        super(Plumber, self).__init__()
        self.Field = None
        self.movementMovies = {}
        self.cells = {}
        self.road = []
        self.data = None
        self.cellItems = {}
        self.startCell = None
        self.currentItemData = None
        self.wallsData = None
        self.safeCells = []
        self.itemsData = []
        self.listHeroes = {}
        self.movieConforms = {}
        self.buttons = {}
        pass

    def _onPreparation(self):
        super(Plumber, self)._onPreparation()
        self.movieConforms = {
            "Movie_Up": ["Movie_Up", "Movie_UpLeft", "Movie_UpRight"],
            "Movie_Down": ["Movie_Down", "Movie_DownLeft", "Movie_DownRight"],
            "Movie_Left": ["Movie_Left", "Movie_LeftUp", "Movie_LeftDown"],
            "Movie_Right": ["Movie_Right", "Movie_RightUp", "Movie_RightDown"],
            "Movie_UpLeft": ["Movie_Left", "Movie_LeftUp", "Movie_LeftDown"],
            "Movie_UpRight": ["Movie_Right", "Movie_RightUp", "Movie_RightDown"],
            "Movie_DownLeft": ["Movie_Left", "Movie_LeftUp", "Movie_LeftDown"],
            "Movie_DownRight": ["Movie_Right", "Movie_RightUp", "Movie_RightDown"],
            "Movie_LeftUp": ["Movie_Up", "Movie_UpLeft", "Movie_UpRight"],
            "Movie_LeftDown": ["Movie_Down", "Movie_DownLeft", "Movie_DownRight"],
            "Movie_RightUp": ["Movie_Up", "Movie_UpLeft", "Movie_UpRight"],
            "Movie_RightDown": ["Movie_Down", "Movie_DownLeft", "Movie_DownRight"]
        }
        self.onPlumberItemWinPos = Notification.addObserver(Notificator.onPlumberItemWinPos, self.__onChangeGame)
        pass

    def playEnigma(self):
        self._setupParams()
        self.listHeroes = self.itemsData[:]
        self.__onChangeGame()

        pass

    def __onChangeGame(self):
        if self.listHeroes == []:
            self.enigmaComplete()
            return False
            pass

        nextHero = self.listHeroes.pop(0)
        nextHeroKey = nextHero.getID()
        self.HeroKey = nextHeroKey
        self._playCurrentGame()
        return False
        pass

    def _stopEnigma(self):
        super(Plumber, self)._stopEnigma()
        return False
        pass

    def onDeactivate(self):
        super(Plumber, self).onDeactivate()
        Notification.removeObserver(self.onPlumberItemWinPos)
        self.Destroy()
        pass

    def _setupParams(self):
        self.data = PlumberManager.getGameData(self.EnigmaName)
        self.wallsData = self.data.getWallsData()
        self._setupField()
        self.movementMovies = self.data.getMovementMovies()
        self.cellItems = self.data.getCellItemData()
        self._setupCellItems()
        self.cells = self.Field.getCells()

        self.itemsData = self.data.getItemData()
        self.disableWinMovies()
        self.setupSafeCells()

        self.buttons = self.data.getButtons()
        pass

    def prepareCurrentGame(self):
        self.currentItemData = self.getItemDataByID(self.HeroKey)
        self.getStartCell()
        self.disableUnusedMovies(self.currentItemData)
        self.Field.setItemToCell(self.currentItemData)
        pass

    def _playCurrentGame(self):
        self.prepareCurrentGame()

        items = self.cellItems.values()
        itemsCount = len(items)

        cells = [cell for cell in self.cells.itervalues() if cell.getMovie() is not None]
        cellsCount = len(cells)

        if TaskManager.existTaskChain("Play"):
            TaskManager.cancelTaskChain("Play")
            pass
        with TaskManager.createTaskChain(Name="Play", Repeat=True) as tc:
            with tc.addRepeatTask() as (tc_setItems, tc_until):
                with tc_setItems.addRaceTask(itemsCount) as tc_items:
                    for tc_item, item in zip(tc_items, items):
                        itemMovie = item.getMovie()
                        itemSelectedMovie = item.getSelectedMovie()

                        tc_item.addScope(self._enableCellItemSocket, item)
                        tc_item.addEnable(itemMovie)
                        tc_item.addDisable(itemSelectedMovie)

                        tc_item.addTask("TaskMovieSocketClick", SocketName="socket", Movie=itemMovie)
                        tc_item.addScope(self._disableCellItemSockets, item)
                        tc_item.addDisable(itemMovie)
                        tc_item.addEnable(itemSelectedMovie)

                        with tc_item.addRaceTask(cellsCount) as tc_cells:
                            for tc_cell, cell in zip(tc_cells, cells):
                                cellMovie = cell.getMovie()
                                tc_cell.addTask("TaskMovieSocketClick", SocketName="socket", Movie=cellMovie)
                                tc_cell.addScope(self.setItemToCell, cell, item)
                                tc_cell.addFunction(self.reatachItemMovies, itemMovie, itemSelectedMovie, cellMovie)
                                pass
                            pass
                        pass
                    pass

                tc_until.addTask("TaskButtonClick", Button=self.buttons["Go"])
                pass
            tc.addScope(self._update)
            pass
        pass

    def _enableCellItemSocket(self, scope, currentCellItem):
        movie = currentCellItem.getMovie()
        scope.addTask("TaskMovieSocketEnable", SocketName="socket", Movie=movie, Value=True)
        pass

    def _disableCellItemSockets(self, scope, currentCellItem):
        for cellItem in self.cellItems.values():
            if cellItem != currentCellItem:
                movie = cellItem.getMovie()
                scope.addTask("TaskMovieSocketEnable", SocketName="socket", Movie=movie, Value=False)
                pass
            pass
        pass

    def disableWinMovies(self):
        for item in self.itemsData:
            itemWinMovie = item.getWinMovie()
            itemWinMovie.setEnable(False)
            pass
        pass

    def disableUnusedMovies(self, currentItem):
        for item in self.itemsData:
            itemMovie = item.getMovie()
            itemMovieEntity = itemMovie.getEntity()

            itemCrashMovie = item.getCrashMovie()
            itemCrashMovieEntity = itemCrashMovie.getEntity()
            itemCrashMovieEntity.removeFromParent()
            itemCrashMovie.setEnable(False)

            itemDirectionMovie = item.getDirectionMovie()
            itemDirectionMovieEntity = itemDirectionMovie.getEntity()

            if item != currentItem:
                itemMovieEntity.removeFromParent()
                itemDirectionMovieEntity.removeFromParent()
                itemMovie.setEnable(False)
                pass
            else:
                itemMovie.setEnable(True)
                pass
            pass
        pass

    def setItemToCell(self, scope, cell, item):
        parentItemCell = item.getParentCell()

        if parentItemCell is not None:
            parentItemCell.setData(0)
            parentItemCellMovie = parentItemCell.getMovie()
            scope.addTask("TaskMovieSocketEnable", SocketName="socket", Movie=parentItemCellMovie, Value=True)
            pass

        if cell is not None:
            cellData = cell.getData()
            if cellData == (0):
                itemMovie = item.getMovie()
                itemMovieName = itemMovie.getName()
                if itemMovieName == "Movie_ItemOne":
                    cell.setData(1)
                    pass
                elif itemMovieName == "Movie_ItemTwo":
                    cell.setData(2)
                    pass
                elif itemMovieName == "Movie_ItemThree":
                    cell.setData(3)
                    pass
                elif itemMovieName == "Movie_ItemFour":
                    cell.setData(4)
                    pass
                pass

            cellMovie = cell.getMovie()
            scope.addTask("TaskMovieSocketEnable", SocketName="socket", Movie=cellMovie, Value=False)
            item.setParentCell(cell)
            pass
        else:
            item.removeParentCell()
            pass
        pass

    def _update(self, scope):
        self.makeRoad()
        with scope.addRepeatTask() as (tc, tc_until):
            tc.addScope(self.makeStep)

            with tc_until.addRaceTask(2) as (tc_until1, tc_until2):
                tc_until1.addListener(Notificator.onPlumberCollision)

                tc_until2.addTask("TaskButtonClick", Button=self.buttons["Stop"])
                tc_until2.addFunction(self.prepareCurrentGame)
                pass  # tc_until.addTask("TaskFunction", Fn = self.prepareCurrentGame)
        pass

    def makeStep(self, scope):
        currentStep = self.road.pop(0)

        currentCell = currentStep[0]
        currentDirectionMovie = currentStep[1]
        currentState = currentStep[2]
        if currentState == "win":
            scope.addFunction(self.playWin, currentCell, currentDirectionMovie)
            pass
        elif currentState == "crash":
            scope.addFunction(self.playCrash, currentCell, currentDirectionMovie)
            self.prepareCurrentGame()
            pass
        else:
            scope.addScope(self.playMove, currentCell, currentDirectionMovie)
            pass
        pass

    def playMove(self, scope, currentCell, currentDirectionMovie):
        curItemMovie = self.currentItemData.getMovie()
        curItemMovieEntity = curItemMovie.getEntity()
        curItemMovieEntity.removeFromParent()

        currentDirectionMovieEntity = currentDirectionMovie.getEntity()
        currentDirectionMovieEntity.removeFromParent()

        currentCellMovie = currentCell.getMovie()
        currentCellMovieEntity = currentCellMovie.getEntity()

        slot = currentDirectionMovieEntity.getMovieSlot("slot")
        slot.addChild(curItemMovieEntity)
        currentCellMovieEntity.addChild(currentDirectionMovieEntity)
        scope.addTask("TaskMoviePlay", Movie=currentDirectionMovie, Wait=True)
        scope.addTask("TaskMovieLastFrame", Movie=currentDirectionMovie, Value=False)
        return True
        pass

    def playWin(self, currentCell, currentDirectionMovie):
        if TaskManager.existTaskChain("Play"):
            TaskManager.cancelTaskChain("Play")
            pass

        if TaskManager.existTaskChain("CompleteWin"):
            TaskManager.cancelTaskChain("CompleteWin")
            pass

        currentCell.setData(self.wallsData)
        cellMovie = currentCell.getMovie()
        cellMovieEntity = cellMovie.getEntity()

        winMovie = self.currentItemData.getWinMovie()
        winMovieEntity = winMovie.getEntity()
        winMovie.setEnable(True)

        currentItemMovie = self.currentItemData.getMovie()
        currentItemMovieEntity = currentItemMovie.getEntity()
        currentItemMovieEntity.removeFromParent()
        currentItemMovie.setEnable(False)

        halfMovie = currentDirectionMovie
        halfMovieEntity = halfMovie.getEntity()
        halfMovieSlot = halfMovieEntity.getMovieSlot("slot")

        cellMovieEntity.addChild(halfMovieEntity)
        halfMovieSlot.addChild(winMovieEntity)

        winMovieEntity.setFirstFrame()
        halfMovieEntity.setFirstFrame()
        with TaskManager.createTaskChain(Name="CompleteWin") as tc:
            with tc.addParallelTask(2) as (tc_1, tc_2):
                tc_1.addTask("TaskMoviePlay", Movie=halfMovie, Wait=True)
                tc_2.addTask("TaskMoviePlay", Movie=winMovie, Wait=True)
                pass
            tc.addTask("TaskMovieSocketEnable", SocketName="socket", Movie=cellMovie, Value=False)
            tc.addFunction(self.completeCurrentWin, cellMovieEntity, winMovieEntity, halfMovieEntity)
            pass
        return True
        pass

    def playCrash(self, currentCell, currentDirectionMovie):
        currentItem = self.currentItemData

        currentCellMovie = currentCell.getMovie()
        currentCellMovieEntity = currentCellMovie.getEntity()

        halfMovie = currentDirectionMovie
        halfMovieEntity = halfMovie.getEntity()

        halfMovieEntity.removeFromParent()

        currentCrushMovie = currentItem.getCrashMovie()
        currentCrushMovieEntity = currentCrushMovie.getEntity()
        currentCrushMovieEntity.removeFromParent()

        currentSlot = halfMovieEntity.getMovieSlot("slot")

        currentCellMovieEntity.addChild(halfMovieEntity)
        currentSlot.addChild(currentCrushMovieEntity)

        halfMovieEntity.setFirstFrame()

        with TaskManager.createTaskChain() as tc:
            tc.addEnable(currentCrushMovie)
            tc.addTask("TaskMoviePlay", Movie=currentCrushMovie, Wait=True)
            tc.addFunction(self.movieRemoveFromParent, currentCrushMovie)
            tc.addFunction(self.movieRemoveFromParent, halfMovie)
            tc.addDisable(currentCrushMovie)
            pass

        Notification.notify(Notificator.onPlumberCollision)
        return True
        pass

    def movieRemoveFromParent(self, movie):
        movieEntity = movie.getEntity()
        movieEntity.removeFromParent()
        pass

    def completeCurrentWin(self, cellMovieEntity, winMovieEntity, halfMovieEntity):
        winMovieEntity.removeFromParent()
        halfMovieEntity.removeFromParent()
        cellMovieEntity.addChild(winMovieEntity)

        Notification.notify(Notificator.onPlumberItemWinPos)
        self._setupCellItems()
        pass

    def getHalfMovie(self, movement):
        movie = None
        if movement == (0, -1):
            movie = self.movementMovies["HalfUp"]
            pass
        elif movement == (0, 1):
            movie = self.movementMovies["HalfDown"]
            pass
        elif movement == (-1, 0):
            movie = self.movementMovies["HalfLeft"]
            pass
        elif movement == (1, 0):
            movie = self.movementMovies["HalfRight"]
            pass
        else:
            pass
        return movie
        pass

    def setCellItemsToStart(self):
        self._setupCellItems()
        for cellItem in self.cellItems.values():
            parentCell = cellItem.getParentCell()
            parentCell.setData(0)

            cellItemMovie = cellItem.getMovie()
            self.movieRemoveFromParent(cellItemMovie)
            pass
        pass

    def setupSafeCells(self):
        self.safeCells.append(0)
        for key in self.cellItems.keys():
            self.safeCells.append(key)
            pass

        for values in self.itemsData:
            key = values.getWinPos()
            self.safeCells.append(key)
            pass

        for values in self.itemsData:
            key = values.getID()
            self.safeCells.append(key)
            pass
        pass

    def reatachItemMovies(self, itemMovie, itemSelectedMovie, cellMovie):
        itemMovieEntity = itemMovie.getEntity()
        itemSelectedMovieEntity = itemSelectedMovie.getEntity()
        cellMovieEntity = cellMovie.getEntity()

        itemMovieEntity.removeFromParent()
        itemSelectedMovieEntity.removeFromParent()
        cellMovieEntity.addChild(itemMovieEntity)
        cellMovieEntity.addChild(itemSelectedMovieEntity)
        pass

    def makeRoad(self):
        self.road = []
        curDirectionMovie = self.currentItemData.getDirectionMovie()

        self.road.append((self.startCell, curDirectionMovie, "move"))
        movement = self.getMovement(curDirectionMovie)
        curCell = self.getNextCell(self.startCell, movement)
        prevDirectionMovie = curDirectionMovie

        while curCell.getData() != self.wallsData and curCell.getData() != self.currentItemData.getWinPos():
            state = "move"
            result = self.addNextCell(curCell, prevDirectionMovie, movement)

            if curCell.getData() != self.wallsData:
                curDirectionMovie = result[1]
                nextCell = result[0]
                step = (curCell, curDirectionMovie, state)
                if step in self.road:
                    break
                    pass
                self.road.append(step)

                curCell = nextCell
                prevDirectionMovie = curDirectionMovie
                movement = self.getMovement(curDirectionMovie)
                pass
            pass
        if curCell.getData() == self.wallsData:
            state = "crash"
            pass
        elif curCell.getData() == self.currentItemData.getWinPos():
            state = "win"
            pass
        else:
            state = "crash"
            pass
        movie = self.getHalfMovie(movement)
        self.road.append((curCell, movie, state))
        pass

    def addNextCell(self, curCell, prevDirectionMovie, movement):
        curCellData = curCell.getData()
        prevDirectionMovieName = prevDirectionMovie.getName()
        movie = None

        if curCellData in self.cellItems.keys():
            movie = self.changeDirection(curCell, prevDirectionMovie, curCellData)
            movement = self.getMovement(movie)
            pass
        else:
            directionMovieName = self.movieConforms[prevDirectionMovieName][0]
            movie = self.object.getObject(directionMovieName)
            pass

        nextCell = self.getNextCell(curCell, movement)

        return (nextCell, movie)
        pass

    def getNextCell(self, curCell, movement):
        curCellRow = curCell.getPosition()[0]
        curCellColumn = curCell.getPosition()[1]
        nextCellRow = curCellRow + movement[1]
        nextCellColumn = curCellColumn + movement[0]
        nextCell = self.cells[(nextCellRow, nextCellColumn)]

        return nextCell
        pass

    def changeDirection(self, curCell, prevCellMovie, key):
        prevCellMovieName = prevCellMovie.getName()

        currentDirectionMovieNames = self.cellItems[key].getDirectionMovieNames()
        currentMovieConforms = self.movieConforms[prevCellMovieName]
        for movieName in currentDirectionMovieNames:
            if movieName in currentMovieConforms:
                movie = self.object.getObject(movieName)
                return movie
            pass

        # if bad direction cellItem
        curCell.setData(self.wallsData)
        return None
        pass

    def getMovement(self, movie):
        if movie == self.movementMovies["Up"] or movie == self.movementMovies["LeftUp"] or movie == self.movementMovies["RightUp"]:
            movement = (0, -1)
            pass
        elif movie == self.movementMovies["Down"] or movie == self.movementMovies["LeftDown"] or movie == self.movementMovies["RightDown"]:
            movement = (0, 1)
            pass
        elif movie == self.movementMovies["Right"] or movie == self.movementMovies["UpRight"] or movie == self.movementMovies["DownRight"]:
            movement = (1, 0)
            pass
        elif movie == self.movementMovies["Left"] or movie == self.movementMovies["UpLeft"] or movie == self.movementMovies["DownLeft"]:
            movement = (-1, 0)
            pass
        else:
            movement = (0, 0)
            pass
        return movement
        pass

    def _setupField(self):
        movieStart = self.object.getObject("Movie_Start")
        movieStartEntity = movieStart.getEntity()

        startSlot = movieStartEntity.getMovieSlot("start")
        startPosX = startSlot.getWorldPosition()[0]
        startPosY = startSlot.getWorldPosition()[1]
        startPos = (startPosX, startPosY)

        self.Field = Field(startPos, self.data)
        self.Field.setupCells(self.object)
        pass

    def getItemDataByID(self, id):
        for itemData in self.itemsData:
            if itemData.getID() == id:
                return itemData
                pass
            pass

        Trace.log("Entity", 0, "id %d not in self.itemsData IDs" % (id))
        return None
        pass

    def getStartCell(self):
        startItemRow = self.currentItemData.getRow()
        startItemColumn = self.currentItemData.getColumn()
        self.startCell = self.cells[(startItemRow, startItemColumn)]
        pass

    def _setupCellItems(self):
        movieStart = self.object.getObject("Movie_Start")
        movieStartEntity = movieStart.getEntity()

        startSlots = {}
        startSlots[1] = movieStartEntity.getMovieSlot("startItemOne")
        startSlots[2] = movieStartEntity.getMovieSlot("startItemTwo")
        startSlots[3] = movieStartEntity.getMovieSlot("startItemThree")
        startSlots[4] = movieStartEntity.getMovieSlot("startItemFour")
        for key, cellItem in self.cellItems.iteritems():
            parentCell = cellItem.getParentCell()
            if parentCell is not None:
                parentCell.setData(0)
                cellMovie = parentCell.getMovie()
                cellItem.removeParentCell()
                TaskManager.runAlias("TaskMovieSocketEnable", None, SocketName="socket", Movie=cellMovie, Value=True)
                pass
            cellItemMovie = cellItem.getMovie()
            cellItemMovieEntity = cellItemMovie.getEntity()

            cellItemSelectedMovie = cellItem.getSelectedMovie()
            cellItemSelectedMovieEntity = cellItemSelectedMovie.getEntity()

            startSlots[key].addChild(cellItemMovieEntity)
            startSlots[key].addChild(cellItemSelectedMovieEntity)
            pass
        pass

    def Destroy(self):
        if TaskManager.existTaskChain("Play"):
            TaskManager.cancelTaskChain("Play")
            pass
        if TaskManager.existTaskChain("CompleteWin"):
            TaskManager.cancelTaskChain("CompleteWin")
            pass

        for item in self.itemsData:
            movie = item.getMovie()
            self.movieRemoveFromParent(movie)
            movieWin = item.getWinMovie()
            self.movieRemoveFromParent(movieWin)
            pass
        for item in self.cellItems.values():
            movie = item.getMovie()
            self.movieRemoveFromParent(movie)
            movieSelected = item.getSelectedMovie()
            self.movieRemoveFromParent(movieSelected)
            item.removeParentCell()
            pass
        for movie in self.movementMovies.itervalues():
            self.movieRemoveFromParent(movie)
            pass

        self.Field.onDrestroy()
        self.Field = None
        self.movementMovies = {}
        self.cells = {}
        self.road = []
        self.data = None
        self.cellItems = {}
        self.startCell = None
        self.currentItemData = None
        self.wallsData = None
        self.safeCells = []
        self.itemsData = []
        self.listHeroes = {}
        self.movieConforms = {}
        self.buttons = {}
        pass
