from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager

from AwardsManager import AwardsManager

class Awards(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addActionActivate(Type, "Open", Update=Awards.__updateOpen)
        Type.addActionActivate(Type, "Count", Update=Awards.__updateCount)
        pass

    def __init__(self):
        super(Awards, self).__init__()
        pass

    def cleanData(self):
        if TaskManager.existTaskChain("Awards%s" % self.MovieName):
            TaskManager.cancelTaskChain("Awards%s" % self.MovieName)
            pass
        self.Socket_Over.setInteractive(False)
        pass

    def _onDeactivate(self):
        self.cleanData()
        pass

    def _onPreparation(self):
        super(Awards, self)._onPreparation()
        awardData = AwardsManager.getAwardData(self.object)
        self.MovieName = awardData.getMovieName()
        self.OpenTextID = awardData.getOpenTextID()
        self.MaxCount = awardData.getAvailableOptionsCount()
        self.ImageCount = awardData.getImageCount()
        pass

    def _onActivate(self):
        self.movie = self.object.getObject(self.MovieName)
        self.Socket_Over = self.object.getObject("Socket_Over")
        self.Socket_Over.setInteractive(True)

        with TaskManager.createTaskChain(Name="Awards%s" % self.MovieName, Repeat=True) as tc:
            tc.addTask("TaskSocketEnter", Socket=self.Socket_Over, AutoEnable=False)
            tc.addTask("TaskEnable", Object=self.movie, Value=True)
            tc.addTask("TaskMoviePlay", Movie=self.movie, Wait=False)
            with tc.addRaceTask(2) as (tc1, tc2):
                tc1.addTask("TaskSocketLeave", Socket=self.Socket_Over, AutoEnable=False)
                tc1.addTask("TaskDelay", Time=0.1 * 1000)  # soeed fix
                tc1.addTask("TaskMovieStop", Movie=self.movie)

                tc2.addTask("TaskMovieEnd", Movie=self.movie)
                pass
            tc.addTask("TaskEnable", Object=self.movie, Value=False)
            pass

        pass

    def __updateOpen(self, value):
        Text_Count = self.object.getObject("Text_Count")
        Text_Count.setEnable(value)

        if self.ImageCount is False and self.MaxCount != self.Count:
            self.__enableImage(False)
            return
            pass

        self.__enableImage(value)
        pass

    def __enableImage(self, value):
        Sprite_Open = self.object.getObject("Sprite_Open")
        Sprite_Open.setEnable(value)
        pass

    def __updateCount(self, value):
        if self.MaxCount == 1:
            return
            pass

        Text_Count = self.object.getObject("Text_Count")
        Text_Count.setTextID("ID_AWARDS")
        Text_Count.setTextArgs((value, self.MaxCount))
        pass

    pass