from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.TransitionHighlightManager import TransitionHighlightManager
from HOPA.TransitionManager import TransitionManager


class SystemTransitionHighlight(System):
    def __init__(self):
        super(SystemTransitionHighlight, self).__init__()

        self.effects = {}
        self.tcs_names = []

        self.activeHighlight = False
        pass

    def _onRun(self):
        self.addObserver(Notificator.onSceneActivate, self.__cbSceneInit)
        self.addObserver(Notificator.onSelectedDifficulty, self.__cbSelectedDifficulty)
        self.addObserver(Notificator.onSceneDeactivate, self.__cbSceneLeave)
        self.addObserver(Notificator.onTransitionBlockOpen, self.__cbTransitionBlockOpen)

        current_scene_name = SceneManager.getCurrentSceneName()
        if SceneManager.isGameScene(current_scene_name) is True:
            self.__cbSceneInit(current_scene_name)

        return True

    def _onStop(self):
        self.removeEffects()
        pass

    def __cbSelectedDifficulty(self):
        if Mengine.getCurrentAccountSettingBool("DifficultyCustomSparklesOnHOPuzzles") is False:
            self.activeHighlight = False

            self.removeEffects()
            for tc_name in self.tcs_names:
                self.TC_end(tc_name)
            self.tcs_names = []
            return False

        self.activeHighlight = True

        scene_name = SceneManager.getCurrentSceneName()
        active_transitions = TransitionManager.getOpenSceneTransitions(scene_name)

        for active_transition in active_transitions:
            self.setTransitionHighlight(active_transition)

        return False

    def __cbSceneInit(self, scene_name):
        if Mengine.getCurrentAccountSettingBool("DifficultyCustomSparklesOnHOPuzzles") is False:
            return False

        self.activeHighlight = True

        active_transitions = TransitionManager.getOpenSceneTransitions(scene_name)

        for active_transition in active_transitions:
            self.setTransitionHighlight(active_transition)

        return False

    def __cbSceneLeave(self, _):
        self.activeHighlight = False

        self.removeEffects()
        for tc_name in self.tcs_names:
            self.TC_end(tc_name)
        self.tcs_names = []

        return False

    def removeEffects(self):
        for effect in self.effects.values():
            self.removeEffect(effect)

        self.effects = {}

    def removeEffect(self, effect):
        effect.removeFromParent()
        effect.onFinalize()
        effect.onDestroy()

    def __cbTransitionBlockOpen(self, transition_object, value):
        current_scene_name = SceneManager.getCurrentSceneName()

        if current_scene_name is None:
            return False

        if self.activeHighlight is False:
            return False

        if value is True:
            if transition_object not in self.effects.keys():
                return False

            effect = self.effects[transition_object]
            self.removeEffect(effect)
            del self.effects[transition_object]

            return False

        enable = transition_object.getEnable()
        if enable is False:
            return False

        block_open = transition_object.getParam("BlockOpen")
        if block_open is True:
            return False

        self.setTransitionHighlight(transition_object)

        return False

    def setTransitionHighlight(self, transition_object):
        if TransitionHighlightManager.hasTransitionHighlight(transition_object.name) is False:
            return

        if transition_object in self.effects.keys():
            return

        name = transition_object.getName()
        transition_highlight = TransitionHighlightManager.getTransitionHighlight(name)
        effect_name = transition_highlight.prototypeName

        if transition_object.hasObject(effect_name) is True:
            return

        prototype_group = GroupManager.getGroup(transition_highlight.prototypeGroupName)
        effect_params = dict(EmitterName=effect_name)
        effect = prototype_group.generateObject("{}_{}".format(transition_highlight.prototypeName, name),
                                                transition_highlight.prototypeName, effect_params)

        if effect is None:
            return

        transition_entity = transition_object.getEntity()

        effect_entity_node = effect.getEntityNode()
        transition_entity.addChild(effect_entity_node)

        hotspot = transition_entity.getHotSpot()
        polygon_center = hotspot.getLocalPolygonCenter()
        effect.setPosition(polygon_center)

        self.effects[transition_object] = effect
        tc_name = "TransitionHighlight_{}".format(name)
        self.tcs_names.append(tc_name)
        with TaskManager.createTaskChain(Name=tc_name, Repeat=True) as tc:
            tc.addScope(self.Difficulty_Turn_On)
            tc.addFunction(effect.setEnable, True)
            with tc.addRaceTask(2) as (tc_play, tc_listener):
                tc_play.addScope(self.Highlight_Show, effect)

                tc_listener.addListener(Notificator.onChangeDifficulty)
                tc_listener.addScope(self.Difficulty_Turn_Off)
                tc_listener.addTask("AliasObjectAlphaTo", Object=effect, Time=500.0, From=1.0, To=0.0)
                tc_listener.addFunction(effect.setEnable, False)

    def Highlight_Show(self, source, effect):
        with source.addParallelTask(2) as (tc_1, tc_2):
            tc_1.addTask("AliasObjectAlphaTo", Object=effect, Time=1500.0, From=0.0, To=1.0)
            tc_2.addTask("TaskMovie2Play", Movie2=effect, Loop=True)

    def Difficulty_Turn_On(self, source):
        if Mengine.getCurrentAccountSettingBool("DifficultyCustomSparklesOnHOPuzzles"):
            pass
        else:
            source.addListener(Notificator.onChangeDifficulty)
            source.addScope(self.Difficulty_Turn_On)

    def Difficulty_Turn_Off(self, source):
        if Mengine.getCurrentAccountSettingBool("DifficultyCustomSparklesOnHOPuzzles"):
            source.addListener(Notificator.onChangeDifficulty)
            source.addScope(self.Difficulty_Turn_Off)

    def TC_end(self, arg=None):
        if TaskManager.existTaskChain(arg):
            TaskManager.cancelTaskChain(arg)

    def IsObjectHighlightedNow(self, transitionObject):
        """
        Check if for some transitionObject/zoomObject is active highlight effect
        """
        lightEffect = self.effects.get(transitionObject, None)
        if lightEffect:
            return lightEffect.isActive() and lightEffect.getEnable()

        return False
