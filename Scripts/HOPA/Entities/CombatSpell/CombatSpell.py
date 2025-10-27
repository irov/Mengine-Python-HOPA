from Foundation.TaskManager import TaskManager


Enigma = Mengine.importEntity("Enigma")


class Slot(object):
    offset_Ai = (-10, 6)
    offset_Player = (-6, 6)

    def __init__(self, slotX, slotY, SocketName, hotspot, MovieSlot, Group):
        self.slotX = slotX
        self.slotY = slotY
        self.SocketName = SocketName
        self.SocketHotSpot = hotspot
        self.MovieSlot = MovieSlot
        self.Group = Group

        self.Type = CombatSpell.Type_None
        self.Pure = None

        self.PlayMovie = None
        pass

    def setType(self, Type):
        self.Type = Type
        pass

    def UpdateTypeVisual(self):
        self.Clear()

        if (self.Type == CombatSpell.Type_Ai):
            self.Pure = self.__CreateSprite(CombatSpell.Sprite_Ai, Slot.offset_Ai)
            pass
        else:
            if (self.Type == CombatSpell.Type_Player):
                self.Pure = self.__CreateSprite(CombatSpell.Sprite_Player, Slot.offset_Player)
                pass
            pass
        pass

    def __CreateSprite(self, Sprite, offset):
        ItemEntity = Sprite.getEntity()
        pure = ItemEntity.generatePure()
        pure.enable()

        posSlot = self.MovieSlot.getLocalPosition()

        pos = (posSlot[0] + offset[0], posSlot[1] + offset[1])
        pure.setLocalPosition(pos)
        # prevent from scale with slot
        mainLayer = self.Group.getMainLayer()
        mainLayer.addChild(pure)

        return pure
        pass

    def Clear(self):
        if (self.Pure is None):
            return
            pass

        self.Pure.removeFromParent()
        Mengine.destroyNode(self.Pure)
        self.Pure = None
        pass

    def AttachMovie(self, movie):
        self.PlayMovie = movie

        movieEntity = self.PlayMovie.getEntity()
        posSlot = self.MovieSlot.getLocalPosition()

        movieEntity.setLocalPosition(posSlot)

        mainLayer = self.Group.getMainLayer()
        mainLayer.addChild(movieEntity)
        pass

    def DettachMovie(self):
        movieEntity = self.PlayMovie.getEntity()
        movieEntity.removeFromParent()
        self.PlayMovie = None
        pass

    pass


