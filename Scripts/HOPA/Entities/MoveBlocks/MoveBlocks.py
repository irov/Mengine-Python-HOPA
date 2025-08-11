from MoveBlocksManager import MoveBlocksManager

Enigma = Mengine.importEntity("Enigma")

class MoveBlocks(Enigma):
    def __init__(self):
        super(MoveBlocks, self).__init__()
        self.Field = None
        self.MovieField = None
        self.Win = {}
        self.buttons = {}
        self.blocks = {}
        self.slots = {}
        self.MoviesToPlay = {}
        self.ButtonObserver = None
        pass

    def _onInitialize(self, obj):
        super(MoveBlocks, self)._onInitialize(obj)
        pass

    def _stopEnigma(self):
        super(MoveBlocks, self)._stopEnigma()
        Notification.removeObserver(self.ButtonObserver)
        self.ButtonObserver = None
        pass

    def _resetEnigma(self):
        for movie in self.slots.values():
            movie.setEnable(False)
            entity = movie.getEntity()
            entity.removeFromParent()
            pass
        Data = MoveBlocksManager.getData(self.EnigmaName)
        self.Field = Data.getField()
        pass

    def _restoreEnigma(self):
        self._playEnigma()
        pass

    def _playEnigma(self):
        self.ButtonObserver = Notification.addObserver(Notificator.onButtonClick, self.__onButtonClick)
        pass

    def _onPreparation(self):
        super(MoveBlocks, self)._onPreparation()
        self.MovieField = self.object.getObject("Movie_Field")
        self.MovieField.setEnable(True)
        Data = MoveBlocksManager.getData(self.EnigmaName)
        if self.Field is None:
            self.Field = Data.getField()
            pass
        self.Win = Data.getWin()
        buttonsData = Data.getButtons()
        for name, data in buttonsData.iteritems():
            button = self.object.getObject(name)
            button.setEnable(True)
            button.setInteractive(True)

            self.buttons[button] = data
            pass

        blocksData = Data.getBlocks()

        for id, data in blocksData.iteritems():
            idleName = data.getIdleName()
            idle = self.object.getObject(idleName)
            idle.setEnable(False)
            offName = data.getOffName()
            off = self.object.getObject(offName)
            off.setEnable(False)
            onName = data.getOnName()
            on = self.object.getObject(onName)
            on.setEnable(False)

            self.blocks[id] = (on, idle, off)
            pass
        pass

    def setupIdle(self):
        for row, values in self.Field.iteritems():
            for pos, value in enumerate(values):
                if value == 0:
                    continue
                    pass
                slotId = str(row) + "_" + str(pos)
                movieIdle = self.blocks[value][1]
                movieFieldEntity = self.MovieField.getEntity()
                slot = movieFieldEntity.getMovieSlot(slotId)
                movieIdle.setEnable(True)
                movieIdleEntityNode = movieIdle.getEntityNode()
                slot.addChild(movieIdleEntityNode)
                movieIdle.setLoop(True)
                movieIdle.setPlay(True)
                self.slots[slotId] = movieIdle
                pass
            pass
        pass

    def printField(self):
        print("------------------")
        for value in self.Field.values():
            print(value)
            pass
        print("------------------")
        pass

    def _onActivate(self):
        super(MoveBlocks, self)._onActivate()
        self.setupIdle()

        pass

    def __onButtonClick(self, button):
        if button not in self.buttons:
            return False
            pass
        # print "OLD----->"
        # self.printField()
        self.updateField(button)
        # print "NEW----->"
        # self.printField()
        if self.isWin() is True:
            self.enigmaComplete()
            return True
            pass
        return False
        pass

    def isWin(self):
        if self.Field == self.Win:
            return True
            pass
        return False
        pass

    def updateField(self, button):
        data = self.buttons[button]
        mode = data.getMode()
        value = data.getValue()
        change = data.getChange()
        if mode == "row":
            tmp = self.Field[value]
            # ____play off movies
            for i, num in enumerate(tmp):
                if num != 0:
                    slotId = str(value) + "_" + str(i)
                    oldMovie = self.slots[slotId]
                    oldMovieEntity = oldMovie.getEntity()
                    oldMovie.setEnable(False)
                    oldMovieEntity.removeFromParent()

                    del self.slots[slotId]
                    pass
                pass
            pass
        elif mode == "column":
            tmp = []
            for i, arr in enumerate(self.Field.values()):
                tmp.append(arr[int(value)])
                if arr[int(value)] != 0:
                    slotId = str(i) + "_" + str(value)
                    oldMovie = self.slots[slotId]
                    oldMovieEntity = oldMovie.getEntity()
                    oldMovie.setEnable(False)
                    oldMovieEntity.removeFromParent()

                    del self.slots[slotId]
                    pass
                pass
            pass

        if change == 1:
            tmp = [tmp[-1]] + tmp[:-1]
            pass
        elif change == -1:
            tmp = tmp[1:] + [tmp[0]]
            pass
        if mode == "row":
            self.Field[value] = tmp
            for i, num in enumerate(tmp):
                if num != 0:
                    slotId = str(value) + "_" + str(i)
                    movieIdle = self.blocks[num][1]
                    movieFieldEntity = self.MovieField.getEntity()
                    slot = movieFieldEntity.getMovieSlot(slotId)
                    movieIdle.setEnable(True)
                    movieIdleEntityNode = movieIdle.getEntityNode()
                    slot.addChild(movieIdleEntityNode)
                    movieIdle.setLoop(True)
                    movieIdle.setPlay(True)
                    self.slots[slotId] = movieIdle
                    pass
                pass
        if mode == "column":
            for i, arr in enumerate(self.Field.values()):
                arr[int(value)] = tmp[i]
                if arr[int(value)] != 0:
                    slotId = str(i) + "_" + str(value)
                    movieIdle = self.blocks[arr[int(value)]][1]
                    movieFieldEntity = self.MovieField.getEntity()
                    slot = movieFieldEntity.getMovieSlot(slotId)
                    movieIdle.setEnable(True)
                    movieIdleEntityNode = movieIdle.getEntityNode()
                    slot.addChild(movieIdleEntityNode)
                    movieIdle.setLoop(True)
                    movieIdle.setPlay(True)
                    self.slots[slotId] = movieIdle
                    pass
                pass
            pass
        pass

    def _onDeactivate(self):
        super(MoveBlocks, self)._onDeactivate()
        for movie in self.slots.values():
            entity = movie.getEntity()
            entity.removeFromParent()
            pass
        # self.slots = {}
        # self.Field = {}
        # self.MovieField = None
        # self.Win = {}
        # self.buttons = {}
        # self.blocks = {}
        pass

    pass
