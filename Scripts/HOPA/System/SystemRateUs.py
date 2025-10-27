from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.Providers.RatingAppProvider import RatingAppProvider
from Foundation.TaskManager import TaskManager
from Foundation.Utils import getCurrentBusinessModel


class SystemRateUs(System):
    s_rate_accepted = False
    s_app_rated = False

    showed_rate_us_scenes = []

    def _onParams(self, params):
        super(SystemRateUs, self)._onParams(params)
        self.__scene_triggers = DefaultManager.getDefaultTuple("RateUsTriggerScenes", [], valueType=str)

    def _onRun(self):
        if Mengine.hasTouchpad() is False:
            return True

        if Mengine.getGameParamBool("AskRateUs", True) is False:
            return True

        if self.isAppRated() is True:
            return True

        if DefaultManager.getDefaultBool("DefaultRateUsUseOwnGroup", False) is True:
            # own group means group "RateUs"
            text_id = "ID_TEXT_RATE_US_MSG_{}".format(getCurrentBusinessModel().upper())
            Mengine.setTextAlias("", "$AliasRateUsMessage", text_id)

        self.addObserver(Notificator.onGameComplete, self._onChapterDone)
        self.addObserver(Notificator.onAppRated, self._onAppRated)
        if len(self.__scene_triggers) > 0:
            self.addObserver(Notificator.onSceneActivate, self._onSceneActivate)
        return True

    def _onStop(self):
        if TaskManager.existTaskChain("RateUsPrepare"):
            TaskManager.cancelTaskChain("RateUsPrepare")
        if TaskManager.existTaskChain("RateUs"):
            TaskManager.cancelTaskChain("RateUs")

    def _onChapterDone(self, *args):
        if self.isAppRated() is True:
            return True

        if SceneManager.getCurrentSceneName() == "Menu":
            self.askRate()
            return False

        self._prepareToShow()

        return False

    def _onAppRated(self):
        SystemRateUs.s_app_rated = True
        return True

    def _onSceneActivate(self, scene_name):
        if self.isAppRated() is True:
            return True

        if scene_name not in self.__scene_triggers:
            return False

        if scene_name in SystemRateUs.showed_rate_us_scenes:
            return False

        SystemRateUs.showed_rate_us_scenes.append(scene_name)
        self.askRate()

        return False

    def _prepareToShow(self):
        if TaskManager.existTaskChain("RateUsPrepare"):
            TaskManager.cancelTaskChain("RateUsPrepare")
        with TaskManager.createTaskChain(Name="RateUsPrepare") as tc:
            tc.addListener(Notificator.onSceneActivate, Filter=lambda scene_name: scene_name == "Menu")
            tc.addFunction(self.askRate)

    @staticmethod
    def askRate():
        if TaskManager.existTaskChain("RateUs") is True:
            return

        if DefaultManager.getDefaultBool("DefaultRateUsUseOwnGroup", False) is True:
            SystemRateUs._askRateWithRateUs()
        else:
            SystemRateUs._askRateWithDialogWindow()

    @staticmethod
    def _askRateWithRateUs():
        """ show group RateUs """

        if GroupManager.hasGroup("RateUs") is False:
            if _DEVELOPMENT is True:
                Trace.log("System", 0, "SystemRateUs can't show `RateUs` - group 'RateUs' not found")
            SystemRateUs.showRate()
            return

        with TaskManager.createTaskChain(Name="RateUs") as tc:
            with tc.addParallelTask(2) as (tc_fade, tc_enable):
                tc_fade.addTask("AliasFadeIn", FadeGroupName="FadeUI", To=0.5, Time=250.0)
                tc_enable.addTask("TaskSceneLayerGroupEnable", LayerName="RateUs", Value=True)

            with tc.addRaceTask(2) as (tc_rate, tc_later):
                tc_rate.addTask("TaskMovie2ButtonClick", GroupName="RateUs", Movie2ButtonName="Movie2Button_Ok")
                tc_rate.addFunction(SystemRateUs.__setRateAccepted, True)
                tc_rate.addFunction(SystemRateUs.showRate)
                tc_later.addTask("TaskMovie2ButtonClick", GroupName="RateUs", Movie2ButtonName="Movie2Button_Close")

            with tc.addParallelTask(2) as (tc_fade, tc_disable):
                tc_fade.addTask("AliasFadeOut", FadeGroupName="FadeUI", From=0.5, Time=250.0)
                tc_disable.addTask("TaskSceneLayerGroupEnable", LayerName="RateUs", Value=False)

    @staticmethod
    def _askRateWithDialogWindow():
        """ show `DialogWindow` - ask RateUs, then calls `showRate` """

        if DemonManager.hasDemon("DialogWindow") is False:
            if _DEVELOPMENT is True:
                Trace.log("System", 0, "Can't show `RateUs` window, coz demon `DialogWindow` not found")
            SystemRateUs.showRate()
            return

        DialogWindow = DemonManager.getDemon("DialogWindow")

        texts = {
            "title": "ID_TEXT_RATE_US_TITLE_{}".format(getCurrentBusinessModel().upper()),
            "question": "ID_TEXT_RATE_US_MSG_{}".format(getCurrentBusinessModel().upper()),
            "confirm": "ID_TEXT_RATE_US_RATE",
            "cancel": "ID_TEXT_RATE_US_LATER",
        }

        for text_id in texts.values():
            if Mengine.existText(text_id) is True:
                continue

            if _DEVELOPMENT is True:
                Trace.log("System", 0, "SystemRateUs not found text id {!r}. Check it all: {}".format(text_id, texts))

            SystemRateUs.showRate()
            return

        with TaskManager.createTaskChain(Name="RateUs") as tc:
            with tc.addParallelTask(2) as (tc_fade, tc_enable):
                tc_fade.addTask("AliasFadeIn", FadeGroupName="FadeUI", To=0.5, Time=250.0)
                tc_enable.addTask("TaskSceneLayerGroupEnable", LayerName="DialogWindow", Value=True)

            tc.addFunction(DialogWindow.run, text_ids=texts, urls=None)
            with tc.addRaceTask(2) as (confirm, cancel):
                confirm.addListener(Notificator.onDialogWindowConfirm)
                confirm.addFunction(SystemRateUs.__setRateAccepted, True)
                confirm.addFunction(SystemRateUs.showRate)
                cancel.addListener(Notificator.onDialogWindowCancel)

            with tc.addParallelTask(2) as (tc_fade, tc_disable):
                tc_fade.addTask("AliasFadeOut", FadeGroupName="FadeUI", From=0.5, Time=250.0)
                tc_disable.addTask("TaskSceneLayerGroupEnable", LayerName="DialogWindow", Value=False)

    @staticmethod
    def showRate():
        """ shows RateUs OS interface """
        RatingAppProvider.rateApp()

    # --- utils

    @staticmethod
    def __setRateAccepted(value):
        SystemRateUs.s_rate_accepted = bool(value)

    @staticmethod
    def isRateAccepted():
        """ :returns: True if player clicked `Rate` """
        return SystemRateUs.s_rate_accepted

    @staticmethod
    def isAppRated():
        """ :returns: True if app rated (got notify onAppRated) """
        return SystemRateUs.s_app_rated

    # --- Save\Load

    def _onSave(self):
        save_dict = {
            "rate_accepted": SystemRateUs.s_rate_accepted,
            "app_rated": SystemRateUs.s_app_rated,
            "showed_rate_us_scenes": SystemRateUs.showed_rate_us_scenes,
        }
        return save_dict

    def _onLoad(self, save_dict):
        SystemRateUs.s_rate_accepted = save_dict.get("rate_accepted", False)
        SystemRateUs.s_app_rated = save_dict.get("app_rated", False)
        SystemRateUs.showed_rate_us_scenes = save_dict.get("showed_rate_us_scenes", [])
