import copy

from Foundation.DatabaseManager import DatabaseManager


class MoveBlocksManager(object):
    s_objects = {}

    class Data(object):
        def __init__(self, field, win, buttons, blocks):
            self.field = field
            self.win = win
            self.buttons = buttons
            self.blocks = blocks
            pass

        def getField(self):
            res = copy.deepcopy(self.field)
            return res
            pass

        def getWin(self):
            return self.win
            pass

        def getButtons(self):
            return self.buttons
            pass

        def getBlocks(self):
            return self.blocks

    class Button(object):
        def __init__(self, mode, value, change):
            self.mode = mode
            self.value = value
            self.change = change
            pass

        def getMode(self):
            return self.mode
            pass

        def getValue(self):
            return self.value
            pass

        def getChange(self):
            return self.change

    class Block(object):
        def __init__(self, idle, off, on):
            self.idle = idle
            self.off = off
            self.on = on
            pass

        def getIdleName(self):
            return self.idle
            pass

        def getOffName(self):
            return self.off
            pass

        def getOnName(self):
            return self.on

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            EnigmaName = record.get("EnigmaName")
            FieldCollection = record.get("FieldCollection")
            WinCollection = record.get("WinCollection")
            ButtonsCollection = record.get("ButtonsCollection")
            BlocksCollection = record.get("BlocksCollection")

            field = MoveBlocksManager.loadField(module, FieldCollection)
            win = MoveBlocksManager.loadWin(module, WinCollection)
            buttons = MoveBlocksManager.loadButtons(module, ButtonsCollection)
            blocks = MoveBlocksManager.loadBlocks(module, BlocksCollection)

            Data = MoveBlocksManager.Data(field, win, buttons, blocks)
            MoveBlocksManager.s_objects[EnigmaName] = Data
            pass

        return True
        pass

    @staticmethod
    def loadField(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        field = {}
        for record in records:
            row = record.get("Row")
            value = record.get("Value")
            field[row] = value
            pass
        return field
        pass

    @staticmethod
    def loadWin(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        win = {}
        for record in records:
            row = record.get("Row")
            value = record.get("Value")
            win[row] = value
            pass
        return win
        pass

    @staticmethod
    def loadButtons(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        buttons = {}
        for record in records:
            ButtonName = record.get("ButtonName")
            Mode = record.get("Mode")
            Value = record.get("Value")
            Change = record.get("Change")
            buttonData = MoveBlocksManager.Button(Mode, Value, Change)
            buttons[ButtonName] = buttonData
            pass

        return buttons
        pass

    @staticmethod
    def loadBlocks(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        blocks = {}
        for record in records:
            Id = record.get("Id")
            MovieIdle = record.get("MovieIdle")
            MovieOn = record.get("MovieOn")
            MovieOff = record.get("MovieOff")

            block = MoveBlocksManager.Block(MovieIdle, MovieOff, MovieOn)
            blocks[Id] = block
            pass
        return blocks
        pass

    @staticmethod
    def getData(name):
        return MoveBlocksManager.s_objects[name]
