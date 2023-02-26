from Foundation.DatabaseManager import DatabaseManager
from Foundation.DemonManager import DemonManager

class MahjongManager(object):
    s_games = {}
    s_inventories = {}

    class Data(object):
        def __init__(self, button1Name, button1SyncMovieName, button2Name, button2SyncMovieName, checkbox):
            self.button1Name = button1Name
            self.button1SyncMovieName = button1SyncMovieName
            self.button2Name = button2Name
            self.button2SyncMovieName = button2SyncMovieName

            self.checkbox = checkbox

        def getButton1Name(self):
            return self.button1Name

        def getButton2Name(self):
            return self.button2Name

        def getButton1SyncMovie(self):
            return self.button1SyncMovieName

        def getButton2SyncMovie(self):
            return self.button2SyncMovieName

        def getCheckBox(self):
            return self.checkbox

    @staticmethod
    def loadParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for record in records:
            EnigmaName = record.get("EnigmaName")
            Param = record.get("Param")
            Inventory = record.get("Inventory")

            MahjongManager.loadGame(module, Param, EnigmaName, Inventory)

        return True

    @staticmethod
    def loadGame(module, name, enigmaName, inventory):
        records = DatabaseManager.getDatabaseRecords(module, name)

        MahjongManager.s_games[enigmaName] = []

        for record in records:
            Button1Name = record.get("Button1")
            Button1SyncMovieName = record.get("Button1SyncMovie")
            Button2Name = record.get("Button2")
            Button2SyncMovieName = record.get("Button2SyncMovie")
            CheckBox = record.get("CheckBox")

            GameData = MahjongManager.Data(Button1Name, Button1SyncMovieName, Button2Name, Button2SyncMovieName, CheckBox)
            MahjongManager.s_games[enigmaName].append(GameData)

        if inventory is None:
            return

        if DemonManager.hasDemon(inventory) is None:
            Trace.log("MahjongManager", 0, "MahjongManager.loadGame: not found inventory demon %s" % inventory)
            return

        MahjongManager.s_inventories[enigmaName] = inventory

    @staticmethod
    def getData(enigmaName):
        return MahjongManager.s_games[enigmaName]

    @staticmethod
    def getInventory(enigmaName):
        inventoryName = MahjongManager.s_inventories.get(enigmaName)
        if inventoryName is None:
            Trace.log("MahjongManager", 0, "MahjongManager.getInventory: not found inventory demon name for enigma '%s'" % enigmaName)
            return None

        if DemonManager.hasDemon(inventoryName) is False:
            Trace.log("MahjongManager", 0, "MahjongManager.getInventory: not found inventory demon '%s'" % inventoryName)
            return None

        return DemonManager.getDemon(inventoryName)