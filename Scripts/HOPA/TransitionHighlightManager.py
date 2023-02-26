from Foundation.DatabaseManager import DatabaseManager

class TransitionHighlightManager(object):
    s_transitionHighlights = {}

    class TransitionHighlight(object):
        def __init__(self, transitionName, prototypeGroupName, prototypeName):
            self.transitionName = transitionName
            self.prototypeGroupName = prototypeGroupName
            self.prototypeName = prototypeName

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            TransitionName = record.get("TransitionName")
            PrototypeGroupName = record.get("PrototypeGroupName")
            PrototypeObjectName = record.get("PrototypeObjectName")
            transitionHighlight = TransitionHighlightManager.TransitionHighlight(TransitionName, PrototypeGroupName, PrototypeObjectName)
            TransitionHighlightManager.s_transitionHighlights[TransitionName] = transitionHighlight

        return True

    @staticmethod
    def getTransitionHighlight(transitionName):
        if transitionName not in TransitionHighlightManager.s_transitionHighlights:
            Trace.log("Manager", 0, "TransitionHighlightManager.getTransitionHighlight(): not found highlight effect for %s", transitionName)
            return None

        transitionHighlight = TransitionHighlightManager.s_transitionHighlights[transitionName]

        return transitionHighlight

    @staticmethod
    def hasTransitionHighlight(transitionName):
        return transitionName in TransitionHighlightManager.s_transitionHighlights