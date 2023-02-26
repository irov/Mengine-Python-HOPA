from Foundation.ArrowManager import ArrowManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.PullManager import PullManager

class SystemPull(System):
    def __init__(self):
        super(SystemPull, self).__init__()
        self.watched_sockets = {}
        pass

    def _onRun(self):
        self.addObserver(Notificator.onPullArrowAttach, self.__onPullArrowAttach)
        self.addObserver(Notificator.onPullArrowDetach, self.__onPullArrowDetach)
        self.addObserver(Notificator.onPullWrong, self.__onPullWrong)
        self.addObserver(Notificator.onSocketMouseEnter, self.__onSocketMouseEnter)
        self.addObserver(Notificator.onSocketMouseLeave, self.__onSocketMouseLeave)
        pass

    def _onStop(self):
        pass

    def __onPullArrowAttach(self, direction, transform, socket):
        self.watched_sockets[socket] = direction
        return False
        pass

    def __onPullArrowDetach(self, direction, socket):
        del self.watched_sockets[socket]
        return False
        pass

    def __onPullWrong(self, item, movieWrong):
        self.__onWrong(item, movieWrong)
        return False
        pass

    def __onSocketMouseEnter(self, socket):
        if socket not in self.watched_sockets.keys():
            return False
            pass

        direction = self.watched_sockets[socket]
        PullCursorMode = PullManager.getCursorMode(direction)
        currentCursor = ArrowManager.getCursorMode()
        if currentCursor == PullCursorMode:
            return False
            pass

        ArrowManager.setCursorMode(PullCursorMode)
        return False
        pass

    def __onSocketMouseLeave(self, socket):
        if socket not in self.watched_sockets.keys():
            return False
            pass

        direction = self.watched_sockets[socket]
        PullCursorMode = PullManager.getCursorMode(direction)
        currentCursor = ArrowManager.getCursorMode()
        if currentCursor != PullCursorMode:
            return False
            pass

        ArrowManager.setCursorMode("Default")
        return False
        pass

    def __onWrong(self, item, movieWrong):
        with TaskManager.createTaskChain() as tc:
            tc.addTask("TaskMoviePlay", Movie=movieWrong)
            tc.addTask("TaskObjectReturn", Object=item)
            pass
        pass

    pass