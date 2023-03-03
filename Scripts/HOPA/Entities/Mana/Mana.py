from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager

from ManaManager import ManaManager


class Mana(BaseEntity):
    IDLE = "Idle"
    HIDE = "Hide"
    SHOW = "Show"
    DOWN = "Down"

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addActionActivate(Type, "ManaCount", Update=Mana.__updateManaCount)
        Type.addActionActivate(Type, "HideState", Update=Mana.__updateHideState)
        pass

    def __init__(self):
        super(Mana, self).__init__()

        self.Text = None

        self.idleMovie = None
        self.hideMovie = None
        self.showMovie = None
        self.downMovie = None

        self.updateMovie = None

        self.MovieTextCounter = None
        self.entitiesToRemove = []
        pass

    def __updateHideState(self, value):
        if value == Mana.HIDE:
            self.hideChain()
            pass
        elif value == Mana.IDLE:
            self.idleChain()
            pass
        elif value == Mana.SHOW:
            self.showChain()
            pass
        elif value == Mana.DOWN:
            self.downChain()
            pass
        pass

    def removeFromParent(self):
        for entity in self.entitiesToRemove:
            entity.removeFromParent()
            pass
        self.entitiesToRemove = []
        pass

    def movieAttach(self, movie):
        movie.setEnable(True)
        movieEntity = movie.getEntity()
        slot = movieEntity.getMovieSlot("slot")
        self.attachToSlot(slot)
        pass

    def attachToSlot(self, slot):
        updateMovieEntity = self.updateMovie.getEntity()
        slot.addChild(updateMovieEntity)
        self.entitiesToRemove.append(updateMovieEntity)

        textCounterEntity = self.MovieTextCounter.getEntity()
        slot.addChild(textCounterEntity)
        self.entitiesToRemove.append(textCounterEntity)
        pass

    def idleChain(self):
        if self.idleMovie is None:
            return
            pass
        if TaskManager.existTaskChain("Hide_" + self.object.getName()):
            TaskManager.cancelTaskChain("Hide_" + self.object.getName())
            pass
        self.removeFromParent()
        self.movieAttach(self.idleMovie)
        pass

    def hideChain(self):
        if self.hideMovie is None:
            return
            pass
        self.cancelHideTaskChains()
        self.removeFromParent()
        self.movieAttach(self.hideMovie)
        with TaskManager.createTaskChain(Name="Hide_" + self.object.getName()) as tc:
            tc.addTask("TaskMoviePlay", Movie=self.hideMovie)
            tc.addTask("TaskSetParam", Object=self.object, Param="HideState", Value="Down")
            pass
        pass

    def showChain(self):
        if self.showMovie is None:
            return
            pass
        self.cancelHideTaskChains()
        self.removeFromParent()
        self.movieAttach(self.showMovie)
        with TaskManager.createTaskChain(Name="Show_" + self.object.getName()) as tc:
            tc.addTask("TaskMoviePlay", Movie=self.showMovie)
            tc.addTask("TaskSetParam", Object=self.object, Param="HideState", Value="Idle")
            pass
        pass

    def downChain(self):
        if self.downMovie is None:
            return
            pass

        self.removeFromParent()
        self.movieAttach(self.downMovie)
        pass

    def __updateManaCount(self, value):
        self.setupCounter(value)
        pass

    def playUpdateMovie(self):
        if TaskManager.existTaskChain("ManaEffect") is True:
            TaskManager.cancelTaskChain("ManaEffect")
            pass

        with TaskManager.createTaskChain(Name="ManaEffect") as tc:
            tc.addTask("TaskEnable", Object=self.updateMovie)
            tc.addTask("TaskMoviePlay", Movie=self.updateMovie, Wait=True, Loop=False)
            tc.addTask("TaskEnable", Object=self.updateMovie, Value=False)
            pass
        pass

    def _onPreparation(self):
        super(Mana, self)._onPreparation()
        self.prepareObjects()
        pass

    def prepareObjects(self):
        ManaData = ManaManager.getManaData(self.object)
        self.idleMovie = ManaData.getIdle()
        self.showMovie = ManaData.getShow()
        self.hideMovie = ManaData.getHide()
        self.downMovie = ManaData.getDown()

        self.MovieTextCounter = self.object.getObject("Movie_TextCounter")

        self.updateMovie = ManaData.getUpdate()
        self.updateMovie.setEnable(False)
        pass

    def _onActivate(self):
        super(Mana, self)._onActivate()
        pass

    def setupCounter(self, value):
        if self.Text is not None:
            self.destroyText()
            pass
        self.MovieTextCounter.setEnable(True)
        MovieEntity = self.MovieTextCounter.getEntity()
        Slot = MovieEntity.getMovieSlot("text")

        self.Text = Mengine.createNode("TextField")
        self.Text.setVerticalCenterAlign()
        self.Text.setCenterAlign()

        self.Text.setTextID("ID_Mana")
        self.Text.setTextArgs(value)

        self.Text.enable()
        Slot.addChild(self.Text)
        pass

    def _onDeactivate(self):
        super(Mana, self)._onDeactivate()
        self.destroyText()

        if TaskManager.existTaskChain("ManaEffect") is True:
            TaskManager.cancelTaskChain("ManaEffect")
            pass

        self.cancelHideTaskChains()
        self.removeFromParent()
        pass

    def destroyText(self):
        if self.Text is not None:
            self.Text.removeFromParent()
            Mengine.destroyNode(self.Text)
            self.Text = None
            pass
        pass

    def cancelHideTaskChains(self):
        if TaskManager.existTaskChain("Hide_" + self.object.getName()) is True:
            TaskManager.cancelTaskChain("Hide_" + self.object.getName())
            pass
        if TaskManager.existTaskChain("Show_" + self.object.getName()) is True:
            TaskManager.cancelTaskChain("Show_" + self.object.getName())
            pass
        pass

    def getUpdatePosition(self):
        MovieEntity = self.MovieTextCounter.getEntity()
        Slot = MovieEntity.getMovieSlot("position")
        pos = Slot.getWorldPosition()
        return pos
        pass

    pass
