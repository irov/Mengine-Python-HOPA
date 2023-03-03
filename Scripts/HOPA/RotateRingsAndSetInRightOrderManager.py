from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class RotateRingsAndSetInRightOrderManager(Manager):
    s_puzzles = {}

    class RotateRingsAndSetInRightOrderParam(object):
        def __init__(self, ringParam):
            self.Rings = ringParam

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
                EnigmaName  RingParam  
            '''
            EnigmaName = record.get('EnigmaName')
            RingParam = record.get('RingParam')

            result = RotateRingsAndSetInRightOrderManager.addParam(EnigmaName, module, RingParam)

            if result is False:
                error_msg = "RotateRingsAndSetInRightOrderManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False
            return True

    @staticmethod
    def addParam(EnigmaName, Module, RingParam):
        if EnigmaName in RotateRingsAndSetInRightOrderManager.s_puzzles:
            error_msg = "RotateRingsAndSetInRightOrderManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Rings -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, RingParam)
        ringParam = {}
        if records is None:
            error_msg = "MoveChipsToKeyPointsManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                RingID MovieName
            '''
            RingID = record.get('RingID')
            MovieName = record.get('MovieName')

            ringParam[RingID] = MovieName
        # ==============================================================================================================

        new_param = RotateRingsAndSetInRightOrderManager.RotateRingsAndSetInRightOrderParam(ringParam)
        RotateRingsAndSetInRightOrderManager.s_puzzles[EnigmaName] = new_param
        return True

    @staticmethod
    def getParam(EnigmaName):
        return RotateRingsAndSetInRightOrderManager.s_puzzles.get(EnigmaName)
