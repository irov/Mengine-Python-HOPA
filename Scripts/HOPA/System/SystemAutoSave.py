from Foundation.DefaultManager import DefaultManager
from Foundation.SessionManager import SessionManager
from Foundation.Providers.AdvertisementProvider import AdvertisementProvider
from Foundation.System import System
from HOPA.StageManager import StageManager
from Notification import Notification


IGNORE_SAVE_SCENES = ["Advertising"]
NO_RESTART_FORCE_SAVE_SCENES = ["CutScene", "PreIntro", "Intro", "SplashScreen", "Store", "Advertising"]
ALWAYS_SAVE_SCENES = ["CutScene"]

SCHEDULE_NOT_ACTIVE = 0


class SystemAutoSave(System):

    """
        saves game automatically:
            - AutoTransitionSave is True: after scene removed if ready (every AutoTransitionSaveDelaySeconds seconds)
            - Every time game was hidden on mobile device
            - When onCheatAutoSave (use -cheats)
    """

    def __init__(self):
        super(SystemAutoSave, self).__init__()

        self.saveReady = False
        self.scheduleId = SCHEDULE_NOT_ACTIVE

    def _onRun(self):
        self.addObserver(Notificator.onCheatAutoSave, self.__cheatAutoSave)

        if Mengine.hasTouchpad() is True:
            self.addObserver(Notificator.onApplicationWillResignActive, self._forceSave)

        if DefaultManager.getDefaultBool("AutoTransitionSave", False) is True:
            self.addObserver(Notificator.onSceneRemoved, self.__onSceneRemoved)
            self._schedule()

        self.__addDevToDebug()

        return True

    def _onStop(self):
        self._removeSchedule()

    def _forceSave(self):
        cur_scene = Mengine.getCurrentScene()

        if cur_scene is None:
            self.__cheatAutoSave()
            return False
        elif cur_scene.getName() in NO_RESTART_FORCE_SAVE_SCENES:
            self.__cheatAutoSave()
            return False

        if AdvertisementProvider.isShowingInterstitialAdvert() is True:
            self._schedule()
            return False

        if AdvertisementProvider.isShowingRewardedAdvert() is True:
            self._schedule()
            return False

        def _cbRestart(scene, isActive, isError):
            if scene is None:
                self.__cheatAutoSave()
                return
            if isActive is True:
                Notification.notify(Notificator.onSceneInit, scene.sceneName)

        Notification.notify(Notificator.onSceneRestartBegin)
        Mengine.restartCurrentScene(True, _cbRestart)
        Notification.notify(Notificator.onSceneRestartEnd)

        return False

    def __cheatAutoSave(self):
        self._autoSave()
        self._schedule()

        return False

    def _schedule(self):
        self._removeSchedule()
        save_delay = DefaultManager.getDefaultFloat("AutoTransitionSaveDelaySeconds", 60)
        save_delay *= 1000  # convert to ms
        self.scheduleId = Mengine.scheduleGlobal(save_delay, self._onSchedule)

    def _removeSchedule(self):
        if self.scheduleId == SCHEDULE_NOT_ACTIVE:
            return
        if Mengine.scheduleGlobalRemove(self.scheduleId) is False:
            Trace.log("System", 0, "Failed to remove global schedule with id {}".format(self.scheduleId))
        self.scheduleId = SCHEDULE_NOT_ACTIVE

    def _onSchedule(self, scheduleId, isComplete):
        if self.scheduleId != scheduleId:
            return

        if isComplete is True:
            self.setSaveReady(True)

        self.scheduleId = SCHEDULE_NOT_ACTIVE

    def __onSceneRemoved(self, SceneName):
        if SceneName in ALWAYS_SAVE_SCENES:
            self.setSaveReady(True)
        elif SceneName in IGNORE_SAVE_SCENES:
            return False

        if self.isSaveReady() is False:
            return False

        self._autoSave()
        self._schedule()

        return False

    def _autoSave(self):
        currentStage = StageManager.getCurrentStage()

        if currentStage is None:
            return

        if SessionManager.saveSession() is False:
            Trace.log("System", 0, "SystemAutoSave _save: invalid save Session")

        self.setSaveReady(False)

    def setSaveReady(self, state):
        self.saveReady = state

    def isSaveReady(self):
        return self.saveReady is True

    def __addDevToDebug(self):
        if Mengine.isAvailablePlugin("DevToDebug") is False:
            return

        tab = Mengine.getDevToDebugTab("Cheats") or Mengine.addDevToDebugTab("Cheats")

        widget = Mengine.createDevToDebugWidgetButton("save_game")
        widget.setTitle("Save game")
        widget.setClickEvent(Notification.notify, Notificator.onCheatAutoSave)

        tab.addWidget(widget)
