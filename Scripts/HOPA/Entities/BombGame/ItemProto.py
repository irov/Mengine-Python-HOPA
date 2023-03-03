Enigma = Mengine.importEntity("Enigma")


class ItemProto(object):
    Global_Iterator = 0

    Type_Simple = 0
    Type_Bomb_Click = 1
    Type_Bomb_Move = 2

    def __init__(self, Game, ItemData, Inivese):
        self.Game = Game
        self.ItemData = ItemData
        self.ArrayPos = ItemProto.Global_Iterator
        ItemProto.Global_Iterator = ItemProto.Global_Iterator + 1

        self.Name = None
        self.BombBlow = False
        self.Colis = False

        self.SpawnItems = []  # tuple what and chanse
        self.Inivese = Inivese

        if (ItemData is not None):
            self.Name = ItemData.ItemName
            self.Colis = True

            if (self.ItemData.ItemType == 1 or self.ItemData.ItemType == 2 or self.ItemData.ItemType == 3):
                self.BombBlow = True
                pass

            self.checkMovie(self.ItemData.MovieIdle)
            self.checkMovie(self.ItemData.MoviePreExploud)
            self.checkMovie(self.ItemData.MovieExploud)
            self.checkMovie(self.ItemData.MovieMoveTop)
            self.checkMovie(self.ItemData.MovieMoveTopOut)
            self.checkMovie(self.ItemData.MovieMoveDown)
            self.checkMovie(self.ItemData.MovieMoveDownOut)
            self.checkMovie(self.ItemData.MovieMoveRight)
            self.checkMovie(self.ItemData.MovieMoveRightOut)
            self.checkMovie(self.ItemData.MovieMoveLeft)
            self.checkMovie(self.ItemData.MovieMoveLeftOut)

            pass
        pass

    def initSpawn(self):
        if (self.ItemData is None):
            return
            pass

        for spawn in self.ItemData.SpawnDatas:
            Name = spawn.What
            item = self.Game.getItemProto(Name)
            tuplll = (item, spawn.Chance)
            self.SpawnItems.append(tuplll)
            pass

        self.SpawnItems.sort(key=lambda tup: tup[1], reverse=True)
        pass

    def ItemRandom(self):
        for spawnTupl in self.SpawnItems:
            spawnItem = spawnTupl[0]
            spawnChanse = spawnTupl[1]
            rand = Mengine.rand(100)
            if (rand < spawnChanse):
                return spawnItem
                pass
            pass
        return None
        pass

    def PrccoesPick(self, slot):
        if (self.ItemData is None):
            return
        type = self.ItemData.ItemType
        if (type < 100):
            return

        if (type == 100):
            self.Game.Coint_Count = self.Game.Coint_Count + self.ItemData.TypeExtraValue
            self.Game.Coint_Count = int(self.Game.Coint_Count)
            self.Game.Update_Gold_Text()
            self.Game.Create_Fly_Text("Domino16_Yellow", int(self.ItemData.TypeExtraValue), slot)
            pass

        if (type == 101):
            # self.Game.Coint_Count = self.Game.Coint_Count + self.ItemData.TypeExtraValue
            # self.Game.Coint_Count = int (self.Game.Coint_Count)
            # self.Game.Update_Gold_Text()
            # self.Game.Create_Fly_Text("Domino16_Yellow", int(self.ItemData.TypeExtraValue), slot)
            pass

        pass

    def AddPoints(self, exploudDict, slot):
        # filter invise
        itemsBlowCountNotInvise = {}
        # add not invise
        for key, value in exploudDict.iteritems():
            if (key.Inivese is False):
                itemsBlowCountNotInvise[key] = value
                pass
            pass

        # now add invise if have not invise perent add to it else add self
        for key, value in exploudDict.iteritems():
            if (key.ItemData is not None and key.Inivese is True):
                idd = key.ArrayPos - 1
                parent = self.Game.getItemProtoById(idd)
                if (parent in itemsBlowCountNotInvise):
                    newVal = itemsBlowCountNotInvise[parent] + value
                    itemsBlowCountNotInvise[parent] = newVal
                    pass
                else:
                    itemsBlowCountNotInvise[key] = value
                    pass
                pass
            pass

        # now plus points
        point_Pool = 0
        for key, value in itemsBlowCountNotInvise.iteritems():
            points = key.getExploudPoints(value)
            point_Pool = point_Pool + points
            pass

        self.Game.Points_Count = self.Game.Points_Count + point_Pool
        self.Game.Points_Count = int(self.Game.Points_Count)
        self.Game.Update_Points_Text()
        self.Game.Create_Fly_Text("Domino16", int(point_Pool), slot)
        pass

    def getExploudPoints(self, count):
        if (self.ItemData is None):
            return 0
        lenBlow = len(self.ItemData.BlowPoints)
        if (lenBlow == 0):
            return 0
        if (lenBlow <= count):
            count = lenBlow - 1
            pass
        points = self.ItemData.BlowPoints[count]
        return points
        pass

    def setItemName(self, Name):
        self.Name = Name
        return self
        pass

    def setColisType(self, colis):
        self.Colis = colis
        return self
        pass

    def setBombBlow(self, blow):
        self.BombBlow = blow
        return self
        pass

    def checkMovie(self, Name):
        if (Name is None):
            return
        movie = self.Game.object.getPrototype(Name)
        if (movie is None):
            Trace.trace()
            pass
        pass

    ###################################
    def getItemType(self):
        if (self.ItemData is None):
            return -1
            pass

        return self.ItemData.ItemType
        pass

    def getStartSpawnDelay(self):
        if (self.ItemData is None or self.Inivese is True):
            return -1
            pass

        return self.ItemData.SpawnStart
        pass

    def getSpawnDelay(self):
        if (self.ItemData is None or self.Inivese is True):
            return -1
            pass

        return self.ItemData.SpawnIntervale
        pass

    def getSpawnIntervaleChangeOn(self):
        if (self.ItemData is None or self.Inivese is True):
            return -1
            pass

        return self.ItemData.SpawnIntervaleChangeOn
        pass

    def getSpawnIntervaleChangeOnIntervale(self):
        if (self.ItemData is None or self.Inivese is True):
            return -1
            pass

        return self.ItemData.SpawnIntervaleChangeOnIntervale
        pass

    def getSpawnIntervaleMinVal(self):
        if (self.ItemData is None or self.Inivese is True):
            return -1
            pass

        return self.ItemData.SpawnIntervaleMinVal
        pass

    def getObjectType(self):
        if (self.ItemData is None):
            return None
            pass

        return self.ItemData.ItemType
        pass

    def getIdleMovieName(self):
        if (self.ItemData is None or self.Inivese is True):
            return None
            pass

        return self.ItemData.MovieIdle
        pass

    def getExploudMovieName(self):
        if (self.ItemData is None):
            return None
            pass

        return self.ItemData.MovieExploud
        pass

    def getPreExploudMovieName(self):
        if (self.ItemData is None or self.Inivese is True):
            return None
            pass

        return self.ItemData.MoviePreExploud
        pass

    def getMoveMovieName(self, dir):
        # dir 1 Top 2 Bot 3 Left 4 Right
        if dir == 0:
            return None
        elif dir == 1:
            return self.ItemData.MovieMoveTop
        elif dir == 2:
            return self.ItemData.MovieMoveDown
        elif dir == 3:
            return self.ItemData.MovieMoveLeft
        elif dir == 4:
            return self.ItemData.MovieMoveRight
        return None
        pass

    def getMoveMovieNameOut(self, dir):
        # dir 1 Top 2 Bot 3 Left 4 Right
        if dir == 0:
            return None
        elif dir == 1:
            return self.ItemData.MovieMoveTopOut
        elif dir == 2:
            return self.ItemData.MovieMoveDownOut
        elif dir == 3:
            return self.ItemData.MovieMoveLeftOut
        elif dir == 4:
            return self.ItemData.MovieMoveRightOut
        return None
        pass

    def __str__(self):
        str = "Name %s data %s" % (self.Name, self.ItemData)
        return str