class CombatSpell(Enigma):
    Type_None = 0
    Type_Ai = 1
    Type_Player = 2

    Sprite_Ai = None
    Sprite_Player = None
    Click = (-1, -1)

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction("FieldWidth")
        Type.addAction("FieldHeight")
        Type.addAction("StartAiCount")
        Type.addAction("StartPlayerCount")

        Type.addAction("FieldXY")
        Type.addAction("AITurn")
        Type.addAction("CheckWin")
        pass

    def __init__(self):
        super(CombatSpell, self).__init__()
        self.slots = []
        self.AiSlots = []

        self.SlotsUpdateVisual = []

        self.Movie_PlayerEat = None
        self.Movie_PlayerMove = None

        self.AnimationsAi_Prefix = ["TL", "T", "TR", "R", "DR", "D", "DL", "L"]

        self.Movie_AnimationsAiEat = []
        self.Movie_AnimationsAiMove = []
        pass

    def _playEnigma(self):
        CombatSpell.Sprite_Ai = self.object.getObject("Item_ChessAi")
        CombatSpell.Sprite_Player = self.object.getObject("Item_ChessPlayer")
        CombatSpell.Sprite_Ai.setEnable(False)
        CombatSpell.Sprite_Player.setEnable(False)

        self.__MakeMovies()
        self.__InitSlots()
        self.__InitAlias()

        self.__InitSlotType()

        self.UpdateVisual()
        pass

    def _stopEnigma(self):
        for x in range(self.FieldWidth):
            for y in range(self.FieldHeight):
                if TaskManager.existTaskChain("CombatSpellSlotClick_%d_%d" % (x, y)) is True:
                    TaskManager.cancelTaskChain("CombatSpellSlotClick_%d_%d" % (x, y))
                    pass
                pass

        if TaskManager.existTaskChain("CombatSpellMain") is True:
            TaskManager.cancelTaskChain("CombatSpellMain")
            pass

        for x in range(self.FieldWidth):
            for y in range(self.FieldHeight):
                slot = self.slots[x][y]
                slot.Clear()
                pass

        self.__DestroyMovie(self.Movie_PlayerEat)
        self.__DestroyMovie(self.Movie_PlayerMove)

        self.slots = []
        self.AiSlots = []
        self.SlotsUpdateVisual = []

        self.Movie_PlayerEat = None
        self.Movie_PlayerMove = None

        for an in self.Movie_AnimationsAiEat:
            self.__DestroyMovie(an)
            pass

        for an in self.Movie_AnimationsAiMove:
            self.__DestroyMovie(an)
            pass

        self.Movie_AnimationsAiEat = []
        self.Movie_AnimationsAiMove = []
        pass

    def __MakeMovies(self):
        self.Movie_PlayerEat = self.__genMovies("Movie_PlayerEat")
        self.Movie_PlayerMove = self.__genMovies("Movie_PlayerMove")
        Movie_PlayerEatEntity = self.Movie_PlayerEat.getEntity()
        Movie_PlayerMoveEntity = self.Movie_PlayerMove.getEntity()

        Movie_PlayerEatEntity.removeFromParent()
        Movie_PlayerMoveEntity.removeFromParent()

        for pref in self.AnimationsAi_Prefix:
            Movie_AiEatName = "Movie_AiEat%s" % (pref)
            Movie_AiMoveName = "Movie_AiMove%s" % (pref)

            Movie_AiEat = self.__genMovies(Movie_AiEatName)
            Movie_AiMove = self.__genMovies(Movie_AiMoveName)

            Movie_AiEatEntity = Movie_AiEat.getEntity()
            Movie_AiMoveEntity = Movie_AiMove.getEntity()

            Movie_AiEatEntity.removeFromParent()
            Movie_AiMoveEntity.removeFromParent()

            self.Movie_AnimationsAiEat.append(Movie_AiEat)
            self.Movie_AnimationsAiMove.append(Movie_AiMove)
            pass
        pass

    def __genMovies(self, name):
        # Movie = self.object.generateObject(name, name)
        Movie = self.object.getObject(name)

        Movie.setEnable(True)
        Movie.setPosition((0, 0))
        return Movie
        pass

    def __DestroyMovie(self, Movie):
        MovieEntity = Movie.getEntity()
        MovieEntity.removeFromParent()
        pass

    def __InitSlots(self):
        self.slots = [[0 for col in range(self.FieldWidth)] for row in range(self.FieldHeight)]
        self.Movie = self.object.getObject("Movie_SlotPoints")

        for x in range(self.FieldWidth):
            for y in range(self.FieldHeight):
                SocketName = "socket_%d_%d" % (x, y)
                hotspot = self.__getHotSpot(SocketName)
                MovieSlot = self.__getMovieSlot(x, y)
                slot = Slot(x, y, SocketName, hotspot, MovieSlot, self.object.getGroup())
                self.slots[x][y] = slot
                pass
            pass
        pass

    def __InitAlias(self):
        for x in range(self.FieldWidth):
            for y in range(self.FieldHeight):
                self.__AliasClick(x, y)
            pass

        def SetXY(x, y):
            CombatSpell.Click = (x, y)
            return True
            pass

        def CheckWin():
            if (self.object.getCheckWin() is False):
                return

            if (len(self.AiSlots) == 0):
                self.enigmaComplete()
                pass

            self.object.setParam("CheckWin", False)
            pass

        with TaskManager.createTaskChain(Name="CombatSpellMain", Repeat=True) as tc:
            # need befor for animation etc if player durring animation leave scene and enter agiane ai move correct
            tc.addFunction(CheckWin)
            tc.addTask("AliasCombatSpellAiTurn", CombatSpell=self)
            tc.addListener(Notificator.onCombatSpellSlotClick, Filter=SetXY)
            tc.addTask("AliasCombatSpellPlayerTurn", CombatSpell=self)
            pass

        pass

    def __AliasClick(self, x, y):
        slot = self.slots[x][y]

        with TaskManager.createTaskChain(Name="CombatSpellSlotClick_%d_%d" % (x, y), Repeat=True) as tc:
            tc.addTask("TaskMovieSocketClick", SocketName=slot.SocketName, Movie=self.Movie)
            tc.addNotify(Notificator.onCombatSpellSlotClick, x, y)
            pass
        pass

    def __PlasePlayer(self, x, y):
        xm = x - 1
        xmm = x - 2

        xp = x + 1
        xpp = x + 2

        ym = y - 1
        ymm = y - 2

        yp = y + 1
        ypp = y + 2

        self.__PlasePlayerCheck((xmm, y), (xm, y), (x, y))
        self.__PlasePlayerCheck((xpp, y), (xp, y), (x, y))
        self.__PlasePlayerCheck((x, ymm), (x, ym), (x, y))
        self.__PlasePlayerCheck((x, ypp), (x, yp), (x, y))
        pass

    def __PlasePlayerCheck(self, pos1, posMidl, pos2):
        if (self.__PosLimitCheck(pos1) is False):
            return
        if (self.__PosLimitCheck(posMidl) is False):
            return
        if (self.__PosLimitCheck(pos2) is False):
            return
        slot1 = self.slots[pos1[0]][pos1[1]]
        slotMidl = self.slots[posMidl[0]][posMidl[1]]
        slot2 = self.slots[pos2[0]][pos2[1]]

        if (slot1.Type == CombatSpell.Type_Player):
            if (slotMidl.Type == CombatSpell.Type_Ai):
                if (slot2.Type == CombatSpell.Type_Player):
                    self.__SetSlotNone(slotMidl)
                    self.__SetSlotType(slotMidl, CombatSpell.Type_Player)

        pass

    def __PlasePlayerOnAi(self, x, y):
        xm = x - 1
        xp = x + 1

        ym = y - 1
        yp = y + 1

        # clock
        pos1 = (xm, ym)
        pos2 = (x, ym)
        pos3 = (xp, ym)
        pos4 = (xp, y)
        pos5 = (xp, yp)
        pos6 = (x, yp)
        pos7 = (xm, yp)
        pos8 = (xm, y)

        posMidl = (x, y)
        positionsAr = []
        positionsAr.append((pos2, pos3, pos4, posMidl))
        positionsAr.append((pos4, pos5, pos6, posMidl))
        positionsAr.append((pos6, pos7, pos8, posMidl))
        positionsAr.append((pos8, pos1, pos2, posMidl))

        for positions in positionsAr:
            if (self.__PlasePlayerOnAiCheck(positions) is True):
                return positions

        return None
        pass

    def __PlasePlayerOnAiCheck(self, positions):
        pos = positions[0]
        pos2 = positions[1]
        pos3 = positions[2]
        posMidl = positions[3]

        positionNear = 0

        if (self.__PosLimitCheck(pos) is True):
            slot = self.slots[pos[0]][pos[1]]
            if (slot.Type == CombatSpell.Type_Player):
                positionNear = positionNear + 1
                pass

        if (self.__PosLimitCheck(pos2) is True):
            slot = self.slots[pos2[0]][pos2[1]]
            if (slot.Type == CombatSpell.Type_Player):
                positionNear = positionNear + 1
                pass

        if (self.__PosLimitCheck(pos3) is True):
            slot = self.slots[pos3[0]][pos3[1]]
            if (slot.Type == CombatSpell.Type_Player):
                positionNear = positionNear + 1
                pass

        if (positionNear < 2):
            return False

        slotMidl = self.slots[posMidl[0]][posMidl[1]]
        self.__SetSlotType(slotMidl, CombatSpell.Type_Player)
        self.object.setParam("AITurn", True)
        return True
        pass

    def __PlasePlayerOnNone(self, x, y):
        slot = self.slots[x][y]
        self.__SetSlotType(slot, CombatSpell.Type_Player)
        ############# init game set 2 start player chess
        putPlayer = self.object.getStartPlayerCount()
        if (putPlayer > 1):
            putPlayer = putPlayer - 1
            self.object.setParam("StartPlayerCount", putPlayer)
            pass
        else:
            self.object.setParam("AITurn", True)
            pass
        #############
        return ((x, y),)
        pass

    def __ThinkAi(self):
        for aiSlot in self.AiSlots:
            x = aiSlot.slotX
            y = aiSlot.slotY
            result = self.__MoveAiEatPlayer(x, y)
            if (result != None):
                return result
            pass

        for aiSlot in self.AiSlots:
            x = aiSlot.slotX
            y = aiSlot.slotY
            result = self.__MoveAiRandom(x, y)
            if (result != None):
                return result
            pass

        return None

        pass

    def __MoveAiEatPlayer(self, x, y):
        xm = x - 1
        xmm = x - 2

        xp = x + 1
        xpp = x + 2

        ym = y - 1
        ymm = y - 2

        yp = y + 1
        ypp = y + 2

        positionsAr = []
        # line
        positionsAr.append(((xm, y), (xmm, y), (x, y), "L"))
        positionsAr.append(((xp, y), (xpp, y), (x, y), "R"))
        positionsAr.append(((x, ym), (x, ymm), (x, y), "T"))
        positionsAr.append(((x, yp), (x, ypp), (x, y), "D"))
        # diagonal
        positionsAr.append(((xm, ym), (xmm, ymm), (x, y), "TL"))
        positionsAr.append(((xp, yp), (xpp, ypp), (x, y), "DR"))
        positionsAr.append(((xp, ym), (xpp, ymm), (x, y), "TR"))
        positionsAr.append(((xm, yp), (xmm, ypp), (x, y), "DL"))

        for positions in positionsAr:
            if (self.__MoveAiEatCheck(positions) is True):
                return positions
            pass
        return None
        pass

    def __MoveAiRandom(self, x, y):
        xm = x - 1
        xp = x + 1

        ym = y - 1
        yp = y + 1

        positionsMove = []
        positionsMove.append(((xm, y), (x, y), "L"))
        positionsMove.append(((xp, y), (x, y), "R"))
        positionsMove.append(((x, ym), (x, y), "T"))
        positionsMove.append(((x, yp), (x, y), "D"))

        # diagonal
        positionsMove.append(((xm, ym), (x, y), "TL"))
        positionsMove.append(((xm, yp), (x, y), "DL"))
        positionsMove.append(((xp, ym), (x, y), "TR"))
        positionsMove.append(((xp, yp), (x, y), "DR"))

        while (len(positionsMove) > 0):
            rand = Mengine.rand(len(positionsMove))
            positions = positionsMove.pop(rand)
            if (self.__MoveAiRandomCheck(positions) is True):
                return positions
        return None
        pass

    def __MoveAiEatCheck(self, positions):
        posNext = positions[0]
        posMove = positions[1]
        posCurrent = positions[2]
        if (self.__PosLimitCheck(posNext) is False):
            return False
        if (self.__PosLimitCheck(posMove) is False):
            return False

        slotNext = self.slots[posNext[0]][posNext[1]]
        slotMove = self.slots[posMove[0]][posMove[1]]
        slotCurrent = self.slots[posCurrent[0]][posCurrent[1]]

        if (slotNext.Type == CombatSpell.Type_Player):
            if (slotMove.Type == CombatSpell.Type_None):
                self.__SetSlotType(slotCurrent, CombatSpell.Type_None)
                self.__SetSlotType(slotNext, CombatSpell.Type_None)
                self.__SetSlotType(slotMove, CombatSpell.Type_Ai)
                return True
        return False
        pass

    def __MoveAiRandomCheck(self, positions):
        posNext = positions[0]
        posCurrent = positions[1]
        if (self.__PosLimitCheck(posNext) is False):
            return False

        slotCurrent = self.slots[posCurrent[0]][posCurrent[1]]
        slotNext = self.slots[posNext[0]][posNext[1]]

        if (slotNext.Type == CombatSpell.Type_None):
            self.__SetSlotType(slotCurrent, CombatSpell.Type_None)
            self.__SetSlotType(slotNext, CombatSpell.Type_Ai)
            return True
        return False
        pass

    def __PosLimitCheck(self, pos):
        if (0 <= pos[0] and pos[0] < self.FieldWidth):
            if (0 <= pos[1] and pos[1] < self.FieldHeight):
                return True
        return False
        pass

    def __InitSlotType(self):
        if (len(self.object.getFieldXY()) == 0):
            Data = [[0 for col in range(self.FieldWidth)] for row in range(self.FieldHeight)]
            self.object.setParam("FieldXY", Data)
            self.__InitSlotAi()
            pass
        else:
            arrayXY = self.object.getFieldXY()
            for x in range(self.FieldWidth):
                arrayY = arrayXY[x]
                for y in range(self.FieldHeight):
                    type = arrayY[y]
                    slot = self.slots[x][y]
                    self.__SetSlotType(slot, type)
                    pass
            pass

        pass

    def __InitSlotAi(self):
        if (self.StartAiCount > self.FieldWidth * self.FieldHeight):
            Trace.trace()
            pass

        for i in range(self.StartAiCount):
            while (True):
                x = Mengine.rand(self.FieldWidth)
                y = Mengine.rand(self.FieldHeight)
                slot = self.slots[x][y]
                if (slot.Type == CombatSpell.Type_None):
                    self.__SetSlotType(slot, CombatSpell.Type_Ai)
                    break
                pass
            pass
        pass

    def __SetSlotType(self, slot, Type):
        if (Type == CombatSpell.Type_Ai):
            self.AiSlots.append(slot)
        else:
            if (slot.Type == CombatSpell.Type_Ai):
                self.AiSlots.remove(slot)
                pass
            pass

        arrayXY = self.object.getFieldXY()
        arrayY = arrayXY[slot.slotX]
        arrayY[slot.slotY] = Type
        self.object.changeParam("FieldXY", slot.slotX, arrayY)

        slot.setType(Type)
        self.SlotsUpdateVisual.append(slot)
        pass

    def __getHotSpot(self, SocketName):
        MovieSlotPointsEntity = self.Movie.getEntity()
        hotspot = MovieSlotPointsEntity.getSocket(SocketName)
        return hotspot
        pass

    def __getMovieSlot(self, x, y):
        MovieSlotPointsEntity = self.Movie.getEntity()

        id = "slot_%d_%d" % (x, y)
        CurrentSlot = MovieSlotPointsEntity.getMovieSlot(id)

        return CurrentSlot
        pass

    def TurnAi(self):
        if (self.object.getAITurn() is False):
            return None

        self.object.setParam("AITurn", False)
        result = self.__ThinkAi()
        return result
        pass

    def TurnPlayer(self):
        x = CombatSpell.Click[0]
        y = CombatSpell.Click[1]
        slot = self.slots[x][y]

        if (slot.Type == CombatSpell.Type_Player):
            return None

        if (slot.Type == CombatSpell.Type_Ai):
            result = self.__PlasePlayerOnAi(x, y)

            if (result != None):
                self.object.setParam("CheckWin", True)
                return result
            pass

        if (slot.Type == CombatSpell.Type_None):
            result = self.__PlasePlayerOnNone(x, y)
            return result
            pass

        return None
        pass

    def UpdateVisual(self):
        for slot in self.SlotsUpdateVisual:
            slot.UpdateTypeVisual()
            pass
        self.SlotsUpdateVisual = []
        pass

    def getSlot(self, pos):
        slot = self.slots[pos[0]][pos[1]]
        return slot
        pass

    def getAiEatAnimation(self, result):
        pref = result[-1]

        for id, prefAr in enumerate(self.AnimationsAi_Prefix):
            if (prefAr == pref):
                return self.Movie_AnimationsAiEat[id]
                pass
            pass

        return None
        pass

    def getAiMoveAnimation(self, result):
        pref = result[-1]

        for id, prefAr in enumerate(self.AnimationsAi_Prefix):
            if (prefAr == pref):
                return self.Movie_AnimationsAiMove[id]
                pass
            pass

        return None
        pass
