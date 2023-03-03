from HOPA.CursorManager import CursorManager
from Foundation.DatabaseManager import DatabaseManager


class PullManager(object):
    s_pulls = {}

    @staticmethod
    def load(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            Direction = record.get("Direction")
            CursorMode = record.get("CursorMode")

            if CursorManager.hasCursorMode(CursorMode) is False:
                Trace.log("Manager", 0, "CursorManager hasn't mode '%s', please add to Cursors.xlsx and CursorObjects.xlsx" % (CursorMode,))
                return False

            PullManager.s_pulls[Direction] = CursorMode

    @staticmethod
    def getCursorMode(direction):
        CursorMode = PullManager.s_pulls[direction]
        return CursorMode
