from Foundation.DatabaseManager import DatabaseManager
from Foundation.DemonManager import DemonManager
from Foundation.Manager import Manager

class DialogBoxManager(Manager):
    s_dialogs = {}

    class Dialog(object):
        def __init__(self, dialogID, textID, characterID, voiceID, AlphaToTime, AlphaFromTime, PlayDialogDelay):
            self.dialogID = dialogID
            self.textID = textID
            self.characterID = characterID
            self.voiceID = voiceID
            self.AlphaToTime = AlphaToTime
            self.AlphaFromTime = AlphaFromTime
            self.PlayDialogDelay = PlayDialogDelay
            pass

        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ID_DIALOG = record.get("ID_DIALOG")

            ID_TEXT = record.get("ID_TEXT")
            CHARACTER = record.get("CHARACTER")
            VoiceID = record.get("VoiceID")
            AlphaToTime = record.get("AlphaToTime", 1000)
            AlphaFromTime = record.get("AlphaFromTime", 500)
            PlayDialogDelay = record.get("PlayDialogDelay", 100)

            DialogBoxManager.addDialog(ID_DIALOG, ID_TEXT, CHARACTER, VoiceID, AlphaToTime, AlphaFromTime, PlayDialogDelay)
            pass

        return True
        pass

    @staticmethod
    def addDialog(dialogID, textID, characterID, voiceID, AlphaToTime, AlphaFromTime, PlayDialogDelay):
        if Mengine.existText(textID) is False:
            Trace.log("Manager", 0, "DialogBoxManager.addDialogID: invalid dialog '%s' not found text '%s'" % (dialogID, textID))
            return
            pass

        Demon_DialogBox = DemonManager.getDemon("DialogBox")
        if Demon_DialogBox.hasObject(characterID) is True:
            CharacterObject = Demon_DialogBox.getObject(characterID)
            CharacterObject.setEnable(False)

        dialog = DialogBoxManager.Dialog(dialogID, textID, characterID, voiceID, AlphaToTime, AlphaFromTime, PlayDialogDelay)

        DialogBoxManager.s_dialogs[dialogID] = dialog
        pass

    @staticmethod
    def hasDialog(dialogID):
        if dialogID not in DialogBoxManager.s_dialogs:
            return False
            pass

        return True
        pass

    @staticmethod
    def getDialog(dialogID):
        if dialogID not in DialogBoxManager.s_dialogs:
            Trace.log("Manager", 0, "DialogBoxManager.getDialogID: not found dialog id %s" % (dialogID))
            return None
            pass

        dialog = DialogBoxManager.s_dialogs[dialogID]

        return dialog
        pass