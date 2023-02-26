from Foundation.DatabaseManager import DatabaseManager

class ProtoManager(object):

    def __init__(self):
        self.FirstField = None
        self.Fields = {}
        self.FieldTypes = {}
        pass

    def InitField(self, *fields):
        self.FirstField = fields[0]

        for fieldName in fields:
            self.Fields[fieldName] = []
            self.FieldTypes[fieldName] = FieldType_String
            pass
        pass

    def InitTypes(self, *fieldTypes):
        for name, type in fieldTypes:
            self.FieldTypes[name] = type
            pass
        pass

    def Fill(self, Record):
        skip = self.__SkipRecord(Record)
        if skip is True:
            return
            pass

        for key, value in self.Fields:
            SpawnStart = record.get("SpawnStart", 0)
            Fields[field] = []
            pass
        pass

    def __SkipRecord(self, Record):
        FirstVal = record.get(self.FirstField, None)
        if FirstVal is None or FirstVal[0] == "#":
            return True
            pass
        return False
        pass

    # for record in records:
    #       ItemName = record.get("ItemName")
    #       if ItemName is None or ItemName[0] == "#":
    #           continue
    #           pass
    #
    #
    #       ItemType = record.get("ItemType")
    #
    #       TypeExtraValue = record.get("TypeExtraValue", 0)
    #       if(ItemType != 1 and ItemType != 2 and ItemType != 3):
    #           TypeExtraValue = float(TypeExtraValue)
    #           pass
    #       else:
    #           TypeExtraValue = BomberManager.__Pars_Bomb_Blow(TypeExtraValue)
    #           pass
    #
    #
    #       BlowPoints = record.get("BlowPoints", "0")
    #       BlowPoints = BlowPoints.split(',')
    #       for id, intt in enumerate(BlowPoints):
    #           BlowPoints[id] = int(intt)
    #           pass
    #
    #       SpawnStart = record.get("SpawnStart", 0)
    #       SpawnStart = float(SpawnStart)
    #
    #       SpawnIntervale = record.get("SpawnIntervale", -1)
    #       SpawnIntervale = float(SpawnIntervale)
    #
    #       SpawnIntervaleChangeOn = record.get("SpawnIntervaleChangeOn", -1)
    #       SpawnIntervaleChangeOn = float(SpawnIntervaleChangeOn)
    #
    #       SpawnIntervaleChangeOnIntervale = record.get("SpawnIntervaleChangeOnIntervale", -1)
    #       SpawnIntervaleChangeOnIntervale = float(SpawnIntervaleChangeOnIntervale)
    #
    #       SpawnIntervaleMinVal = record.get("SpawnIntervaleMinVal", -1)
    #       SpawnIntervaleMinVal = float(SpawnIntervaleMinVal)
    #
    #       MovieIdle = record.get("MovieIdle")
    #
    #       MoviePreExploud = record.get("MoviePreExploud", None)
    #
    #       MovieExploud = record.get("MovieExploud", None)
    #       MovieMoveTop = record.get("MovieMoveTop", None)
    #       MovieMoveTopOut = record.get("MovieMoveTopOut", None)
    #       MovieMoveDown = record.get("MovieMoveDown", None)
    #       MovieMoveDownOut = record.get("MovieMoveDownOut", None)
    #       MovieMoveRight = record.get("MovieMoveRight", None)
    #       MovieMoveRightOut = record.get("MovieMoveRightOut", None)
    #       MovieMoveLeft = record.get("MovieMoveLeft", None)
    #       MovieMoveLeftOut = record.get("MovieMoveLeftOut", None)
    #
    #       intervales = [SpawnStart, SpawnIntervale, SpawnIntervaleChangeOn, SpawnIntervaleChangeOnIntervale, SpawnIntervaleMinVal]
    #       movie = [MoviePreExploud, MovieExploud, MovieMoveTop, MovieMoveTopOut, MovieMoveDown, MovieMoveDownOut, MovieMoveRight, MovieMoveRightOut, MovieMoveLeft, MovieMoveLeftOut]
    #
    #       item = BomberManager.Item(Game, ItemName, ItemType, TypeExtraValue, BlowPoints, intervales, MovieIdle, movie)
    #
    #       Game.addItem(item)
    #       pass

    pass

