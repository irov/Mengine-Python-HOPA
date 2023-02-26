from Foundation.SceneManager import SceneManager
from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.TransitionManager import TransitionManager

class MacroTransition(MacroCommand):
    Immediately = True

    def __init__(self):
        """
        first param scene

        second param zoom

        third param disable fade, by default is enabled,
            to disable set to 0, if no second param then second param should be 0
        """
        super(MacroTransition, self).__init__()
        self.scene_name_to = None
        self.zoom_group_name = None
        self.zoom_effect_transition_object = None
        self.fade = True

    def _onValues(self, values):
        if _DEVELOPMENT is True:
            if len(values) == 0:
                self.initializeFailed("Macro should have at least one param, scene name")

        self.scene_name_to = values[0]

        if len(values) == 2:
            self.zoom_group_name = values[1]
            if self.zoom_group_name is 0:
                self.zoom_group_name = None

        if len(values) == 3:
            self.fade = bool(values[2])

    def _onInitialize(self):
        if self.scene_name_to == "Back":
            return

        if _DEVELOPMENT is True:
            if SceneManager.hasScene(self.scene_name_to) is False:
                self.initializeFailed("First required param Scene '%s' found item" % (self.scene_name_to,))

        if bool(self.zoom_group_name):
            if _DEVELOPMENT is True:
                if SceneManager.hasSceneZoom(self.scene_name_to, self.zoom_group_name) is False:
                    self.initializeFailed("Second optional param Zoom '%s' not found" % (self.zoom_group_name,))

            self.zoom_effect_transition_object = TransitionManager.getTransition(self.scene_name_to, self.zoom_group_name)

    def _onGenerate(self, source):
        """
        self.SceneName, self.GroupName params of MacroCommand class
        """
        if self.scene_name_to == "Back":
            source.addTask("TaskFunction", Fn=TransitionManager.changeToGameScene)
            return

        quest = self.addQuest(source, "Teleport", SceneName=self.SceneName, GroupName=self.GroupName, SceneNameTo=self.scene_name_to)

        with quest as tc_quest:
            if self.ScenarioRunner.isZoom is True:
                tc_quest.addTask("TaskZoomClose", ZoomName=self.GroupName)
            tc_quest.addTask("AliasTransition", SceneName=self.scene_name_to, ZoomGroupName=self.zoom_group_name, ZoomEffectTransitionObject=self.zoom_effect_transition_object, Fade=self.fade)