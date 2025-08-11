from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Notification import Notification

class MindManager(Manager):
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

        def getDelay(self):
            return self.delay

        def getGroup(self):
            return self.group

        def getVoiceID(self):
            return self.voiceID

    @staticmethod
    def _onFinalize():
        MindManager.s_minds = {}
        pass

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

    @staticmethod
    def addMind(mindId, textId, delay, group, voiceID):
        mind = MindManager.Mind(textId, delay, group, voiceID)

        MindManager.s_minds[mindId] = mind
        pass

    @staticmethod
    def hasMind(mindId):
        return mindId in MindManager.s_minds

    @staticmethod
    def getMind(mindId):
        if mindId not in MindManager.s_minds:
            return None

        mind = MindManager.s_minds[mindId]

        return mind

    @staticmethod
    def getAllMinds():
        return MindManager.s_minds

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

    @staticmethod
    def getDelay(mindId):
        mind = MindManager.getMind(mindId)
        delay = mind.getDelay()

        return delay

    @staticmethod
    def getGroup(mindId):
        mind = MindManager.getMind(mindId)
        group = mind.getGroup()

        return group

    @staticmethod
    def getVoiceID(mindId):
        mind = MindManager.getMind(mindId)
        VoiceID = mind.getVoiceID()

        return VoiceID
