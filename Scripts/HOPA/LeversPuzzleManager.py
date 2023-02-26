from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from Foundation.Manager import Manager

class LeversPuzzleManager(Manager):
    s_puzzles = {}

    # - param -------------------------------------------------------------------------------------
    class LeversPuzzleParam(object):
        def __init__(self, ChipsRecords, LeversRecords, ParamChipsOver):
            self.ChipsRecords = ChipsRecords
            self.LeversRecords = LeversRecords

            self.ParamChipsOver = ParamChipsOver

        def getLevers(self):
            levers = {}

            for record in self.LeversRecords:
                LeverID = record.get('LeverID')

                if LeverID is None:
                    continue

                GroupName = record.get('GroupName')
                MovieCheckBoxName = record.get('MovieCheckBoxName')

                CheckBox = GroupManager.getObject(GroupName, MovieCheckBoxName)

                levers[LeverID] = CheckBox

            return levers

        def getChips(self):
            chips = {}

            for record in self.ChipsRecords:
                ChipID = record.get('ChipID')

                if ChipID is None:
                    continue

                GroupName = record.get('GroupName')
                MovieNameOff = record.get('MovieNameOff')
                MovieNameOn = record.get('MovieNameOn')

                StartState = record.get('StartState')
                WinState = record.get('WinState')

                LeverIDs = record.get('LeverIDs')

                MovieOff = GroupManager.getObject(GroupName, MovieNameOff)
                MovieOn = GroupManager.getObject(GroupName, MovieNameOn)

                chips[ChipID] = (MovieOff, MovieOn, StartState, WinState, LeverIDs)

            return chips

        def getChipsOver(self):
            if self.ParamChipsOver is None:
                return None

            chips_over = []

            for record in self.ParamChipsOver:
                ChipID = record.get('ChipID')
                ChipOverID = record.get('ChipOverID')

                GroupName = record.get('GroupName')

                MovieNameOffOver = record.get('MovieNameOffOver')
                MovieNameOnOver = record.get('MovieNameOnOver')

                MovieOffOver = GroupManager.getObject(GroupName, MovieNameOffOver)
                MovieOnOver = GroupManager.getObject(GroupName, MovieNameOnOver)

                chips_over.append((ChipID, ChipOverID, MovieOffOver, MovieOnOver))

            return chips_over

    # ---------------------------------------------------------------------------------------------

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            EnigmaName = record.get("EnigmaName")

            ParamChips = record.get("ParamChips")
            ParamLevers = record.get("ParamLevers")

            ParamChipsOver = record.get("ParamChipsOver")

            param = LeversPuzzleManager.addParam(EnigmaName, module, ParamChips, ParamLevers, ParamChipsOver)

            if param is False:
                error_msg = "LeversPuzzleManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False

        return True

    @staticmethod
    def addParam(EnigmaName, Module, ParamChips, ParamLevers, ParamChipsOver):
        if EnigmaName in LeversPuzzleManager.s_puzzles:
            error_msg = "LeversPuzzleManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # read Chips database
        ChipsRecords = DatabaseManager.getDatabaseRecords(Module, ParamChips)

        if ChipsRecords is None:
            error_msg = "LeversPuzzleManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # read Levers database
        LeversRecords = DatabaseManager.getDatabaseRecords(Module, ParamLevers)

        if LeversRecords is None:
            error_msg = "LeversPuzzleManager cant find Levers database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # read ChipsOver database
        ParamChipsOver = DatabaseManager.getDatabaseRecords(Module, ParamChipsOver)

        NewParam = LeversPuzzleManager.LeversPuzzleParam(ChipsRecords, LeversRecords, ParamChipsOver)

        LeversPuzzleManager.s_puzzles[EnigmaName] = NewParam
        return True

    @staticmethod
    def getParam(EnigmaName):
        return LeversPuzzleManager.s_puzzles.get(EnigmaName)