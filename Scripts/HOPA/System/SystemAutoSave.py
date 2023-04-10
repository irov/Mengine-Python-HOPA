from Foundation.DefaultManager import DefaultManager
from Foundation.SessionManager import SessionManager
from Foundation.System import System
from HOPA.StageManager import StageManager
from Notification import Notification


class SystemAutoSave(System):
    def _onParams(self, params):
        super(SystemAutoSave, self)._onParams(params)

        self.AutoSave = True
        self.saveReady = False

        self.scheduleId = 0
        pass

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
        pause_notifications = [
            Notificator.oniOSApplicationWillResignActive,  # ios
            Notificator.onAndroidActivityPaused  # android
        ]

        for notificator in pause_notifications:
            self.addObserver(notificator, self._forceSave)

    def __addDevToDebug(self):
        if Mengine.isAvailablePlugin("DevToDebug") is False:
            return

        tab = Mengine.getDevToDebugTab("Cheats") or Mengine.addDevToDebugTab("Cheats")

        widget = Mengine.createDevToDebugWidgetButton("save_game")
        widget.setTitle("Save game")
        widget.setClickEvent(Notification.notify, Notificator.onCheatAutoSave)

        tab.addWidget(widget)

    def _forceSave(self):
        ignore_scenes = ["CutScene", "PreIntro", "Intro", "SplashScreen", "Store"]
        cur_scene = Mengine.getCurrentScene()
        if cur_scene is not None and cur_scene.getName() in ignore_scenes:
            self.__cheatAutoSave()
            return False

        def _cbRestart(scene, isActive, isError):
            print("cb restart", scene.sceneName if scene else None, isActive, isError)
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
        SystemSaveDelayTime = DefaultManager.getDefaultFloat("SystemSaveDelayTime", 60)
        SystemSaveDelayTime *= 1000  # speed fix
        self.scheduleId = Mengine.scheduleGlobal(SystemSaveDelayTime, self._onSchedule)
        pass

    def _onSchedule(self, ID, isRemoved):
        if self.scheduleId != ID:
            return
            pass

        self.scheduleId = 0

        self.saveReady = True
        pass

    def _onStop(self):
        if self.scheduleId != 0:
            Mengine.scheduleGlobalRemove(self.scheduleId)
            self.scheduleId = 0
            pass

        AutoTransitionSave = DefaultManager.getDefaultBool("AutoTransitionSave", False)
        if AutoTransitionSave is False:
            return
            pass
        pass

    def __onSceneRemoved(self, SceneName):
        if SceneName == "CutScene":
            self.saveReady = True

        if self.saveReady is False:
            return False
            pass

        if self.scheduleId != 0:
            if Mengine.scheduleGlobalRemove(self.scheduleId) is False:
                Trace.trace()
                pass
            pass

        self._autoSave()
        self._schedule()

        return False
        pass

    def _autoSave(self):
        if self.AutoSave is False:
            return
            pass

        currentStage = StageManager.getCurrentStage()

        if currentStage is None:
            return
            pass

        if SessionManager.saveSession() is False:
            Trace.log("System", 0, "SystemAutoSave _save: invalid save Session")
            pass

        self.saveReady = False
        pass

    pass
