from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class QuestIconManager(Manager):
    s_quests = {}
    s_actions = {}

    @staticmethod
    def _onFinalize():
        QuestIconManager.s_quests = {}
        QuestIconManager.s_actions = {}
        pass

    @staticmethod
    def importQuestIconActions(module, names):
        for name in names:
            QuestIconManager.importQuestIconAction(module, name)

    @staticmethod
    def importQuestIconAction(module, name):
        Name = "%s" % (name)
        FromName = module
        ModuleName = "%s.%s" % (FromName, Name)
        Module = __import__(ModuleName, fromlist=[FromName])
        Type = getattr(Module, Name)
        QuestIconManager.addQuestIconAction(name, Type)

    @staticmethod
    def addQuestIconAction(actionType, action):
        QuestIconManager.s_actions[actionType] = action

    @staticmethod
    def getQuestIconAction(questType):
        questIconActionName = QuestIconManager.getQuestActionType(questType)
        return QuestIconManager.s_actions[questIconActionName]

    @staticmethod
    def getQuestActionType(questType):
        return QuestIconManager.s_quests[questType][0]

    @staticmethod
    def loadQuestIcon(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            QuestType = record.get("QuestID")
            QuestIconActionName = record.get("QuestIconActionName")
            SpriteIconName = record.get("SpriteIconName")
            UseQuestObject = bool(record.get("UseQuestObject"))
            IconGroupName = record.get("IconGroupName")
            StartEnable = bool(record.get("StartEnable"))

            icon = GroupManager.getObject(IconGroupName, SpriteIconName)
            icon.setEnable(False)

            QuestIconManager.s_quests[QuestType] = (QuestIconActionName, icon, UseQuestObject, StartEnable)

    @staticmethod
    def getQuests():
        return QuestIconManager.s_quests

    @staticmethod
    def getQuestIcon(questType):
        return QuestIconManager.s_quests[questType][1]
