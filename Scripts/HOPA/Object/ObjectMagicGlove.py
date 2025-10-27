from Foundation.Object.DemonObject import DemonObject

from Foundation.SceneManager import SceneManager
from HOPA.QuestManager import QuestManager
from HOPA.ZoomManager import ZoomManager


class ObjectMagicGlove(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("Point")
        Type.declareParam("Runes")
        Type.declareParam("State")

    def _onParams(self, params):
        super(ObjectMagicGlove, self)._onParams(params)

        self.initParam("Point", params, (0.0, 0.0))
        self.initParam("Runes", params, [])
        self.initParam("State", params, "Idle")

    @staticmethod
    def getActiveUseRuneQuest():
        current_scene_name = SceneManager.getCurrentSceneName()
        group_name = ZoomManager.getZoomOpenGroupName()
        if group_name is None:
            group_name = SceneManager.getSceneMainGroupName(current_scene_name)
        quests = QuestManager.getSceneQuests(current_scene_name, group_name)
        for quest in quests:
            if quest.getType() != "UseRune":
                continue
            if quest.isActive():
                return quest
        return None
