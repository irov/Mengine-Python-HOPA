from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskSplashScreenPlay(MixinObserver, Task):
    def _onParams(self, params):
        super(TaskSplashScreenPlay, self)._onParams(params)
        self.SplashScreen = DemonManager.getDemon("SplashScreen")
        pass

    def _onRun(self):
        self.addObserver(Notificator.onPlaySplashScreens, self._onPlaySplashScreens)

        self.SplashScreen.setParam("Play", True)

        return False
        pass

    def _onPlaySplashScreens(self):
        self.SplashScreen.setParam("Play", False)

        return True
        pass
    pass