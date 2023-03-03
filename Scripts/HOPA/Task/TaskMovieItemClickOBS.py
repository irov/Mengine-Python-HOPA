from Foundation.Task.MixinObjectTemplate import MixinMovieItem
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskMovieItemClickOBS(MixinMovieItem, MixinObserver, Task):
    def _onParams(self, params):
        super(TaskMovieItemClickOBS, self)._onParams(params)
        pass

    def _onRun(self):
        self.addObserverFilter(Notificator.onMovieItemClick, self._onMovieItemPick, self.MovieItem)
        return False
        pass

    def _onMovieItemPick(self, movieButton):
        # if ArrowManager.emptyArrowAttach() is False:
        #     return False
        #     pass

        return True
        pass

    pass
