from Foundation.DatabaseManager import DatabaseManager


class ProtoManager(object):     # fixme ?????

    def __init__(self):
        self.FirstField = None
        self.Fields = {}
        self.FieldTypes = {}

    def InitField(self, *fields):
        self.FirstField = fields[0]

        for fieldName in fields:
            self.Fields[fieldName] = []
            self.FieldTypes[fieldName] = FieldType_String

    def InitTypes(self, *fieldTypes):
        for name, type in fieldTypes:
            self.FieldTypes[name] = type

    def Fill(self, Record):
        skip = self.__SkipRecord(Record)
        if skip is True:
            return

        for fieldName, value in self.Fields:
            SpawnStart = Record.get("SpawnStart", 0)
            self.Fields[fieldName] = []

    def __SkipRecord(self, Record):
        FirstVal = Record.get(self.FirstField, None)
        if FirstVal is None or FirstVal[0] == "#":
            return True
        return False


class BomberBoxManager(object):
    @staticmethod
    def loadParams(module, param):
        pass


class BomberBombSlideManager(object):
    @staticmethod
    def loadParams(module, param):
        pass


class BomberBombClickManager(object):
    @staticmethod
    def loadParams(module, param):
        pass


class BomberSpawnManager(object):
    @staticmethod
    def loadSpawn(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            if Name is None or Name[0] == "#":
                continue

            if (BomberManager.hasGame(Name) is True):
                Trace.trace()
                continue

            SpawnName = record.get("SpawnName")
            ##################################
            FieldWidth = record.get("FieldWidth")
            FieldWidth = int(FieldWidth)

            FieldHeight = record.get("FieldHeight")
            FieldHeight = int(FieldHeight)

            CellSize = record.get("CellSize")
            CellSize = int(CellSize)

            WinGold = record.get("WinGold", 0)
            WinGold = int(WinGold)

            WinPoints = record.get("WinPoints", 0)
            WinPoints = int(WinPoints)
            ##################################
            Game = BomberManager.GameData(Name, FieldWidth, FieldHeight, CellSize, WinGold, WinPoints)
            BomberManager.Games[Name] = Game
            BomberManager.loadGame(module, Name, Game)
            BomberManager.loadSpawnItems(module, SpawnName, Game)

        return True



class BomberManager(object):
    ###################  ###################  ###################  ###################
    Items = {}

    class ItemGameParams(object):
        def __init__(self, name, itemType, Parametrs):
            self.Name = name
            self.Type = itemType
            self.ItemParameters = Parametrs
            self.SpawnParameters = {}
            self.SpawnDropParameters = {}

    @staticmethod
    def AddItem(itemName, ItemParameters, itemType):
        if BomberManager.PrintTrace(BomberManager.Items.has_key(itemName) is True,
                                    "Item with name %s already loadet " % (itemName)):
            return

        item = BomberManager.ItemGameParams(itemName, ItemParameters, itemType)

        BomberManager.Items[itemName] = item

    @staticmethod
    def SetItemSpawn(itemName, SpawnParameters):
        if BomberManager.PrintTrace(BomberManager.Items.has_key(itemName) is False,
                                    "can't find Item with name %s" % (itemName)):
            return
        BomberManager.Items[itemName].SpawnParameters = SpawnParameters

    @staticmethod
    def SetItemSpawnDrop(itemName, SpawnDropParameters):
        if BomberManager.PrintTrace(BomberManager.Items.has_key(itemName) is False,
                                    "can't find Item with name %s" % (itemName)):
            return
        BomberManager.Items[itemName].SpawnDropParameters = SpawnDropParameters

    @staticmethod
    def LoadItems(itemName, SpawnDropParameters):
        if BomberManager.PrintTrace(BomberManager.Items.has_key(itemName) is False,
                                    "can't find Item with name %s" % (itemName)):
            return
        BomberManager.Items[itemName].SpawnDropParameters = SpawnDropParameters

    @staticmethod
    def PrintTrace(Bool, Text):
        if Bool is True:
            Trace.log("Manager", 0, Text)
        return Bool

    @staticmethod
    def _MakeDict(record, *parameters):
        Dict = {}
        for param in parameters:
            Dict[param] = record.get(param)
        return Dict

    ###################  ###################  ###################  ###################

    Games = {}

    class Item(object):
        def __init__(self, Game, ItemName, ItemType, TypeExtraValue, BlowPoints, Intervales, MovieIdle, Movies):
            self.Game = Game
            self.ItemName = ItemName
            self.ItemType = ItemType

            self.TypeExtraValue = TypeExtraValue
            self.BlowPoints = BlowPoints

            self.SpawnStart = Intervales[0]
            self.SpawnIntervale = Intervales[1]
            self.SpawnIntervaleChangeOn = Intervales[2]
            self.SpawnIntervaleChangeOnIntervale = Intervales[3]
            self.SpawnIntervaleMinVal = Intervales[4]

            self.MovieIdle = MovieIdle

            self.MoviePreExploud = Movies[0]
            self.MovieExploud = Movies[1]

            self.MovieMoveTop = Movies[2]
            self.MovieMoveTopOut = Movies[3]

            self.MovieMoveDown = Movies[4]
            self.MovieMoveDownOut = Movies[5]

            self.MovieMoveRight = Movies[6]
            self.MovieMoveRightOut = Movies[7]

            self.MovieMoveLeft = Movies[8]
            self.MovieMoveLeftOut = Movies[9]

            self.SpawnDatas = []

        def addSpawnData(self, data):
            self.SpawnDatas.append(data)

        def __str__(self):
            str1 = "ItemName %s ItemType %s" % (self.ItemName, self.ItemType)
            str2 = "SpawnStart %s  SpawnIntervale %s  SpawnIntervaleChangeOn %s  SpawnIntervaleChangeOnIntervale %s  SpawnIntervaleMinVal %s " % (
            self.SpawnStart, self.SpawnIntervale, self.SpawnIntervaleChangeOn, self.SpawnIntervaleChangeOnIntervale,
            self.SpawnIntervaleMinVal)
            str3 = "MovieIdle %s" % (self.MovieIdle)
            str4 = "MoviePreExploud %s MovieExploud %s  MovieMoveTop %s  MovieMoveDown %s  MovieMoveRight %s  MovieMoveLeft %s " % (
            self.MoviePreExploud, self.MovieExploud, self.MovieMoveTop, self.MovieMoveDown, self.MovieMoveRight,
            self.MovieMoveLeft)
            str = "%s %s %s %s" % (str1, str2, str3, str4)
            return str

    class SpawnData(object):
        def __init__(self, From, What, Chance):
            self.From = From
            self.What = What
            self.Chance = Chance

        def __str__(self):
            str = "From %s What %s Chance %s " % (self.From, self.What, self.Chance)
            return str

    class GameData(object):
        def __init__(self, Name, FieldWidth, FieldHeight, CellSize, WinGold, WinPoints):
            self.Name = Name
            self.FieldWidth = FieldWidth
            self.FieldHeight = FieldHeight
            self.CellSize = CellSize

            self.WinGold = WinGold
            self.WinPoints = WinPoints

            self.Items = {}
            self.SpawnDatas = []

        def addItem(self, item):
            for itemInName in self.Items:
                if (itemInName == item.ItemName):
                    Trace.log("Manager", 0, "BomberManager Can't add Item in GameData '%s' with Name '%s' , Item with such name already in" % (
                        self.Name, item.ItemName))
                    return
            self.Items[item.ItemName] = item

        def addSpawnItem(self, item):
            if (item.From not in self.Items):
                Trace.log("Manager", 0, "BomberManager Can't find From Item in GameData '%s' with Name '%s'" % (self.Name, item.From))
                return

            if (item.What not in self.Items):
                Trace.log("Manager", 0, "BomberManager Can't find What Item in GameData '%s' with Name '%s'" % (self.Name, item.What))
                return

            self.SpawnDatas.append(item)

            fromItem = self.Items[item.From]

            fromItem.addSpawnData(item)
            Trace.msg(item)

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            if Name is None or Name[0] == "#":
                continue

            if (BomberManager.hasGame(Name) is True):
                Trace.log("Manager", 0, "BomberManager.loadGames game wtih name Already Loadet :", Name)
                continue

            SpawnName = record.get("SpawnName")
            ##################################
            FieldWidth = record.get("FieldWidth")
            FieldWidth = int(FieldWidth)

            FieldHeight = record.get("FieldHeight")
            FieldHeight = int(FieldHeight)
            CellSize = record.get("CellSize")
            CellSize = int(CellSize)

            WinGold = record.get("WinGold", 0)
            WinGold = int(WinGold)

            WinPoints = record.get("WinPoints", 0)
            WinPoints = int(WinPoints)
            ##################################
            Game = BomberManager.GameData(Name, FieldWidth, FieldHeight, CellSize, WinGold, WinPoints)
            BomberManager.Games[Name] = Game
            # BomberManager.loadGame(module, Name, Game)
            # BomberManager.loadSpawnItems(module, SpawnName, Game)

        return True

    @staticmethod
    def loadGame(module, param, Game):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ItemName = record.get("ItemName")
            if ItemName is None or ItemName[0] == "#":
                continue

            ItemType = record.get("ItemType")

            TypeExtraValue = record.get("TypeExtraValue", 0)
            if (ItemType != 1 and ItemType != 2 and ItemType != 3):
                TypeExtraValue = float(TypeExtraValue)
            else:
                TypeExtraValue = BomberManager.__Pars_Bomb_Blow(TypeExtraValue)

            BlowPoints = record.get("BlowPoints", "0")
            BlowPoints = BlowPoints.split(',')
            for id, intt in enumerate(BlowPoints):
                BlowPoints[id] = int(intt)

            SpawnStart = record.get("SpawnStart", 0)
            SpawnStart = float(SpawnStart)

            SpawnIntervale = record.get("SpawnIntervale", -1)
            SpawnIntervale = float(SpawnIntervale)

            SpawnIntervaleChangeOn = record.get("SpawnIntervaleChangeOn", -1)
            SpawnIntervaleChangeOn = float(SpawnIntervaleChangeOn)

            SpawnIntervaleChangeOnIntervale = record.get("SpawnIntervaleChangeOnIntervale", -1)
            SpawnIntervaleChangeOnIntervale = float(SpawnIntervaleChangeOnIntervale)

            SpawnIntervaleMinVal = record.get("SpawnIntervaleMinVal", -1)
            SpawnIntervaleMinVal = float(SpawnIntervaleMinVal)

            MovieIdle = record.get("MovieIdle")

            MoviePreExploud = record.get("MoviePreExploud", None)

            MovieExploud = record.get("MovieExploud", None)
            MovieMoveTop = record.get("MovieMoveTop", None)
            MovieMoveTopOut = record.get("MovieMoveTopOut", None)
            MovieMoveDown = record.get("MovieMoveDown", None)
            MovieMoveDownOut = record.get("MovieMoveDownOut", None)
            MovieMoveRight = record.get("MovieMoveRight", None)
            MovieMoveRightOut = record.get("MovieMoveRightOut", None)
            MovieMoveLeft = record.get("MovieMoveLeft", None)
            MovieMoveLeftOut = record.get("MovieMoveLeftOut", None)

            intervales = [SpawnStart, SpawnIntervale, SpawnIntervaleChangeOn, SpawnIntervaleChangeOnIntervale,
                SpawnIntervaleMinVal]
            movie = [MoviePreExploud, MovieExploud, MovieMoveTop, MovieMoveTopOut, MovieMoveDown, MovieMoveDownOut,
                MovieMoveRight, MovieMoveRightOut, MovieMoveLeft, MovieMoveLeftOut]

            item = BomberManager.Item(Game, ItemName, ItemType, TypeExtraValue,
                                      BlowPoints, intervales, MovieIdle, movie)

            Game.addItem(item)

        return True

    @staticmethod
    def __Pars_Bomb_Blow(Stringg):
        Stringg = Stringg.replace(" ", "")
        dir = []
        if (Stringg[-1] == "R"):
            Stringg = Stringg.replace("R", "")
            r_Count = int(Stringg)
            dir.append(r_Count)
            dir.append("R")
            return dir
        Stringg = Stringg.split(';')

        for sec in Stringg:
            secCL = sec.replace("(", "")
            secCL = secCL.replace(")", "")

            secCL = secCL.split(':')

            fromVAL = secCL[0].split(',')
            ToVAL = secCL[1].split(',')

            x_From = fromVAL[0]
            x_From = int(x_From)
            y_From = fromVAL[1]
            y_From = int(y_From)

            x_to = ToVAL[0]
            x_to = int(x_to)
            y_to = ToVAL[1]
            y_to = int(y_to)

            for y in range(y_From, y_to + 1):
                for x in range(x_From, x_to + 1):
                    tup = (x, y)
                    dir.append(tup)

        return dir

    @staticmethod
    def loadSpawnItems(module, param, Game):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            FromItem = record.get("FromItem")
            if FromItem is None or FromItem[0] == "#":
                continue
            WhatItem = record.get("WhatItem")

            SpawnChance = record.get("SpawnChance")
            SpawnChance = float(SpawnChance)

            spawnItem = BomberManager.SpawnData(FromItem, WhatItem, SpawnChance)

            if (SpawnChance > 100):
                Trace.log("Manager", 0, "Spawn Item error SpawnChance > 100 ", spawnItem)
            elif (SpawnChance < 0):
                Trace.log("Manager", 0, "Spawn Item error SpawnChance < 0 ", spawnItem)

            Game.addSpawnItem(spawnItem)

        return True

    @staticmethod
    def hasGame(name):
        return name in BomberManager.Games

    @staticmethod
    def getGame(name):
        if (BomberManager.hasGame(name) is False):
            Trace.log("Manager", 0, "BomberManager.getGame can't find game with Name ", name)
            return None
        return BomberManager.Games[name]