class BomberBoxManager(object):
    @staticmethod
    def loadParams(module, param):
        pass
    pass

class BomberBombSlideManager(object):
    @staticmethod
    def loadParams(module, param):
        pass
    pass

class BomberBombClickManager(object):
    @staticmethod
    def loadParams(module, param):
        pass
    pass

class BomberSpawnManager(object):
    @staticmethod
    def loadSpawn(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            if Name is None or Name[0] == "#":
                continue
                pass

            if (BomberManager.hasGame(Name) is True):
                Trace.trace()
                continue
                pass

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
            BomberManager.__loadGame(module, Name, Game)
            BomberManager.__loadSpawnItems(module, SpawnName, Game)
            pass

        return True
        pass
    pass

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
            pass
        pass

    @staticmethod
    def AddItem(itemName, ItemParameters, itemType):
        if PrintTrace(BomberManager.Items.has_key(itemName) is True, "Item with name %s already loadet " % (itemName)):
            return
            pass

        item = BomberManager.ItemGameParams(itemName, ItemParameters, itemType)

        BomberManager.Items[itemName] = item
        pass

    @staticmethod
    def SetItemSpawn(itemName, SpawnParameters):
        if PrintTrace(BomberManager.Items.has_key(itemName) is False, "can't find Item with name %s" % (itemName)):
            return
            pass

        BomberManager.Items[itemName].SpawnParameters = SpawnParameters
        pass

    @staticmethod
    def SetItemSpawnDrop(itemName, SpawnDropParameters):
        if PrintTrace(BomberManager.Items.has_key(itemName) is False, "can't find Item with name %s" % (itemName)):
            return
            pass

        BomberManager.Items[itemName].SpawnDropParameters = SpawnDropParameters
        pass

    @staticmethod
    def LoadItems(itemName, SpawnDropParameters):
        if PrintTrace(BomberManager.Items.has_key(itemName) is False, "can't find Item with name %s" % (itemName)):
            return
            pass

        BomberManager.Items[itemName].SpawnDropParameters = SpawnDropParameters
        pass

    def PrintTrace(self, Bool, Text):
        if Bool is True:
            print(Text)
            Trace.trace()
            pass
        return Bool
        pass

    @staticmethod
    def _MakeDict(record, *parameters):
        Dict = {}
        for param in parameters:
            Dict[param] = record.get(param)
            pass
        return Dict
        pass

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
            pass

        def addSpawnData(self, data):
            self.SpawnDatas.append(data)
            pass

        def __str__(self):
            str1 = "ItemName %s ItemType %s" % (self.ItemName, self.ItemType)
            str2 = "SpawnStart %s  SpawnIntervale %s  SpawnIntervaleChangeOn %s  SpawnIntervaleChangeOnIntervale %s  SpawnIntervaleMinVal %s " % (self.SpawnStart, self.SpawnIntervale, self.SpawnIntervaleChangeOn, self.SpawnIntervaleChangeOnIntervale, self.SpawnIntervaleMinVal)
            str3 = "MovieIdle %s" % (self.MovieIdle)
            str4 = "MoviePreExploud %s MovieExploud %s  MovieMoveTop %s  MovieMoveDown %s  MovieMoveRight %s  MovieMoveLeft %s " % (self.MoviePreExploud, self.MovieExploud, self.MovieMoveTop, self.MovieMoveDown, self.MovieMoveRight, self.MovieMoveLeft)
            str = "%s %s %s %s" % (str1, str2, str3, str4)
            return str
            pass

        pass

    class SpawnData(object):
        def __init__(self, From, What, Chance):
            self.From = From
            self.What = What
            self.Chance = Chance
            pass

        def __str__(self):
            str = "From %s What %s Chance %s " % (self.From, self.What, self.Chance)
            return str
            pass
        pass

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
            pass

        def addItem(self, item):
            for itemInName in self.Items:
                if (itemInName == item.ItemName):
                    print("BomberManager Can't add Item in GameData '%s' with Name '%s' , Item with such name already in" % (self.Name, item.ItemName))
                    Trace.trace()
                    return
                pass

            self.Items[item.ItemName] = item
            pass

        def addSpawnItem(self, item):
            if (item.From not in self.Items):
                print("BomberManager Can't find From Item in GameData '%s' with Name '%s'" % (self.Name, item.From))
                Trace.trace()
                return
                pass

            if (item.What not in self.Items):
                print("BomberManager Can't find What Item in GameData '%s' with Name '%s'" % (self.Name, item.What))
                Trace.trace()
                return
                pass

            self.SpawnDatas.append(item)

            fromItem = self.Items[item.From]

            fromItem.addSpawnData(item)
            print(item)
            pass
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            if Name is None or Name[0] == "#":
                continue
                pass

            if (BomberManager.hasGame(Name) is True):
                print("BomberManager.loadGames game wtih name Already Loadet :", Name)
                Trace.trace()
                continue
                pass
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
            # BomberManager.__loadGame(module, Name, Game)
            # BomberManager.__loadSpawnItems(module, SpawnName, Game)
            pass

        return True
        pass

    @staticmethod
    def __loadGame(module, param, Game):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ItemName = record.get("ItemName")
            if ItemName is None or ItemName[0] == "#":
                continue
                pass

            ItemType = record.get("ItemType")

            TypeExtraValue = record.get("TypeExtraValue", 0)
            if (ItemType != 1 and ItemType != 2 and ItemType != 3):
                TypeExtraValue = float(TypeExtraValue)
                pass
            else:
                TypeExtraValue = BomberManager.__Pars_Bomb_Blow(TypeExtraValue)
                pass

            BlowPoints = record.get("BlowPoints", "0")
            BlowPoints = BlowPoints.split(',')
            for id, intt in enumerate(BlowPoints):
                BlowPoints[id] = int(intt)
                pass

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

            intervales = [SpawnStart, SpawnIntervale, SpawnIntervaleChangeOn, SpawnIntervaleChangeOnIntervale, SpawnIntervaleMinVal]
            movie = [MoviePreExploud, MovieExploud, MovieMoveTop, MovieMoveTopOut, MovieMoveDown, MovieMoveDownOut, MovieMoveRight, MovieMoveRightOut, MovieMoveLeft, MovieMoveLeftOut]

            item = BomberManager.Item(Game, ItemName, ItemType, TypeExtraValue, BlowPoints, intervales, MovieIdle, movie)

            Game.addItem(item)
            pass

        return True
        pass

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
            pass
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
                    pass
                pass
            pass

        return dir
        pass

    @staticmethod
    def __loadSpawnItems(module, param, Game):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            FromItem = record.get("FromItem")
            if FromItem is None or FromItem[0] == "#":
                continue
                pass
            WhatItem = record.get("WhatItem")

            SpawnChance = record.get("SpawnChance")
            SpawnChance = float(SpawnChance)

            spawnItem = BomberManager.SpawnData(FromItem, WhatItem, SpawnChance)
            if (SpawnChance > 100):
                print("Spawn Item error SpawnChance > 100 ", spawnItem)
                Trace.trace()
                pass

            if (SpawnChance < 0):
                print("Spawn Item error SpawnChance < 0 ", spawnItem)
                Trace.trace()
                pass

            Game.addSpawnItem(spawnItem)
            pass

        return True
        pass

    @staticmethod
    def hasGame(name):
        return name in BomberManager.Games
        pass

    @staticmethod
    def getGame(name):
        if (BomberManager.hasGame(name) is False):
            print("BomberManager.getGame can't find game with Name ", name)
            Trace.trace()
            return None
            pass
        return BomberManager.Games[name]
        pass

    pass