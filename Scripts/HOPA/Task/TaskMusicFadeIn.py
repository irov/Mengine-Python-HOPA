from Foundation.SceneManager import SceneManager
from Foundation.Task.Task import Task
from Notification import Notification


class TaskMusicFadeIn(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskMusicFadeIn, self)._onParams(params)
        self.FadeTime = params.get("FadeTime", 2.0)
        self.easing = params.get("Easing", "easyLinear")

        self.id = 0
        pass

    def _onRun(self):
        self.id = Mengine.musicFadeIn(self.FadeTime, self.easing, self.__musicPause)
        Notification.notify(Notificator.onCommandMusicFadeIn, SceneManager.getCurrentSceneName())
        return False
        pass

    def __musicPause(self, fadeID, isEnd):
        if self.id != fadeID:
            return
        Mengine.musicPause()
        self.complete()
        pass

    def _onSkip(self):
        remove_id = self.id
        self.id = 0

        # Mengine.scheduleRemove(remove_id)
        pass

    pass
