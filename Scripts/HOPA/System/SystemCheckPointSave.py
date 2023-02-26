from Foundation.DefaultManager import DefaultManager
from Foundation.SaveManager import SaveManager
from Foundation.SceneManager import SceneManager
from Foundation.SessionManager import SessionManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from HOPA.StageManager import StageManager
from HOPA.TransitionManager import TransitionManager
from HOPA.ZoomManager import ZoomManager

# todo: add keyboard shortcut feature


class SystemCheckPointSave(System):
    def _onParams(self, params):
        super(SystemCheckPointSave, self)._onParams(params)

    def _onRun(self):
        self.addObserver(Notificator.onKeyEvent, self.__onKeyEvent)
        return True

    def _onStop(self):
        pass

    def __onKeyEvent(self, key, x, y, isDown, isRepeat):
        if SceneManager.isCurrentGameScene() is False:
            return False

        if isDown is False:
            return False

        if SystemManager.hasSystem("SystemEditBox"):
            system_edit_box = SystemManager.getSystem("SystemEditBox")
            if system_edit_box.hasActiveEditbox():
                return False

        checkpoint_name = u"checkpoint.save"
        if key == DefaultManager.getDefaultKey("DevDebugSaveCheckpoint", "VK_S"):
            def __onSceneRestart(scene, isActive, isError):
                if scene is not None:
                    return

                currentStage = StageManager.getCurrentStage()

                if currentStage is None:
                    return

                save_session, save_types = SessionManager.getSaveData()

                gameSceneName = SceneManager.getCurrentGameSceneName()
                gameZoomName = ZoomManager.getCurrentGameZoomName()

                save_checkpoint = (save_session, gameSceneName, gameZoomName)

                if Mengine.writeGlobalPickleFile(checkpoint_name, save_checkpoint, save_types) is False:
                    Trace.log("System", 0, "SystemCheckPointSave invalid save {!r}".format(checkpoint_name))
                else:
                    Trace.msg("<SystemCheckPointSave> checkpoint successfully created as {!r}".format(checkpoint_name))
            Mengine.restartCurrentScene(True, __onSceneRestart)

        elif key == DefaultManager.getDefaultKey("DevDebugLoadCheckpoint", "VK_X"):
            Trace.msg("<SystemCheckPointSave> load checkpoint...")

            def __onSceneChangeDebugMenu(isSkip):
                accountID = Mengine.getCurrentAccountName()

                SessionManager.removeCurrentSession()
                SessionManager.selectAccount(accountID, False)

                pickle_types = SaveManager.getPickleTypes()

                try:
                    load_checkpoint = Mengine.loadGlobalPickleFile(checkpoint_name, pickle_types)
                except Exception as e:
                    Trace.log("System", 0, "<SystemCheckPointSave> can't load checkpoint {!r}: {}".format(checkpoint_name, e))
                    # todo: return last scene
                    return False

                load_session, gameSceneName, gameZoomName = load_checkpoint

                SessionManager.loadSaveData(load_session)

                Notification.notify(Notificator.onSessionNew, accountID)

                TransitionManager.changeScene(gameSceneName, gameZoomName, fade=False)
                Trace.msg("<SystemCheckPointSave> ...done!")

            TransitionManager.changeScene("DebugMenu", Cb=__onSceneChangeDebugMenu)

        return False