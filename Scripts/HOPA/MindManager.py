from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Notification import Notification


class MindManager(object):
    s_minds = {}

    class Mind(object):
        def __init__(self, textId, delay, group, voiceID):
            self.textId = textId
            self.delay = delay
            self.group = group
            self.voiceID = voiceID
            pass

        def getTextID(self):
            return self.textId
            pass

        def getDelay(self):
            return self.delay
            pass

        def getGroup(self):
            return self.group
            pass

        def getVoiceID(self):
            return self.voiceID

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            MindId = record.get("MindId")
            TextId = record.get("TextId")

            DefaultMindDelay = DefaultManager.getDefaultFloat("MindShowTime", 3)

            Delay = record.get("Delay", DefaultMindDelay)
            Delay *= 1000  # speed fix
            Group = record.get("Group", None)
            VoiceID = record.get("VoiceID", None)

            MindManager.addMind(MindId, TextId, Delay, Group, VoiceID)
            pass

        return True
        pass

    @staticmethod
    def addMind(mindId, textId, delay, group, voiceID):
        mind = MindManager.Mind(textId, delay, group, voiceID)

        MindManager.s_minds[mindId] = mind
        pass

    @staticmethod
    def hasMind(mindId):
        return mindId in MindManager.s_minds
        pass

    @staticmethod
    def getMind(mindId):
        if mindId not in MindManager.s_minds:
            return None
            pass

        mind = MindManager.s_minds[mindId]

        return mind
        pass

    @staticmethod
    def getAllMinds():
        return MindManager.s_minds
        pass

    @staticmethod
    def mindShow(mindId, isZoom, static):
        Notification.notify(Notificator.onBlackBarRelease, mindId)
        Notification.notify(Notificator.onMindShow, mindId, isZoom, static)
        pass

    @staticmethod
    def getTextID(mindId):
        mind = MindManager.getMind(mindId)
        textID = mind.getTextID()

        return textID
        pass

    @staticmethod
    def getDelay(mindId):
        mind = MindManager.getMind(mindId)
        delay = mind.getDelay()

        return delay
        pass

    @staticmethod
    def getGroup(mindId):
        mind = MindManager.getMind(mindId)
        group = mind.getGroup()

        return group
        pass

    @staticmethod
    def getVoiceID(mindId):
        mind = MindManager.getMind(mindId)
        VoiceID = mind.getVoiceID()

        return VoiceID
