import Trace
from Foundation.Bootstrapper import checkBuildMode
from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from Notification import Notification

DEMON_DIALOG = "Demon_Dialog"
DEMON_DIALOG_AVATAR = "Demon_Switch_Avatar"

class DialogManager(object):
    s_dialogs = {}

    class Dialog(object):
        def __init__(self, dialogID, textID, characterID, idleID, GROUP, nextID, voiceID, textDelay, finish, audio_duration):
            self.dialogID = dialogID
            self.textID = textID
            self.characterID = characterID
            self.idleID = idleID
            self.group = GROUP
            self.nextID = nextID
            self.voiceID = voiceID
            self.textDelay = textDelay
            self.finish = finish
            self.audio_duration = audio_duration
            pass
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ID_DIALOG = record.get("ID_DIALOG")

            ID_TEXT = record.get("ID_TEXT")
            CHARACTER = record.get("CHARACTER")
            IDLE = record.get("IDLE")
            GROUP = record.get("GROUP")
            NEXT = record.get("NEXT")
            VoiceID = record.get("VoiceID")
            TextDelay = record.get("TextDelay")
            Finish = bool(int(record.get("Finish", False)))
            AudioDuration = record.get("AudioDuration")
            Survey = record.get("Survey", None)
            CE = record.get("CE", None)
            BuildModeTags = record.get("BuildModeTags", [])

            DialogManager.addDialog(ID_DIALOG, ID_TEXT, CHARACTER, IDLE, GROUP, NEXT, VoiceID, TextDelay, Finish, AudioDuration, Survey, CE, BuildModeTags)
            pass

        if _DEVELOPMENT is True:
            DialogManager.__validateDialogs()

        return True
        pass

    # for movie-character resource check if exists any audio composition with |vo| tag
    @staticmethod
    def __dialogCharacterCompHasSoundVoiceTag(dialog):
        group = GroupManager.getGroup(dialog.group)
        if group is None or isinstance(group, GroupManager.EmptyGroup):
            Trace.log("Manager", 0, "Can't find dialog group %s for dialog %s" % (dialog.group, dialog.dialogID))
        else:
            demonDialog = group.getObject(DEMON_DIALOG)
            if demonDialog is None:
                Trace.log("Manager", 0, "Can't find demon %s dialog in group %s for dialog %s" % (DEMON_DIALOG, dialog.group, dialog.dialogID))
            else:
                demonDialogAvatar = demonDialog.getObject(DEMON_DIALOG_AVATAR)
                if demonDialogAvatar is None:
                    Trace.log("Manager", 0, "Can't find demon %s in parent demon %s dialog group %s for dialog %s" % (DEMON_DIALOG_AVATAR, DEMON_DIALOG, dialog.group, dialog.dialogID))
                else:
                    voiceCharacterMovie = demonDialogAvatar.getObject(dialog.characterID)
                    if voiceCharacterMovie is None:
                        Trace.log("Manager", 0, "Dialog %s: Can't find character movie %s in %s - > %s - > %s" % (dialog.dialogID, dialog.characterID, dialog.group, DEMON_DIALOG, DEMON_DIALOG_AVATAR))
                    else:
                        resourceVoCharMovie = voiceCharacterMovie.getResourceMovie()

                        if resourceVoCharMovie.hasComposition(voiceCharacterMovie.getCompositionName()):
                            layers = resourceVoCharMovie.getCompositionLayers(voiceCharacterMovie.getCompositionName())

                            # old export compatibility
                            if len(layers) == 0:
                                # Trace.log("Manager", 0, "Need reexport AE file with recent export script OR dialog %s Composition %s is empty"
                                #           % (dialog.dialogID, voiceCharacterMovie.getCompositionName()))
                                return False

                            for layer in layers:
                                if layer["type"] == "Sound" and layer["options"].count("vo") > 0:
                                    return True

                            Trace.log("Manager", 0, "Dialog: %s CharacterMovie: %s should has sound layer with '|vo|' tag to mark sound as voice" % (dialog.dialogID, dialog.characterID))
                        else:
                            Trace.log("Manager", 0, "Dialog: %s CharacterMovie: %s something wrong with %s composition" % (dialog.dialogID, dialog.characterID, voiceCharacterMovie.getCompositionName()))
        return False

    @staticmethod
    def __validateDialogs():
        for dialogID, dialog in DialogManager.s_dialogs.iteritems():
            # validate sounds:
            DialogManager.__dialogCharacterCompHasSoundVoiceTag(dialog)

            if dialog.nextID is None:
                continue
                pass

            if DialogManager.hasDialog(dialog.nextID) is False:
                Trace.log("Manager", 0, "DialogManager.__validateDialogs dialog %s has invalid next dialog %s" % (dialogID, dialog.nextID))
                continue
                pass

            dialogChainId = []
            dialogChainId.append(dialogID)

            while dialog.nextID is not None:
                dialog = DialogManager.getDialog(dialog.nextID)

                if dialog.nextID in dialogChainId:
                    Trace.log("Manager", 0, "DialogManager.__validateDialogs dialog %s has cicle next %s" % (dialogID, dialog.nextID))
                    break
                    pass

                dialogChainId.append(dialog.nextID)
                pass
            pass
        pass

    @staticmethod
    def addDialog(dialogID, textID, characterID, idleID, GROUP, nextID, voiceID, textDelay, finish, AudioDuration, Survey, CE, BuildModeTags):
        if Mengine.existText(textID) is False:
            Trace.log("Manager", 0, "DialogManager.addDialogID: invalid dialog '%s' not found text '%s'" % (dialogID, textID))
            return
            pass

        if checkBuildMode(dialogID, Survey, CE, BuildModeTags) is True:
            return

        dialog = DialogManager.Dialog(dialogID, textID, characterID, idleID, GROUP, nextID, voiceID, textDelay, finish, AudioDuration)
        DialogManager.s_dialogs[dialogID] = dialog
        pass

    @staticmethod
    def hasDialog(dialogID):
        if dialogID not in DialogManager.s_dialogs:
            return False
            pass

        return True
        pass

    @staticmethod
    def getDialog(dialogID):
        if dialogID not in DialogManager.s_dialogs:
            Trace.log("Manager", 0, "DialogManager.getDialogID: not found dialog id %s" % (dialogID))
            return None
            pass

        dialog = DialogManager.s_dialogs[dialogID]

        return dialog
        pass

    @staticmethod
    def dialogShow(dialogId):
        Notification.notify(Notificator.onBlackBarRelease, dialogId)
        Notification.notify(Notificator.onDialogShow, dialogId)
        pass

    @staticmethod
    def getDialogChain(dialogID):
        dialog = DialogManager.getDialog(dialogID)

        if dialog is None:
            return None
            pass

        dialogs = []
        dialogs.append(dialog)

        while dialog.nextID is not None:
            dialog = DialogManager.getDialog(dialog.nextID)
            dialogs.append(dialog)
            pass

        return dialogs

    pass