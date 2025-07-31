from Foundation.SceneManager import SceneManager
from Foundation.Task.Task import Task
from Notification import Notification


class TaskMusicFadeOut(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskMusicFadeOut, self)._onParams(params)
        self.FadeTime = params.get("FadeTime", 2.0)
        pass

    def _onRun(self):
        Mengine.musicResume()
        Mengine.musicFadeOut(self.FadeTime, self.__musicResume)
        Notification.notify(Notificator.onCommandMusicFadeOut, SceneManager.getCurrentSceneName())
        return False

    def __musicResume(self, isEnd):
        self.complete()
        pass

    def _onSkip(self):
        pass

    pass
