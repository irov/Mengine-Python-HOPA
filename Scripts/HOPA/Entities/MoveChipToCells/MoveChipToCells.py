from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.MoveChipToCellsManager import MoveChipToCellsManager

Enigma = Mengine.importEntity("Enigma")

class MoveChipToCells(Enigma):
    class Chip(object):
        def __init__(self, movie):
            self.movie = movie
            self.node = movie.getEntityNode()
            self.currentCell = None
            self.previousCell = None
            self.previousPosition = None
            self.push_state = {True: "Sprite_Toast_Icon_push", False: "Sprite_Toast_Icon_idle"}
            self.setPush(False)

        def clickDown(self, source):
            source.addTask('TaskMovie2SocketClick', SocketName="chip", Movie2=self.movie, isDown=True)
            source.addFunction(self.setPush, True)

        def clickUp(self, source):
            source.addTask('TaskMouseButtonClick', isDown=False)
            source.addFunction(self.setPush, False)

        def setPush(self, state):
            DisableLayers = self.movie.getParam("DisableLayers")
            if self.push_state[not state] not in DisableLayers:
                self.movie.appendParam("DisableLayers", self.push_state[not state])
            if self.push_state[state] in DisableLayers:
                self.movie.delParam("DisableLayers", self.push_state[state])

    class Cell(object):
        def __init__(self, movie, id, slot):
            self.id = id
            self.movie = movie
            self.slot = slot
            self.isUp = False

        def cellUp(self):
            if self.movie is not None:
                self.movie.setEnable(True)
            self.isUp = True

        def scopeCellUp(self, source):
            self.cellUp()
            source.addTask("TaskMovie2Play", Movie2=self.movie, Wait=False)

        def kill(self):
            if self.movie is not None:
                self.movie.onDestroy()

        def getPosition(self):
            return self.slot.getWorldPosition()

    def __init__(self):
        super(MoveChipToCells, self).__init__()
        self.param = None
        self.tc = None
        self.cells = {}
        self.upCells = []
        self.chip = None
        self.movieMove = None
        self.finishCell = None
        self.move_buttons = {}

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(MoveChipToCells, self)._onPreparation()

    def _onActivate(self):
        super(MoveChipToCells, self)._onActivate()

    def _onDeactivate(self):
        super(MoveChipToCells, self)._onDeactivate()
        self._cleanUp()

    # ==================================================================================================================

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self._loadParam()
        self._setup()
        self._runTaskChain()

    def _restoreEnigma(self):
        self._playEnigma()

    # ==================================================================================================================

    def _loadParam(self):
        self.param = MoveChipToCellsManager.getParam(self.EnigmaName)

    def _setup(self):
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        Group = GroupManager.getGroup(GroupName)
        BG = Group.getObject('Movie2_BG')

        for i in range(1, self.param.CellParams['NumOfCells'] + 1):
            slot = BG.getMovieSlot('cell_{}'.format(i))
            movieCellUp = None
            if i not in self.param.CellParams['CellsWithDeep']:
                movieCellUp = Group.tryGenerateObjectUnique(self.param.CellParams['CellUp'] + '_{}'.format(i), self.param.CellParams['CellUp'], Enable=True)

                slot.addChild(movieCellUp.getEntityNode())
                movieCellUp.setEnable(False)
            cell = MoveChipToCells.Cell(movieCellUp, i, slot)
            self.cells[i] = cell

        startCellID = self.param.CellParams['StartCell']
        slot = BG.getMovieSlot('cell_{}'.format(startCellID))

        # chipMovie = Group.getObject(self.param.ChipName)
        movieChip = Group.tryGenerateObjectUnique(self.param.ChipName, self.param.ChipName, Enable=True)

        slot.addChild(movieChip.getEntityNode())
        self.chip = MoveChipToCells.Chip(movieChip)

        # slot_pos = slot.getWorldPosition()
        # self.chip.node.setWorldPosition(slot_pos)

        self.chip.currentCell = self.cells[startCellID]

        self.movieMove = Group.tryGenerateObjectUnique("move", "Movie2_Move", Enable=True)
        slot.addChild(self.movieMove.getEntityNode())

        slot = BG.getMovieSlot('cell_{}'.format(self.param.CellParams['FinishCell']))
        cell = MoveChipToCells.Cell(None, self.param.CellParams['FinishCell'], slot)
        self.finishCell = cell

        if Mengine.hasTouchpad() is True:
            sockets = ['down', 'right', 'up', 'left']
            angle = 0
            for socket in sockets:
                slot = BG.getMovieSlot(socket)
                movieMove = Group.tryGenerateObjectUnique("MobileMove_" + "{}".format(socket), "Movie2Button_MoveMobile", Enable=True)
                movieMoveNode = movieMove.getEntityNode()
                slot.addChild(movieMoveNode)
                movieMoveNode.setAngle(angle)
                angle += 1.5708

                self.move_buttons[socket] = movieMove

    def _runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)

        with self.tc as tc:
            if Mengine.hasTouchpad() is False:
                tc.addScope(self.chip.clickDown)
                with tc.addRepeatTask() as (tc_repeat, tc_until):
                    tc_repeat.addScope(self.scopeDrag)
                    tc_until.addScope(self.chip.clickUp)
            else:
                for socket_name, source in tc.addRaceTaskList(self.move_buttons):
                    source.addTask("TaskMovie2ButtonClick", Movie2Button=self.move_buttons[socket_name], isDown=True)
                    SocketHolder = Holder()
                    source.addFunction(SocketHolder.set, socket_name)
                    source.addScope(self.moveToCellUnderSocket, SocketHolder)
                    source.addDelay(100)
            tc.addFunction(self._checkWin)
        pass

    def scopeDrag(self, source):
        sockets = ['up', 'down', 'right', 'left']
        SocketHolder = Holder()
        for socket, race in source.addRaceTaskList(sockets):
            race.addTask("TaskMovie2SocketEnter", Movie2=self.movieMove, SocketName=socket)
            # race.addPrint(" >> {}".format(socket))
            race.addFunction(SocketHolder.set, socket)
        source.addScope(self.moveToCellUnderSocket, SocketHolder)
        source.addDelay(100)
        pass

    def moveToCellUnderSocket(self, source, holder):
        socketName = holder.get()
        socket = self.movieMove.getSocket(socketName)

        cell = self.getCellBySocket(socket)

        if self.chip.currentCell.id == self.finishCell.id:
            return

        if cell is None:
            # print " !! cell is None"
            return

        if cell.isUp is True:
            # print " !! cell {} isUp is True".format(cell.id)
            return

        if self.isBlocked(self.chip.currentCell, cell) is True:
            # print " !! self.isBlocked({}, {}) is True".format(self.chip.currentCell.id, cell.id)
            return

        if cell.id in self.param.CellParams['CellsWithDeep']:
            new_cell = self.getNextTeleport(cell.id)
            cell = new_cell  # print " !! cell {} is Teleport to {}".format(cell.id, new_cell.id)

        # print "cell ", cell.id

        cell.slot.addChild(self.chip.node)
        cell.slot.addChild(self.movieMove.getEntityNode())

        # pos = cell.getPosition()
        # self.chip.node.setWorldPosition(pos)

        if self.chip.currentCell.id not in self.param.CellParams['CellsWithDeep']:
            # self.chip.currentCell.cellUp()
            source.addScope(self.chip.currentCell.scopeCellUp)
        self.chip.currentCell = cell

        self.upCells.append(cell)

    def isBlocked(self, cell_1, cell_2):
        if (cell_1.id, cell_2.id) in self.param.BorderParams:
            return True

        if (cell_2.id, cell_1.id) in self.param.BorderParams:
            return True

        return False

    def getNextTeleport(self, cellID):
        index = self.param.CellParams['CellsWithDeep'].index(cellID)

        new_index = index + 1
        if new_index >= len(self.param.CellParams['CellsWithDeep']):
            new_index = 0

        nextCellID = self.param.CellParams['CellsWithDeep'][new_index]
        nextCell = self.cells[nextCellID]
        return nextCell

    def getCellBySocket(self, socket):
        # bb = socket.getBoundingBox()
        bb = Mengine.getHotSpotPolygonBoundingBox(socket)
        minX, maxX, minY, maxY = bb.minimum.x, bb.maximum.x, bb.minimum.y, bb.maximum.y
        for cell in self.cells.itervalues():
            pos = cell.getPosition()

            if (pos.x > minX) and (pos.x < maxX) and (pos.y > minY) and (pos.y < maxY):
                return cell

        pos = self.finishCell.getPosition()
        if (pos.x > minX) and (pos.x < maxX) and (pos.y > minY) and (pos.y < maxY):
            return self.finishCell
        return None

    def _checkWin(self):
        if len(self.upCells) == len(self.cells):
            self.enigmaComplete()
            return

        if self.chip.currentCell.id == self.finishCell.id:
            self._resetEnigma()
            return

        sockets = ['up', 'down', 'right', 'left']
        for socketName in sockets:
            socket = self.movieMove.getSocket(socketName)
            cell = self.getCellBySocket(socket)
            if cell is None:
                continue
            if cell.isUp is True:
                continue
            if self.isBlocked(self.chip.currentCell, cell) is True:
                continue
            return

        self._resetEnigma()

        pass

    def _resetEnigma(self):
        self._cleanUp()
        self._playEnigma()

        pass

    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
        self.tc = None

        self.param = None
        for cell in self.cells.itervalues():
            cell.kill()
        self.cells = {}

        if self.chip is not None:
            # self.chip.node.removeFromParent()
            self.chip.movie.onDestroy()
        self.chip = None

        if self.movieMove is not None:
            self.movieMove.onDestroy()
        self.movieMove = None

        for button in self.move_buttons.values():
            button.onDestroy()
        self.move_buttons = {}

        self.upCells = []