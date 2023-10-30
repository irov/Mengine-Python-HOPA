from Foundation.DefaultManager import DefaultManager
from Foundation.SessionManager import SessionManager
from Foundation.System import System
from HOPA.StageManager import StageManager
from Notification import Notification


IGNORE_SAVE_SCENES = ["Advertising"]
NO_RESTART_FORCE_SAVE_SCENES = ["CutScene", "PreIntro", "Intro", "SplashScreen", "Store"]
ALWAYS_SAVE_SCENES = ["CutScene"]


class SystemAutoSave(System):
    def _onParams(self, params):
        super(SystemAutoSave, self)._onParams(params)

        self.AutoSave = True
        self.saveReady = False

        self.scheduleId = 0

    def _onRun(self):
        AutoTransitionSave = DefaultManager.getDefaultBool("AutoTransitionSave", False)

        self.addObserver(Notificator.onCheatAutoSave, self.__cheatAutoSave)

        if Mengine.hasTouchpad() is True:
            self._setMobilePauseAutoSave()

        if AutoTransitionSave is True:
            self.addObserver(Notificator.onSceneRemoved, self.__onSceneRemoved)
            self._schedule()

        self.__addDevToDebug()

        return True

    def _setMobilePauseAutoSave(self):
        self.addObserver(Notificator.onApplicationWillResignActive, self._forceSave)

    def __addDevToDebug(self):
        if Mengine.isAvailablePlugin("DevToDebug") is False:
            return

        tab = Mengine.getDevToDebugTab("Cheats") or Mengine.addDevToDebugTab("Cheats")

        widget = Mengine.createDevToDebugWidgetButton("save_game")
        widget.setTitle("Save game")
        widget.setClickEvent(Notification.notify, Notificator.onCheatAutoSave)

        tab.addWidget(widget)

    def _forceSave(self):
        cur_scene = Mengine.getCurrentScene()

        if cur_scene is None:
            self.__cheatAutoSave()
            return False
        elif cur_scene.getName() in NO_RESTART_FORCE_SAVE_SCENES:
            self.__cheatAutoSave()
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
        save_delay = DefaultManager.getDefaultFloat("AutoTransitionSaveDelaySeconds", 60)
        save_delay *= 1000  # convert to ms
        self.scheduleId = Mengine.scheduleGlobal(save_delay, self._onSchedule)

    def _onSchedule(self, ID, isRemoved):
        if self.scheduleId != ID:
            return

        self.scheduleId = 0
        self.saveReady = True

    def _onStop(self):
        if self.scheduleId != 0:
            Mengine.scheduleGlobalRemove(self.scheduleId)
            self.scheduleId = 0

        AutoTransitionSave = DefaultManager.getDefaultBool("AutoTransitionSave", False)
        if AutoTransitionSave is False:
            return

    def __onSceneRemoved(self, SceneName):
        if SceneName in ALWAYS_SAVE_SCENES:
            self.saveReady = True
        elif SceneName in IGNORE_SAVE_SCENES:
            return False

        if self.saveReady is False:
            return False

        if self.scheduleId != 0:
            if Mengine.scheduleGlobalRemove(self.scheduleId) is False:
                Trace.trace()

        self._autoSave()
        self._schedule()

        return False

    def _autoSave(self):
        if self.AutoSave is False:
            return

        currentStage = StageManager.getCurrentStage()

        if currentStage is None:
            return

        if SessionManager.saveSession() is False:
            Trace.log("System", 0, "SystemAutoSave _save: invalid save Session")

        self.saveReady = False
