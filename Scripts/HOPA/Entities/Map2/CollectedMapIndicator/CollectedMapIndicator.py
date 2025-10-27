from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from HOPA.TransitionManager import TransitionManager

from CollectedMapIndicatorManager import CollectedMapIndicatorManager


class CollectedMapIndicator(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addActionActivate("CurrentValue", Update=CollectedMapIndicator.__updateCurrentValue)
        Type.addActionActivate("CurrentCollectedMap")
        pass

    def __init__(self):
        super(CollectedMapIndicator, self).__init__()
        self.CurrentMovie = None
        pass

    def __updateCurrentValue(self, value):
        if self.CurrentMovie is not None:
            self.CurrentMovie.setEnable(False)
        self.updateMovie(value)
        pass

    def _onPreparation(self):
        super(CollectedMapIndicator, self)._onPreparation()
        Data = CollectedMapIndicatorManager.getData(self.object.getName())
        for movie in Data.itervalues():
            movie.setEnable(False)
            pass
        pass

    def _onActivate(self):
        super(CollectedMapIndicator, self)._onActivate()
        pass

    def _onDeactivate(self):
        super(CollectedMapIndicator, self)._onDeactivate()
        self.cancelTaskChains()
        pass

    def updateMovie(self, value):
        movie = CollectedMapIndicatorManager.getCurrentValueMovie(self.object.getName(), value)
        if movie is None:
            return
        movie.setEnable(True)
        self.CurrentMovie = movie
        movieEn = movie.getEntity()
        if movieEn.hasSocket("socket") is False:
            return
            pass
        self.runTasks()
        pass

    def runTasks(self):
        self.cancelTaskChains()
        with TaskManager.createTaskChain(Name="CollectedMapIndicator", Repeat=True) as tc:
            tc.addTask("TaskMovieSocketClick", SocketName="socket", Movie=self.CurrentMovie)
            tc.addPrint("Here Must Be Transition to Collected Map")
            tc.addFunction(TransitionManager.changeScene, self.CurrentCollectedMap)
        pass

    def cancelTaskChains(self):
        if TaskManager.existTaskChain("CollectedMapIndicator") is True:
            TaskManager.cancelTaskChain("CollectedMapIndicator")
            pass
        pass

    pass
