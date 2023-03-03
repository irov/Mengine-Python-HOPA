from Foundation.ArrowManager import ArrowManager
from Foundation.Task.MixinObjectTemplate import MixinMovieItem
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskMovieItemClick(MixinMovieItem, MixinObserver, Task):
    def _onParams(self, params):
        super(TaskMovieItemClick, self)._onParams(params)
        pass

    def _onRun(self):
        self.MovieItem.setParam("Interactive", 1)

        self.addObserverFilter(Notificator.onMovieItemClick, self._onMovieItemClick, self.MovieItem)
        return False
        pass

    def _onMovieItemClick(self, movieButton):
        if ArrowManager.emptyArrowAttach() is False:
            return False
            pass

        self.MovieItem.setParam("Interactive", 0)

        return True
        pass

    pass
