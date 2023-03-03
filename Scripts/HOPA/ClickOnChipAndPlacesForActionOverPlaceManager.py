from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class ClickOnChipAndPlacesForActionOverPlaceManager(Manager):
    s_puzzles = {}

    class ClickOnChipAndPlacesForActionOverPlaceParam(object):
        def __init__(self, placeParam, NumberOfChips, neighboringPlacesParam, skipParam, chipParam):
            self.Places = placeParam
            self.NumberOfChips = NumberOfChips
            self.NeighboringPlaces = neighboringPlacesParam
            self.Skip = skipParam
            self.Chips = chipParam

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
                EnigmaName	PlaceParam	NumberOfChips	NeighboringPlaces	Skip ChipParam
            '''
            EnigmaName = record.get('EnigmaName')
            PlaceParam = record.get('PlaceParam')
            NumberOfChips = record.get('NumberOfChips')
            NeighboringPlaces = record.get('NeighboringPlaces')
            Skip = record.get('Skip')
            ChipParam = record.get('ChipParam')

            result = ClickOnChipAndPlacesForActionOverPlaceManager.addParam(EnigmaName, module, PlaceParam,
                                                                            NumberOfChips, NeighboringPlaces, Skip,
                                                                            ChipParam)

            if result is False:
                error_msg = "ClickOnChipAndPlacesForActionOverPlaceManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(EnigmaName, Module, PlaceParam, NumberOfChips, NeighboringPlaces, Skip, ChipParam):
        if EnigmaName in ClickOnChipAndPlacesForActionOverPlaceManager.s_puzzles:
            error_msg = "ClickOnChipAndPlacesForActionOverPlaceManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Chips -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ChipParam)
        chipParam = {}
        if records is None:
            error_msg = "MoveChipsToKeyPointsManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                ChipID	MovieName
            '''
            ChipID = record.get('ChipID')
            MovieName = record.get('MovieName')

            chipParam[ChipID] = MovieName

            pass
        # ==============================================================================================================

        # -------------- Places ---------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, PlaceParam)
        placeParam = {}
        if records is None:
            error_msg = "ClickOnChipAndPlacesForActionOverPlaceManager cant find placeParam database for {}".format(
                EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                PlaceID	MovieNameGreen	MovieNameBlue	MovieNameYellow     MovieNameGreenWin	MovieNameBlueWin	
                MovieNameYellowWin  MovieNameSilverWin


            '''
            PlaceID = record.get('PlaceID')
            MovieNameGreen = record.get('MovieNameGreen')
            MovieNameBlue = record.get('MovieNameBlue')
            MovieNameYellow = record.get('MovieNameYellow')
            MovieNameGreenWin = record.get('MovieNameGreenWin')
            MovieNameBlueWin = record.get('MovieNameBlueWin')
            MovieNameYellowWin = record.get('MovieNameYellowWin')
            MovieNameSilverWin = record.get('MovieNameSilverWin')

            placeParam[PlaceID] = ((MovieNameGreen, MovieNameGreenWin), (MovieNameBlue, MovieNameBlueWin),
            (MovieNameYellow, MovieNameYellowWin), (None, MovieNameSilverWin))
        # ==============================================================================================================

        # -------------- Neighboring Places ----------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, NeighboringPlaces)
        neighboringPlacesParam = {}
        if records is None:
            error_msg = "ClickOnChipAndPlacesForActionOverPlaceManager cant find NeighboringPlaces database for {}".format(
                EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                PlaceID	[NeighboringPlaceID]
            '''
            PlaceID = record.get('PlaceID')
            NeighboringPlaceIDList = record.get('NeighboringPlaceID')

            neighboringPlacesParam[PlaceID] = NeighboringPlaceIDList
        # ==============================================================================================================

        # -------------- Skip ------------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, Skip)
        skipParam = {}
        if records is None:
            error_msg = "ClickOnChipAndPlacesForActionOverPlaceManager cant find Skip database for {}".format(
                EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                PlaceID	ChipID
            '''
            PlaceID = record.get('PlaceID')
            ChipID = record.get('ChipID')

            skipParam[PlaceID] = ChipID
        # ==============================================================================================================

        new_param = ClickOnChipAndPlacesForActionOverPlaceManager.ClickOnChipAndPlacesForActionOverPlaceParam(
            placeParam, NumberOfChips, neighboringPlacesParam, skipParam, chipParam)

        ClickOnChipAndPlacesForActionOverPlaceManager.s_puzzles[EnigmaName] = new_param

        return True

    @staticmethod
    def getParam(EnigmaName):
        return ClickOnChipAndPlacesForActionOverPlaceManager.s_puzzles.get(EnigmaName)
