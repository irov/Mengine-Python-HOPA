from Foundation.SceneManager import SceneManager
from Foundation.Task.Task import Task
from Notification import Notification

class TaskMusicFadeOut(Task):
    Skiped = True
    def _onParams(self, params):
        super(TaskMusicFadeOut, self)._onParams(params)
        self.FadeTime = params.get("FadeTime", 2.0)

        self.id = 0
        pass

    def _onRun(self):
        Mengine.musicResume()
        self.id = Mengine.musicFadeOut(self.FadeTime, self.__musicResume)
        Notification.notify(Notificator.onCommandMusicFadeOut, SceneManager.getCurrentSceneName())
        return False
        pass

    def __musicResume(self, fadeID, isEnd):
        if self.id != fadeID:
            return
        self.complete()
        pass

    def _onSkip(self):
        remove_id = self.id
        self.id = 0

        # Mengine.scheduleRemove(remove_id)
        pass
    pass