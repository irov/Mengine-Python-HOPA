from Foundation.SceneManager import SceneManager
from Foundation.Task.Task import Task
from Notification import Notification


class TaskMusicFadeIn(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskMusicFadeIn, self)._onParams(params)
        self.FadeTime = params.get("FadeTime", 2.0)
        self.easing = params.get("Easing", "easyLinear")
        pass

    def _onRun(self):
        Mengine.musicFadeIn(self.FadeTime, self.easing, self.__musicPause)
        Notification.notify(Notificator.onCommandMusicFadeIn, SceneManager.getCurrentSceneName())
        return False

    def __musicPause(self, isEnd):
        Mengine.musicPause()
        self.complete()
        pass

    def _onSkip(self):
        pass

    pass
