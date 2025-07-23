from Foundation.DemonManager import DemonManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from Foundation.Utils import isCollectorEdition


class SystemAchievementPlate(System):

    def _onRun(self):
        if self.__checkEnable() is False:
            return True

        if DemonManager.hasDemon("AchievementsInGameMenu"):
            self.demon = DemonManager.getDemon('AchievementsInGameMenu')
        else:
            self.demon = None

        self.askWait = False
        self.queue = []

        self._setObservers()

        return True

    def __checkEnable(self):
        """ returns True if CE or state from param `Achievements` """
        if Mengine.hasGameParam("Achievements") is True:
            return Mengine.getGameParamBool("Achievements", False) is True

        if _DEVELOPMENT is True:
            Trace.log("System", 3, "DEPRECATED warning: add param 'Achievements' to config to handling achievements")

        return isCollectorEdition() is True

    def _setObservers(self):
        self.addObserver(Notificator.onAddAchievementPlateToQueue, self.__cbAddAchievementsPlateToQueue)
        self.addObserver(Notificator.onZoomClick, self.__cbCloseAchievementsPlate)
        self.addObserver(Notificator.onTransitionClick, self.__cbCloseAchievementsPlate)
        self.addObserver(Notificator.onItemCollectInit, self.__cbCloseAchievementsPlate)
        self.addObserver(Notificator.onCloseCurrentItemCollect, self.__cbCloseAchievementsPlate)
        self.addObserver(Notificator.onItemClick, self.__cbCloseAchievementsPlate)
        self.addObserver(Notificator.onSceneChange, self.__cbAskAchievementsPlateToWait)
        self.addObserver(Notificator.onSceneInit, self.__cbAskAchievementsPlateToResume)

    def __cbAddAchievementsPlateToQueue(self, type_, name):
        if type_ == "Achievements":
            # wait a bit to know if scene changes
            with TaskManager.createTaskChain(Repeat=False) as tc:
                tc.addDelay(2000.0)
                tc.addFunction(self.delayPlate, type_, name)

        self.demonAppendParam(type_, name)

        return False

    def delayPlate(self, type_, name):
        if self.askWait:
            self.queue.append([type_, name])

    def __cbAskAchievementsPlateToWait(self, *args, **kwargs):
        self.askWait = True

        return False

    def __cbAskAchievementsPlateToResume(self, *args, **kwargs):
        self.askWait = False
        while len(self.queue) > 0:
            element = self.queue.pop(0)
            type_ = element[0]
            name = element[1]
            self.demonAppendParam(type_, name)

        return False

    def __cbCloseAchievementsPlate(self, item=None, *args, **kwargs):
        Notification.notify(Notificator.onCloseAchievementPlate)

        return False

    def demonAppendParam(self, type_, name):
        if self.demon:
            self.demon.appendParam('{}Queue'.format(type_), name)
