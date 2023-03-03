from Foundation.SceneManager import SceneManager
from Foundation.Task.MixinGroup import MixinGroup
from HOPA.QuestIconAction import QuestIconAction


class QuestIconActionDefault(MixinGroup, QuestIconAction):
    def __init__(self):
        super(QuestIconActionDefault, self).__init__()
        self.questIconParentObject = None
        self.iconPosition = None
        self.nodeCopyIcon = None
        self.activeIcon = False
        pass

    def _onInitialize(self):
        super(QuestIconActionDefault, self)._onInitialize()

        self.questIconParentObject = self.getQuestIconObject()
        pass

    def isActiveIcon(self):
        return self.activeIcon
        pass

    def _onParams(self, params):
        super(QuestIconActionDefault, self)._onParams(params)
        pass

    def _onAction(self):
        questIconObj = self.getParentQuestIconObject()
        object = self.getQuestIconObject()
        nodePosition = self.getQuestIconPosition(object)
        objectEntity = object.getEntity()

        questIconEntity = questIconObj.getEntity()
        sprite = questIconEntity.getSprite()

        iconResource = sprite.getResourceImage()

        self.nodeCopyIcon = Mengine.createSprite("quest_icon", iconResource)
        self.nodeCopyIcon.enable()

        scene = SceneManager.getCurrentScene()
        objectEntity.addChild(self.nodeCopyIcon)

        self.nodeCopyIcon.setWorldPosition(nodePosition)
        self.activeIcon = True
        pass

    def onCheck(self):
        if self.activeIcon is True:
            return False

        obj = self.getQuestIconObject()
        if obj.getEnable() is False:
            return False
            pass

        if obj.isActive() is False:
            return False

        return True
        pass

    def _onEnd(self):
        if self.nodeCopyIcon is None:
            return

        self.nodeCopyIcon.disable()
        self.nodeCopyIcon.removeFromParent()
        Mengine.destroyNode(self.nodeCopyIcon)
        self.nodeCopyIcon = None

        self.activeIcon = False
        pass

    def getQuestIconObject(self):
        return self._getQuestIconObject()
        pass

    def getQuestIconPosition(self, object):
        return self._getQuestIconPosition(object)
        pass

    def _getQuestIconObject(self):
        return None
        pass

    def _getQuestIconPosition(self, Object):
        return (0, 0)
        pass

    pass
