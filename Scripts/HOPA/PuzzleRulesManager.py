class PuzzleRulesManager(object):
    s_objects = {}

    class PuzzleRules(object):
        def __init__(self, casualTextID, expertTextID):
            self.casualTextID = casualTextID
            self.expertTextID = expertTextID
            pass
        pass

    @staticmethod
    def onFinalize():
        PuzzleRulesManager.s_objects = {}
        pass

    @staticmethod
    def loadPuzzleRules(param):
        PuzzleRules_Param = Mengine.getParam(param)

        if PuzzleRules_Param is None:
            Trace.log("Manager", 0, "PuzzleRulesManager.loadPuzzleRules: invalid param %s" % (param))
            return

        for values in PuzzleRules_Param:
            collectionName = values[0].strip()
            if collectionName == "":
                continue

            casualTextID = values[1].strip()
            expertTextID = values[2].strip()

            Object = PuzzleRulesManager.PuzzleRules(casualTextID, expertTextID)

            PuzzleRulesManager.s_objects[collectionName] = Object
            pass
        pass

    @staticmethod
    def getPuzzleRules(name):
        if name not in PuzzleRulesManager.s_objects.keys():
            return None
            pass

        return PuzzleRulesManager.s_objects[name]
        pass

    @staticmethod
    def hasPuzzleRules(name):
        if name not in PuzzleRulesManager.s_objects.keys():
            return False
            pass

        return True
        pass

    pass

pass