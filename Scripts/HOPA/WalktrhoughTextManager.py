from Foundation.DatabaseManager import DatabaseManager

class WalktrhoughTextManager(object):
    s_walktrhoughTexts = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            SCENE_NAME = record.get("SCENE_NAME")

            ID_TEXT = record.get("ID_TEXT")

            WalktrhoughTextManager.s_walktrhoughTexts[SCENE_NAME] = ID_TEXT
            pass

        return True
        pass

    @staticmethod
    def getTextID(sceneName):
        if sceneName not in WalktrhoughTextManager.s_walktrhoughTexts:
            return None
            pass

        walktrhoughText = WalktrhoughTextManager.s_walktrhoughTexts[sceneName]
        return walktrhoughText
        pass