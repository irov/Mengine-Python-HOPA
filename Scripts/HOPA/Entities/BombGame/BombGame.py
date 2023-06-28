from Foundation.TaskManager import TaskManager
from HOPA.BomberManager import BomberManager
from HOPA.Entities.BombGame.BombClick import BombClick
from HOPA.Entities.BombGame.BombGameSlot import BombGameSlot
from HOPA.Entities.BombGame.BombMoving import BombMoving
from HOPA.Entities.BombGame.FlyText import FlyText
from HOPA.Entities.BombGame.ItemProto import ItemProto


Enigma = Mengine.importEntity("Enigma")


# TODO Fix movie exploushen for every slot not 1 for all Timing play

class BombGame(Enigma):
    # dir 1 Top 2 Bot 3 Left 4 Right

    Dir_Add = ((0, 0), (0, -1), (0, 1), (-1, 0), (1, 0))
    Click = (-1, -1)
    ClickMouse = (-1, -1)
    GlobalMovieInc = 0
    GlobalChainInc = 0
    GlobalTextInc = 0

    item_None_Open = None
    item_Close_Move = None
    item_Close_Block = None

    # item_Bomb_Back = None

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        pass

    def __init__(self):
        super(BombGame, self).__init__()
        self.Reinit()
        pass

    def Reinit(self):
        BombGame.Click = (-1, -1)
        BombGame.ClickMouse = (-1, -1)
        BombGame.GlobalMovieInc = 0
        BombGame.GlobalChainInc = 0
        BombGame.GlobalTextInc = 0

        BombGame.item_None_Open = None
        BombGame.item_Close_Move = None
        BombGame.item_Close_Block = None

        self.FieldWidth = 0
        self.FieldHeight = 0
        self.CellSize = 0
        self.WinGold = 0
        self.WinPoint = 0

        self.GameData = None
        self.ItemsPrototypes = []
        self.slots = []
        self.PreventSpawn = []

        self.Movie_Bar = None
        self.Movie_Text_Gold = None
        self.Movie_Text_Points = None

        self.Movie_Layer_1 = None
        self.Movie_Layer_2 = None
        self.Movie_Layer_3 = None
        self.FlyTexts = []

        self.Points_Count = 0
        self.Coint_Count = 0

        self.Movies_Gen_Glob = []
        # self.Movies_Free_Glob = []
        self.Aliase_Names_Glob = []
        pass

    def _skipEnigma(self):
        self.__Finita()
        self.enigmaComplete()
        pass

    def __Finita(self):
        for name in self.Aliase_Names_Glob:
            self.__canTT(name)
            pass

        self.Aliase_Names_Glob = []

        for mov in self.Movies_Gen_Glob:
            if mov.parent is not None:
                mov.onDestroy()
                pass
            pass

        self.Movies_Gen_Glob = []

        self.Reinit()
        pass

    def __canTT(self, Name):
        if TaskManager.existTaskChain(Name) is True:
            TaskManager.cancelTaskChain(Name)
            pass
        pass

    def _playEnigma(self):
        self.GameData = BomberManager.getGame(self.EnigmaName)
        self.FieldWidth = self.GameData.FieldWidth
        self.FieldHeight = self.GameData.FieldHeight
        self.CellSize = self.GameData.CellSize
        self.WinGold = self.GameData.WinGold
        self.WinPoint = self.GameData.WinPoints

        self.Movie_Bar = self.object.getObject("Movie_Bar")

        self.Movie_Layer_1 = self.object.getObject("Movie_Layer1")
        self.Movie_Layer_2 = self.object.getObject("Movie_Layer2")
        self.Movie_Layer_3 = self.object.getObject("Movie_Layer3")

        self.__InitItem()

        # self.__MakeMovies()
        self.__InitMovie()
        self.__InitSlots()
        self.__InitAlias()
        pass

    def _stopEnigma(self):
        pass

    def __InitItem(self):
        ItemProto.Global_Iterator = 0

        BombGame.item_None_Open = ItemProto(self, None, True).setItemName("None_Open")
        BombGame.item_Close_Move = ItemProto(self, None, True).setItemName("Close_Move")
        BombGame.item_Close_Block = ItemProto(self, None, True).setItemName("Close_Block").setColisType(True)
        # BombGame.item_Bomb_Back = ItemProto(self, None).setItemName("Bomb_Back").setColisType(True).setBombBlow(True)

        self.ItemsPrototypes.append(BombGame.item_None_Open)
        self.ItemsPrototypes.append(BombGame.item_Close_Move)
        self.ItemsPrototypes.append(BombGame.item_Close_Block)
        # self.ItemsPrototypes.append(BombGame.item_Bomb_Back)

        for itemData in self.GameData.Items.itervalues():
            item = ItemProto(self, itemData, False)
            self.ItemsPrototypes.append(item)
            if (item.BombBlow is True):
                # do invise for move etc
                item = ItemProto(self, itemData, True)
                self.ItemsPrototypes.append(item)
                pass
            pass

        for item in self.ItemsPrototypes:
            item.initSpawn()
            pass

        pass

    def getMovies(self, name):
        Movie = self.object.getObject(name)

        Movie.setEnable(True)
        Movie.setPosition((0, 0))
        return Movie
        pass

    def genBaseMovies(self, name):
        BombGame.GlobalMovieInc = BombGame.GlobalMovieInc + 1
        genName = "%s %d" % (name, BombGame.GlobalMovieInc)
        Movie = self.__genMovies(genName, name)
        MovieEntity = Movie.getEntity()
        self.Movie_Layer_1.getEntity().addChild(MovieEntity)

        Movie.setEnable(True)
        Movie.setPosition((0, 0))
        return Movie
        pass

    def genExploudMovies(self, name):
        BombGame.GlobalMovieInc = BombGame.GlobalMovieInc + 1
        genName = "%s %d" % (name, BombGame.GlobalMovieInc)
        Movie = self.__genMovies(genName, name)
        MovieEntity = Movie.getEntity()
        self.Movie_Layer_2.getEntity().addChild(MovieEntity)

        Movie.setEnable(True)
        Movie.setPosition((0, 0))
        return Movie
        pass

    def __genMovies(self, genName, name):
        Movie = self.object.generateObject(genName, name)
        self.Movies_Gen_Glob.append(Movie)
        return Movie
        pass

    # def __DestroyMovie(self, Movie):
    #     MovieEntity = Movie.getEntity()
    #     MovieEntity.removeFromParent()
    #     pass

    def __InitMovie(self):
        self.Movie = self.object.getObject("Movie_TextPoint")

        self.Movie_Text_Gold = self.__getMovieSlot("Gold")
        self.Movie_Text_Points = self.__getMovieSlot("Points")

        self.text_Gold = Mengine.createNode("TextField")
        self.text_Points = Mengine.createNode("TextField")

        self.text_Gold.setName("Text Gold")
        self.text_Points.setName("Text Points")

        self.text_Gold.setRightAlign()
        self.text_Gold.setVerticalCenterAlign()
        self.text_Gold.setFontName("Domino16_Yellow")
        self.text_Gold.setScale((2.5, 2.5, 1.0))

        self.text_Points.setRightAlign()
        self.text_Points.setVerticalCenterAlign()
        self.text_Points.setFontName("Domino16_Gray")
        self.text_Points.setScale((2.5, 2.5, 1.0))

        self.Movie_Text_Gold.addChild(self.text_Gold)
        self.Movie_Text_Points.addChild(self.text_Points)

        self.Update_Gold_Text()
        self.Update_Points_Text()
        pass

    def Create_Fly_Text(self, name, Value, slot):
        text = Mengine.createNode("TextField")
        text.setName("Text Fly %s " % (BombGame.GlobalTextInc))
        BombGame.GlobalTextInc = BombGame.GlobalTextInc + 1

        text.setCenterAlign()
        text.setVerticalCenterAlign()
        text.setFontName(name)
        text.setTextId("ID_BombGame")
        text.setTextArgs(Value)
        text.setScale((1.5, 1.5, 1.0))
        self.Movie_Layer_3.getEntity().addChild(text)
        x = slot.Pos[0] + self.CellSize / 2 - 5
        y = slot.Pos[1] + self.CellSize / 2 - 5

        flyText_Obj = FlyText(self, (x, y), text)
        flyText_Obj.Fly()
        self.FlyTexts.append(flyText_Obj)
        pass

    def Delete_Text(self, Text):
        Text.onDestroy()
        pass

    def Update_Gold_Text(self):
        self.text_Gold.setTextId("ID_BombGameGold")
        self.text_Gold.setTextArgs(self.Coint_Count)
        pass

    def Update_Points_Text(self):
        Tic = self.Movie_Bar.getDuration() / self.WinPoint * self.Points_Count
        Tic = Tic * 1000

        Movie_BarEnt = self.Movie_Bar.getEntity()
        Movie_BarEnt.setTiming(Tic)

        self.text_Points.setText(u"%s" % (self.Points_Count))
        pass

    def Check_Win(self):
        if (self.Coint_Count >= self.WinGold and self.Points_Count >= self.WinPoint):
            self.__Finita()
            self.enigmaComplete()
            pass
        pass

    def __InitSlots(self):
        self.slots = [[0 for col in range(self.FieldHeight)] for row in range(self.FieldWidth)]

        movieSlotsName = "Movie_SlotPoints"
        Movie = self.object.generateObject("Base", movieSlotsName)
        MovieSlot = self.__getMovieSlotMovie("slot", Movie)
        posBase = MovieSlot.getLocalPosition()

        for x in range(self.FieldWidth):
            for y in range(self.FieldHeight):
                posOffCell = (x * self.CellSize, y * self.CellSize)
                posNew = (
                posBase[0] + posOffCell[0] - self.CellSize / 2, posBase[1] + posOffCell[1] - self.CellSize / 2)
                Movie = self.object.generateObject("%s_%d_%d" % (movieSlotsName, x, y), movieSlotsName)
                Movie.setPosition(posOffCell)

                slot = BombGameSlot(self, x, y, posNew, Movie, "socket", self.object.getGroup())

                slot.setItemCheckSame(BombGame.item_None_Open)
                slot.UpdateTypeVisual()
                self.slots[x][y] = slot
                pass
            pass

        pass

    def __InitAlias(self):
        for x in range(self.FieldWidth):
            for y in range(self.FieldHeight):
                self.__AliasClick(x, y)
                self.__AliasPlayMovie(x, y)
            pass

        for i, item in enumerate(self.ItemsPrototypes):
            self.__AliasItemTime(item, i)
            pass

        self.__AliasFlyText()

        pass

    def __AliasFlyText(self):
        def Fly():
            for text in self.FlyTexts:
                if (text.Fly() is True):
                    self.FlyTexts.remove(text)
                    self.Delete_Text(text.Text)
                    pass
                pass
            pass

        name = "FlyTexts"
        self.Aliase_Names_Glob.append(name)

        with TaskManager.createTaskChain(Name=name, Repeat=True) as tc:
            tc.addTask("TaskFunction", Fn=Fly)
            tc.addTask("TaskDelay", Time=0.02 * 1000)  # speed fix
            pass
        pass

    def __AliasClick(self, x, y):
        slot = self.slots[x][y]

        def SetXY():
            # print  "%d %d "%(x,y), slot," ", slot.Item
            BombGame.Click = (x, y)
            BombGame.ClickMouse = Mengine.getCursorPosition()
            pass

        name = "CombatSpellSlotClick_%d_%d" % (x, y)
        self.Aliase_Names_Glob.append(name)

        with TaskManager.createTaskChain(Name=name, Repeat=True) as tc:
            tc.addTask("TaskMovieSocketClick", SocketName=slot.SocketName, Movie=slot.Movie, isDown=True)
            tc.addTask("TaskFunction", Fn=SetXY)
            tc.addTask("TaskFunction", Fn=self.__genChain)
            pass
        pass

    def __AliasPlayMovie(self, x, y):
        slot = self.slots[x][y]

        Movie = [None]

        def setMovie():
            Movie[0] = [(slot.MovieIdle, True)]
            pass

        name = "slotMoviePlay_%d_%d" % (x, y)
        self.Aliase_Names_Glob.append(name)

        with TaskManager.createTaskChain(Name=name, Repeat=True) as tc:
            tc.addTask("TaskFunction", Fn=setMovie)
            tc.addTask("AliasMultyplMovePlay", Movies=Movie)
            tc.addTask("TaskDelay", Time=0.1 * 1000)  # speed fix
            pass
        pass

    def __genChain(self):
        BombGame.GlobalChainInc = BombGame.GlobalChainInc + 1
        name = "BombGameSlotClick_%d_%d_%d" % (BombGame.Click[0], BombGame.Click[1], BombGame.GlobalChainInc)
        # self.Aliase_Names_Glob.append(name)

        with TaskManager.createTaskChain(Name=name) as tc:
            tc.addTask("AliasBombGamePlayerClickProcces", BombGame=self)
            tc.addTask("TaskFunction", Fn=self.Check_Win)
            pass

        pass

    def __AliasItemTime(self, item, i):
        SpawnDelay = item.getSpawnDelay()
        if (SpawnDelay <= 0):
            return
            pass
        StartSpawnDelay = item.getStartSpawnDelay()

        SpawnDelayPointer = [SpawnDelay]

        SpawnIntervaleChangeOn = item.getSpawnIntervaleChangeOn()
        SpawnIntervaleChangeOnIntervale = item.getSpawnIntervaleChangeOnIntervale()
        SpawnIntervaleMinVal = item.getSpawnIntervaleMinVal()

        def SpawnItem():
            self.__SpawnRandom(item)
            pass

        def ChangeSpawnTime(SpawnDelayPointer):
            SpawnDelayPointer[0] = SpawnDelayPointer[0] - SpawnIntervaleChangeOn
            if (SpawnDelayPointer[0] < SpawnIntervaleMinVal):
                SpawnDelayPointer[0] = SpawnIntervaleMinVal
            pass

        name = "BombGameSpawner%d" % (i)
        self.Aliase_Names_Glob.append(name)

        with TaskManager.createTaskChain(Name=name) as tc:
            tc.addTask("TaskDelay", Time=StartSpawnDelay)
            with tc.addParallelTask(2) as (tc_Delay, tc_Spawn):
                with tc_Delay.addRepeatTask() as (tc_Delay_do, tc_Delay_until):
                    tc_Delay_do.addTask("TaskDelay", Time=SpawnIntervaleChangeOnIntervale)
                    tc_Delay_do.addTask("TaskFunction", Fn=ChangeSpawnTime, Args=(SpawnDelayPointer,))

                    tc_Delay_until.addTask("TaskListener", ID=Notificator.onBombGameEnd)
                    pass

                with tc_Spawn.addRepeatTask() as (tc_do, tc_until):
                    tc_do.addTask("TaskDelayPointer", TimePointer=SpawnDelayPointer)
                    tc_do.addTask("TaskFunction", Fn=SpawnItem)

                    tc_until.addTask("TaskListener", ID=Notificator.onBombGameEnd)
                    pass
                pass

            pass
        pass

    def __SpawnRandom(self, item):
        def resPrev(pos):
            for bomb in self.PreventSpawn:
                if (pos in bomb.SpawnPrevent):
                    return False
                    pass

                if (len(bomb.SpawnPrevent) == 0):
                    self.PreventSpawn.remove(bomb)
                    pass
                pass
            return True
            pass

        randAr = []
        for x in range(self.FieldWidth):
            for y in range(self.FieldHeight):
                slot = self.slots[x][y]
                if (slot.Item == BombGame.item_None_Open):
                    pos = (slot.slotX, slot.slotY)
                    if (resPrev(pos) is True):
                        rand = Mengine.rand(100)
                        randAr.append((rand, slot))
                        pass
                    pass
                pass
            pass

        if (len(randAr) == 0):
            return
            pass

        randAr.sort(key=lambda tup: tup[0])
        slotMin = randAr[0]
        slot = slotMin[1]
        slot.setItemForce(item)
        slot.UpdateTypeVisual()
        pass

    def StartBombBlov(self, slotBase):
        sloteExp = []

        self.__BombBlov(slotBase, sloteExp)
        return sloteExp
        pass

    def __BombBlov(self, slotStart, sloteExp):
        self.__AddSlotExpl(slotStart, sloteExp)
        dir = slotStart.Item.ItemData.TypeExtraValue
        x = slotStart.slotX
        y = slotStart.slotY

        ##################################
        def blowSlot(slot, sloteExp):
            item = slot.Item
            if (self.__AddSlotExpl(slot, sloteExp) is False):
                return
                pass

            if (item.BombBlow is True and item.getItemType() != 3):
                self.__BombBlov(slot, sloteExp)
                pass
            pass

        if (dir[1] == "R"):
            randAr = []
            for x in range(self.FieldWidth):
                for y in range(self.FieldHeight):
                    slot = self.slots[x][y]
                    rand = Mengine.rand(100)
                    randAr.append((rand, slot))
                    pass
                pass
            randAr.sort(key=lambda tup: tup[0])

            for i in range(dir[0]):
                if (len(randAr) == 0):
                    break
                    pass
                slot = randAr.pop(0)[1]
                blowSlot(slot, sloteExp)
                pass

            pass
        else:
            for d in dir:
                pos = (x + d[0], y + d[1])
                if (self.__PosLimitCheck(pos) is False):
                    continue
                    pass

                slot = self.getSlot(pos)
                blowSlot(slot, sloteExp)
                pass
            pass
        pass

    def __AddSlotExpl(self, slot, sloteExp):
        if (slot in sloteExp):
            return False
            pass
        sloteExp.append(slot)
        return True
        pass

    ###############################
    def __PosLimitCheck(self, pos):
        if (0 <= pos[0] and pos[0] < self.FieldWidth):
            if (0 <= pos[1] and pos[1] < self.FieldHeight):
                return True
        return False
        pass

    def __getHotSpot(self, SocketName):
        MovieSlotPointsEntity = self.Movie.getEntity()
        hotspot = MovieSlotPointsEntity.getSocket(SocketName)
        return hotspot
        pass

    def __getMovieSlot(self, id):
        MovieSlotPointsEntity = self.Movie.getEntity()
        CurrentSlot = MovieSlotPointsEntity.getMovieSlot(id)
        return CurrentSlot
        pass

    def __getHotSpotMovie(self, SocketName, Movie):
        MovieSlotPointsEntity = Movie.getEntity()
        hotspot = MovieSlotPointsEntity.getSocket(SocketName)
        return hotspot
        pass

    def __getMovieSlotMovie(self, id, Movie):
        MovieSlotPointsEntity = Movie.getEntity()
        CurrentSlot = MovieSlotPointsEntity.getMovieSlot(id)
        return CurrentSlot
        pass

    def getSlotDir(self, slot, dir):
        diradd = BombGame.Dir_Add[dir]
        pos = (slot.slotX + diradd[0], slot.slotY + diradd[1])
        if (self.__PosLimitCheck(pos) is False):
            return None
            pass

        slot = self.slots[pos[0]][pos[1]]
        return slot
        pass

    def getSlot(self, pos):
        if (self.__PosLimitCheck(pos) is False):
            return None
            pass
        slot = self.slots[pos[0]][pos[1]]
        return slot
        pass

    def getItemProto(self, Name):
        for item in self.ItemsPrototypes:
            if (item.Name == Name):
                return item
                pass
            pass
        return None
        pass

    def getItemProtoById(self, Id):
        return self.ItemsPrototypes[Id]
        pass

    def createBombMove(self, pos):
        bomb = BombMoving(self, pos)
        return bomb
        pass

    def createBombClick(self, pos):
        bomb = BombClick(self, pos)
        return bomb
        pass
