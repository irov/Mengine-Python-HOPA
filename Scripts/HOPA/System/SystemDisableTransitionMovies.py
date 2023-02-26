from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.System import System
from HOPA.TransitionManager import TransitionManager

class SystemDisableTransitionMovies(System):
    def _onParams(self, params):
        super(SystemDisableTransitionMovies, self)._onParams(params)
        pass

    def _onRun(self):
        moviesIn = TransitionManager.getInMovies()
        moviesOut = TransitionManager.getOutMovies()
        for movie in moviesIn + moviesOut:
            movie.setEnable(False)
            pass

        DefaultFadeOutGroup = DefaultManager.getDefault("TransitionFadeOutGroup", None)
        TransitionFadeOutMovie = DefaultManager.getDefault("TransitionFadeOutMovie", None)
        if DefaultFadeOutGroup is not None and TransitionFadeOutMovie is not None:
            FadeOutTransition = GroupManager.getObject(DefaultFadeOutGroup, TransitionFadeOutMovie)
            FadeOutTransition.setEnable(False)
            pass
        pass

    def _onStop(self):
        pass
    pass