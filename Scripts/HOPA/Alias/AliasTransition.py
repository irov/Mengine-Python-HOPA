from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.SceneManager import SceneManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.ZoomManager import ZoomManager

class AliasTransition(TaskAlias):
    # Skiped = False

    def _onParams(self, params):
        super(AliasTransition, self)._onParams(params)

        self.SceneName = params.get("SceneName")
        self.ZoomGroupName = params.get("ZoomGroupName", None)
        self.MovieIn = params.get("MovieIn", None)
        self.MovieOut = params.get("MovieOut", None)
        self.Intro = params.get("Intro", False)
        self.Wait = params.get("Wait", True)
        self.SkipTaskChains = params.get("SkipTaskChains", True)
        self.CheckToScene = params.get("CheckToScene", True)

        self.IgnoreGameScene = params.get("IgnoreGameScene", False)
        self.Bypass = params.get("Bypass", False)

        self.Fade = params.get("Fade", True)

        self.BlockInput = False

        self.alphaFadeIn = 1
        self.alphaFadeOut = 1

        default_fade_in_time = DefaultManager.getDefaultFloat("TransitionFadeInTime", 0.15) * 1000
        self.timeFadeIn = params.get("TimeFadeIn", default_fade_in_time)

        default_fade_out_time = DefaultManager.getDefaultFloat("TransitionFadeOutTime", 0.1) * 1000
        self.timeFadeOut = params.get("TimeFadeOut", default_fade_out_time)

        self.ZoomEffectTransitionObject = params.get("ZoomEffectTransitionObject", None)
        self.ZoomEffectTransitionBackObject = params.get("ZoomEffectTransitionBackObject", None)

        default_zoom_effect_factor = DefaultManager.getDefaultFloat("TransitionZoomEffectFactor", 1.5)
        self.ZoomEffectZoomFactor = params.get("ZoomEffectZoomFactor", default_zoom_effect_factor)

        default_in_easing = DefaultManager.getDefault("TransitionTweenIn", "easyLinear")
        self.easingIn = params.get("EasingIn", default_in_easing)

        default_out_easing = DefaultManager.getDefault("TransitionTweenOut", "easyLinear")
        self.easingOut = params.get("EasingOut", default_out_easing)
        pass

    def _onInitialize(self):
        super(AliasTransition, self)._onInitialize()

        self.BlockInput = GroupManager.hasObject("BlockInput", "Socket_Click")

        if _DEVELOPMENT is True:
            if self.SceneName is None:
                self.initializeFailed("SceneName is None")
                return

            DescriptionTo = SceneManager.getSceneDescription(self.SceneName)

            if DescriptionTo is None:
                self.initializeFailed("Not found description for scene '%s'" % (self.SceneName))

            if self.BlockInput is False:
                self.log("don't has BlockInput please add BlockInput.Socket_Click")

            if self.ZoomGroupName is not None:
                if ZoomManager.hasZoom(self.ZoomGroupName) is False:
                    self.initializeFailed("Not found description for Zoom '%s'" % (self.ZoomGroupName))

                Zoom = ZoomManager.getZoom(self.ZoomGroupName)
                FromSceneName = Zoom.getFromSceneName()

                if self.SceneName != FromSceneName:
                    self.initializeFailed("Zoom '%s' not inside in scene '%s' but inside scene '%s'" % (self.ZoomGroupName, self.SceneName, FromSceneName))

    def _onCheck(self):
        CurrentSceneName = SceneManager.getCurrentSceneName()

        if self.CheckToScene and self.SceneName == CurrentSceneName:
            return False

        ChangeSceneName = SceneManager.getChangeSceneName()

        if self.SceneName == ChangeSceneName:
            return False

        return True

    def _scope_zoom_effect_transition(self, source):
        CurrentScene = SceneManager.getCurrentScene()

        if CurrentScene is None:
            return

        MainLayer = CurrentScene.getMainLayer()

        cur_scale = MainLayer.getScale()

        scale_to = (
            cur_scale[0] * self.ZoomEffectZoomFactor,
            cur_scale[1] * self.ZoomEffectZoomFactor,
            cur_scale[2] * self.ZoomEffectZoomFactor,
        )

        if self.ZoomEffectTransitionObject.getType() in ["ObjectMovie2", "ObjectMovie2Button"]:
            entity_node = self.ZoomEffectTransitionObject.getEntityNode()
            point = entity_node.getWorldPosition()
        else:
            transition_entity = self.ZoomEffectTransitionObject.getEntity()
            hotspot = transition_entity.getHotSpot()
            point = hotspot.getWorldPolygonCenter()

        with source.addFork() as fork:
            fork.addTask("TaskNodeSetPosition", Node=MainLayer, Value=point)
            fork.addTask("TaskNodeSetOrigin", Node=MainLayer, Value=point)
            fork.addTask("TaskNodeScaleTo", Node=MainLayer, To=scale_to, Time=self.timeFadeIn, Easing=self.easingIn)

    def _scope_zoom_effect_transition_back(self, source, TransitionObject):
        CurrentScene = SceneManager.getCurrentScene()

        if CurrentScene is None:
            return

        MainLayer = CurrentScene.getMainLayer()

        cur_scale = MainLayer.getScale()

        scale_from = (
            cur_scale[0] * self.ZoomEffectZoomFactor,
            cur_scale[1] * self.ZoomEffectZoomFactor,
            cur_scale[2] * self.ZoomEffectZoomFactor,
        )

        transition_entity = TransitionObject.getEntity()
        hotspot = transition_entity.getHotSpot()
        point = hotspot.getWorldPolygonCenter()

        with source.addFork() as fork:
            fork.addTask("TaskNodeSetPosition", Node=MainLayer, Value=point)
            fork.addTask("TaskNodeSetOrigin", Node=MainLayer, Value=point)
            fork.addTask("TaskNodeScaleTo", Node=MainLayer, From=scale_from, To=cur_scale, Time=self.timeFadeOut, Easing=self.easingOut)

    def _onGenerate(self, source):
        CurrentSceneName = SceneManager.getCurrentSceneName()

        if self.IgnoreGameScene is True:  # I think it is cheating...
            GameScene = True
        else:
            GameScene = SceneManager.isGameScene(self.SceneName)

        # please, research why we can't force transition to non-game scenes and add description
        if self.Bypass is False:
            source.addTask("TaskTransitionUnblock", IsGameScene=GameScene)
            source.addTask("TaskTransitionBlock", Value=True, IsGameScene=GameScene)

        with GuardBlockInput(source, self.BlockInput) as guard_source:
            guard_source.addNotify(Notificator.onTransitionBegin, CurrentSceneName, self.SceneName, self.ZoomGroupName)

            # - Zoom effect -----------------------------------------------------------------------------
            if self.ZoomEffectTransitionObject is not None:
                guard_source.addScope(self._scope_zoom_effect_transition)
                pass

            if self.Intro is False:
                CurrentSceneName = SceneManager.getCurrentSceneName()

                if CurrentSceneName is not None:
                    if self.Fade is True:
                        if self.MovieIn is None:
                            # Take Fade group from default slots
                            Slot = SceneManager.getSceneDescription(CurrentSceneName)
                            if Slot.hasSlotsGroup("Fade") is True:
                                FadeGroupName = Slot.getSlotsGroup("Fade")
                                guard_source.addTask("AliasFadeIn", FadeGroupName=FadeGroupName, To=self.alphaFadeIn, Time=self.timeFadeIn)
                        else:
                            guard_source.addTask("TaskMoviePlay", Movie=self.MovieIn, AutoEnable=True, Wait=True, LastFrame=False)

                    guard_source.addTask("TaskSceneLeaving")

            PolicyAliasTransitionNormal = PolicyManager.getPolicy("AliasTransition", "PolicyAliasTransitionNormal")

            guard_source.addTask(PolicyAliasTransitionNormal, SceneName=self.SceneName, Wait=self.Wait, SkipTaskChains=self.SkipTaskChains, CheckToScene=self.CheckToScene)



            if self.ZoomGroupName is not None:
                guard_source.addNotify(Notificator.onZoomForceOpen, self.ZoomGroupName)
                # source.addTask("TaskNotify", ID = Notificator.onZoomOpen, Args = (self.ZoomGroupName, ))
                pass

            # - Zoom effect -----------------------------------------------------------------------------
            if self.ZoomEffectTransitionBackObject is not None:
                guard_source.addScope(self._scope_zoom_effect_transition_back, self.ZoomEffectTransitionBackObject)
            # elif self.ZoomEffectTransitionObject is not None:
            #     guard_source.addScope(self._scope_zoom_effect_transition_back, self.ZoomEffectTransitionObject)

            # -------------------------------------------------------------------------------------------

            if self.Intro is False:
                if self.Fade is True:
                    if self.MovieOut is None:
                        # Take Fade group from default slots
                        Slot = SceneManager.getSceneDescription(self.SceneName)
                        if Slot.hasSlotsGroup("Fade") is True:
                            FadeGroupName = Slot.getSlotsGroup("Fade")

                            # guard_source.addTask("TaskFadeSetStateFadeInComplete", GroupName=FadeGroupName)  # old hack
                            guard_source.addTask("AliasFadeOut", FadeGroupName=FadeGroupName,
                                                 From=self.alphaFadeOut, Time=self.timeFadeOut, FromIdle=True,
                                                 # enable fade out from IDLE state (alpha=0)
                                                 ResetFadeCount=True)
                    else:
                        guard_source.addTask("TaskMoviePlay", Movie=self.MovieOut, AutoEnable=True, Wait=True, LastFrame=False)

        if self.Bypass is False:
            source.addTask("TaskTransitionBlock", Value=False, IsGameScene=GameScene)

        source.addNotify(Notificator.onTransitionEnd, CurrentSceneName, self.SceneName, self.ZoomGroupName)

        if self.ZoomGroupName is None:
            source.addTask("TaskSceneEntering")