from Foundation.TaskManager import TaskManager
from HOPA.JoinBlocksManager import JoinBlocksManager
from Notification import Notification

from Block import Block
from Road import Road
from Slot import Slot


Enigma = Mengine.importEntity("Enigma")


class JoinBlocks(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction(Type, "BlockSave")
        pass

    def __init__(self):
        super(JoinBlocks, self).__init__()
        self.socketName = "Socket_Button"
        self.startSocket = None
        self.CheckRoads = []
        self.back = False
        self.newRoad = []
        self.allRoads = []
        self.currentBuildPath = {}
        self.previousSlot = None
        self.blocks = {}
        self.socket = None
        self.BeginBlock = None
        self.PathSoundMovie = None
        pass

    def _onDeactivate(self):
        super(JoinBlocks, self)._onDeactivate()
        self._stopEnigma()
        pass

    def _stopEnigma(self):
        super(JoinBlocks, self)._stopEnigma()

        Notification.removeObserver(self.EnigmaUndoButton)

        self.makeSave()
        self.destroy()
        if TaskManager.existTaskChain(self.EnigmaName):
            TaskManager.cancelTaskChain(self.EnigmaName)
            pass
        return False
        pass

    def makeSave(self):
        SaveData = {}
        for removeRoad in self.CheckRoads:
            head = removeRoad.getPathHead()
            block = removeRoad.getBeginBlock()
            saveName = block.getName()
            savePath = head.getPathSlotOrientation()
            SaveData[saveName] = savePath
            pass
        self.object.setParam("BlockSave", SaveData)
        pass

    def destroy(self):
        self.clearWaiters()

        if self.previousSlot is not None:
            self.previousSlot.destroy()
            pass

        for removeRoad in self.CheckRoads:
            removeRoad.destroy()
            pass

        for key, block in self.blocks.iteritems():
            block.destroy()
            key.removeFromParent()
            pass

        self.blocks.clear()
        del self.CheckRoads[:]
        self.previousSlot = None
        self.BeginBlock = None
        pass

    pass

    def restorePathFromSave(self):
        for blockName, pathArray in self.BlockSave.iteritems():
            # restore blocks states-------
            for keys, block in self.blocks.iteritems():
                if blockName == block.getName():
                    block.setState(True)
                    block._blocked = True
                    # take first block
                    if self.BeginBlock is None:
                        self.BeginBlock = block
                        continue
                    # take second block
                    pathArray.reverse()
                    for slotName, orient in pathArray:
                        # create path
                        id = "%s" % slotName
                        MovieEntity = self.Movie_Field.getEntity()
                        MovieSlot = MovieEntity.getMovieSlot(id)

                        slot = Slot()
                        slot._enigmaObject = self.object
                        slot.setSlot(MovieSlot)
                        slot.setPrevious(self.previousSlot)
                        slot.setOrientation(orient)
                        slot.recoverMovie()
                        self.newRoad.append(id)
                        self.allRoads.append(id)
                        self.previousSlot = slot
                    # add to check road

                    road = Road()
                    road.setBeginBlock(self.BeginBlock)
                    road.setEndBlock(block)
                    road.setPathHead(self.previousSlot)
                    road.setSlotIdList(self.newRoad)
                    road.setAllSlotList(self.allRoads)
                    self.CheckRoads.append(road)
                    # ------------------
                    self.newRoad = []
                    self.BeginBlock = None
                    self.previousSlot = None
                    pass
                pass
            pass
        pass

    def __onEnigmaUndoStep(self):
        if len(self.newRoad) != 0:
            self.cleanCurrentRoad(self.startSocket)
            return False
            pass
        checkId = len(self.CheckRoads)
        if checkId == 0:
            return False
            pass
        road = self.CheckRoads[checkId - 1]
        road.destroy()
        self.CheckRoads.pop()
        return False
        pass

    pass

    def _playEnigma(self):
        self.JoinBlocks = JoinBlocksManager.getJoinBlocks(self.EnigmaName)

        self.EnigmaUndoButton = Notification.addObserver(Notificator.onEnigmaUndoStep, self.__onEnigmaUndoStep)
        BlockList = self.JoinBlocks.getBlockName()
        BlockPositionList = self.JoinBlocks.getBlockPosition()
        BlockStateList = self.JoinBlocks.getBlockStates()

        self.Movie_Field = self.object.getObject("Movie_Field")

        self._createSlots(BlockList, BlockStateList, BlockPositionList)
        self.restorePathFromSave()

        if self.object.hasObject("Movie_PathSound") is True:
            self.PathSoundMovie = self.object.getObject("Movie_PathSound")
            pass

        self._startClick()
        pass

    def _restoreEnigma(self):
        self._playEnigma()
        pass

    def __blockSocket(self, curSocket):
        if curSocket not in self.blocks.keys():
            return False
            pass
        self.socket = curSocket
        block = self.blocks[curSocket]
        if block._blocked is True:
            return False
            pass
        block.setState(True)
        self.BeginBlock = block
        self.currentSlotMovie = block.getSlot()
        self.previousSlot = None
        for socket in self.blocks.keys():
            if socket is curSocket:
                self.startSocket = curSocket
                continue
                pass
            socket.setInteractive(False)
        return True
        pass

    pass

    def __blockEndSocket(self, curSocket):
        if curSocket in self.currentBuildPath.keys():
            check = curSocket.getName()
            for socket in self.blocks.keys():
                block = self.blocks[socket]
                blockName = block.getSlotName()
                if str(check) == str(blockName):
                    block = self.blocks[socket]
                    if block is self.BeginBlock:
                        self.cleanCurrentRoad(self.startSocket)
                        return False
                        pass
                    if block.getName() == self.BeginBlock.getName():
                        for i in self.newRoad:
                            self.allRoads.append(i)
                            pass
                        block.setState(True)
                        begin = self.BeginBlock
                        checkSlot = self.previousSlot
                        roadToSave = self.newRoad
                        self.newRoad = []
                        self.BeginBlock._blocked = True
                        block._blocked = True

                        checkRoad = Road()
                        checkRoad.setBeginBlock(begin)
                        checkRoad.setEndBlock(block)
                        checkRoad.setPathHead(checkSlot)
                        checkRoad.setSlotIdList(roadToSave)
                        checkRoad.setAllSlotList(self.allRoads)
                        self.CheckRoads.append(checkRoad)

                        self.startSocket.setInteractive(False)
                        for socket in self.blocks.keys():
                            socket.setInteractive(True)
                            pass
                        self.socket = None

                        orientation = self.currentBuildPath[curSocket]
                        self.previousSlot.setOrientationOut(orientation)
                        self.previousSlot.updateMovie()

                        self.clearWaiters()
                        return True
                        pass
                    else:
                        self.cleanCurrentRoad(self.startSocket)
                        return False
                        pass
                    pass
                pass
            pass
        else:
            self.cleanCurrentRoad(self.startSocket)
            return False
            pass
        self.cleanCurrentRoad(self.startSocket)
        return False
        pass

    def __pathSocket(self, curSocket):
        socketEntity = curSocket.getEntity()
        socketEntityNode = curSocket.getEntityNode()

        currentMovieSlot = socketEntityNode.getParent()
        check = currentMovieSlot.getName()
        checkLength = len(self.newRoad)
        if checkLength > 1:
            if check == self.newRoad[checkLength - 2]:
                self.currentSlotMovie = currentMovieSlot
                self.backStep()
                self.back = True
                self.newRoad.pop()
                return True
                pass
            pass
        if curSocket not in self.currentBuildPath.keys():
            return False
            pass
        if curSocket in self.currentBuildPath.keys():
            for socket in self.blocks.keys():
                block = self.blocks[socket]
                blockName = block.getSlotName()
                if str(check) == str(blockName):
                    return False
                    pass
                pass
            pass
        if check in self.newRoad:
            return False
            pass
        if check in self.allRoads:
            return False
            pass
        self.currentSlotMovie = currentMovieSlot
        self.socket = curSocket
        self.back = False
        return True
        pass

    def cleanCurrentRoad(self, startSocket):
        if TaskManager.existTaskChain(self.EnigmaName):
            TaskManager.cancelTaskChain(self.EnigmaName)
            pass
        startSocket.setInteractive(False)
        for socket in self.blocks.keys():
            socket.setInteractive(True)
            pass
        if self.previousSlot is not None:
            self.previousSlot.destroy()
            pass
        self.clearWaiters()
        self.BeginBlock.setState(False)
        self.newRoad = []
        self.back = False
        self._startClick()
        pass

    def _startClick(self):
        with TaskManager.createTaskChain(Name=self.EnigmaName, Group=self.object, Repeat=True) as tc_do:
            tc_do.addTask("TaskListener", ID=Notificator.onSocketClick, Filter=self.__blockSocket)
            with tc_do.addRepeatTask() as (tc_path, tc_until):
                tc_path.addTask("TaskFunction", Fn=self.createPath)
                tc_path.addTask("TaskFunction", Fn=self.generatePathHandler)
                tc_path.addTask("TaskListener", ID=Notificator.onSocketMouseEnter, Filter=self.__pathSocket)

                tc_until.addTask("TaskListener", ID=Notificator.onSocketClick, Filter=self.__blockEndSocket)
                tc_until.addTask("TaskFunction", Fn=self.__completeCheck)
                pass
            pass
        pass

    def clearWaiters(self):
        for socket in self.currentBuildPath.keys():
            socketEntity = socket.getEntity()
            socketEntity.removeFromParent()
            socket.removeFromParent()
            pass
        self.currentBuildPath = {}
        pass

    def createPath(self):
        if self.PathSoundMovie is not None:
            TaskManager.runAlias("TaskMoviePlay", None, Movie=self.PathSoundMovie)
            pass

        if self.back is True:
            return
            pass
        slot = Slot()
        slot._enigmaObject = self.object
        slot.setSlot(self.currentSlotMovie)
        slot.setPrevious(self.previousSlot)
        if self.previousSlot is not None:
            orientation = self.currentBuildPath[self.socket]
            slot.setOrientationIn(orientation)
            self.previousSlot.setOrientationOut(orientation)
            slot.updateMovie()
            self.previousSlot.updateMovie()
            pass
        self.newRoad.append(self.currentSlotMovie.getName())
        self.previousSlot = slot
        pass

    def backStep(self):
        if self.previousSlot is not None:
            slot = self.previousSlot.getPrevious()
            self.previousSlot.destroyOwn()
            self.previousSlot.setPrevious(None)
            self.previousSlot = slot
            self.previousSlot.setOrientationOut("")
            self.previousSlot.updateMovie()
            pass
        pass

    def generatePathHandler(self):
        self.clearWaiters()
        currentPosition = self.currentSlotMovie.getName()
        tmp = str(int(''.join(x for x in str(currentPosition) if x.isdigit())))
        x = int(tmp[0])
        y = int(tmp[1])
        if x - 1 > 0:
            socket = self.generatePathSocket(x - 1, y)
            self.currentBuildPath[socket] = "S"
            pass
        if x + 1 <= self.JoinBlocks.getFieldHeight():
            socket = self.generatePathSocket(x + 1, y)
            self.currentBuildPath[socket] = "N"
            pass
        if y - 1 > 0:
            socket = self.generatePathSocket(x, y - 1)
            self.currentBuildPath[socket] = "E"
            pass
        if y + 1 <= self.JoinBlocks.getFieldWidth():
            socket = self.generatePathSocket(x, y + 1)
            self.currentBuildPath[socket] = "W"
            pass
        socket = self.generatePathSocket(x, y)
        self.currentBuildPath[socket] = ""
        pass

    def generatePathSocket(self, x, y):
        id = "%d_%d" % (x, y)
        MovieEntity = self.Movie_Field.getEntity()
        CurrentSlot = MovieEntity.getMovieSlot(id)
        socket = self._generateSocket(self.socketName, str(id))
        socket.setPosition((0, 0))
        socket.setInteractive(True)
        socketEntityNode = socket.getEntityNode()
        CurrentSlot.addChild(socketEntityNode)
        return socket
        pass

    def _generateSocket(self, name, id):
        obj = self.object.generateObject(str(id), name)
        return obj
        pass

    def __completeCheck(self):
        countCheckRoads = len(self.CheckRoads)
        if countCheckRoads == self.JoinBlocks.getWinLength():
            if TaskManager.existTaskChain(self.EnigmaName):
                TaskManager.cancelTaskChain(self.EnigmaName)
                pass
            self.enigmaComplete()
            pass
        pass

    def _createSlots(self, BlockList, BlockStateList, BlockPositionList):
        for movieName, blockName, blockPosition in zip(BlockStateList, BlockList, BlockPositionList):
            movieObject = self.object.getObject(movieName[0])
            movie_activeObject = self.object.getObject(movieName[1])

            id = "%s" % blockPosition
            MovieEntity = self.Movie_Field.getEntity()
            MovieSlot = MovieEntity.getMovieSlot(id)

            block = Block()
            block.setMovieWait(movieObject)
            block.setMovieActive(movie_activeObject)
            block.setSlot(MovieSlot)
            block.setSlotName(blockPosition)
            block.setName(blockName)
            _socket = self._generateSocket(self.socketName, "BlockSocket_" + str(id))

            block.setState(False)
            block.setSocket(_socket)
            self.blocks[_socket] = block
            pass

        pass

    pass


pass
