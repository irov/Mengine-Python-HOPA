from Foundation.ArrowManager import ArrowManager
from Foundation.DatabaseManager import DatabaseManager

class PullManager(object):
    s_pulls = {}

    @staticmethod
    def load(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            Direction = record.get("Direction")
            CursorMode = record.get("CursorMode")

            if ArrowManager.hasCursorMode(CursorMode) is False:
                Trace.log("Manager", 0, "PullManager.load: ArrowManager not has mode '%s', please add to Cursors.xlsx and CursorObjects.xlsx" % (CursorMode,))
                return False
                pass

            PullManager.s_pulls[Direction] = CursorMode
            pass
        pass

    @staticmethod
    def getCursorMode(direction):
        CursorMode = PullManager.s_pulls[direction]
        return CursorMode
        pass

    pass

pass