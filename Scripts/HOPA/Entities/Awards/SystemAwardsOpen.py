from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager

from AwardsManager import AwardsManager


class SystemAwardsOpen(System):
    def _onParams(self, params):
        super(SystemAwardsOpen, self)._onParams(params)
        self.openAwards = {}
        self.awardsTempList = []
        pass

    def _onSave(self):
        return self.openAwards
        pass

    def _onLoad(self, data_save):
        self.openAwards = data_save
        pass

    def _onRun(self):
        self.addObserver(Notificator.onAwardsOpen, self.__onAwardsOpen)
        self.addObserver(Notificator.onSceneEnter, self.__onSceneEnter)
        self.addObserver(Notificator.onSceneLeave, self.__onSceneLeave)

        self.Movie_AwardsOpen = GroupManager.getObject("AwardsOpen", "Movie_AwardsOpen")
        self.Text_Open = GroupManager.getObject("AwardsOpen", "Text_Open")

        return True
        pass

    def __enableAwards(self, awardsID, count):
        Awards = AwardsManager.getAwards(awardsID)
        if Awards is None:
            return False
            pass

        Awards.setOpen(True)
        Awards.setCount(count)
        return False
        pass

    def __disableAwards(self, awardsID, count):
        Awards = AwardsManager.getAwards(awardsID)
        if Awards is None:
            return False
            pass

        Awards.setOpen(False)
        Awards.setCount(0)
        return False
        pass

    def __onAwardsOpen(self, awardsID):
        Awards = AwardsManager.getAwards(awardsID)
        awardData = AwardsManager.getAwardData(Awards)
        MaxCount = awardData.getAvailableOptionsCount()
        Count = Awards.getAvailableOptionsCount()

        if MaxCount == Count:
            return False
            pass

        Count += 1
        self.__enableAwards(awardsID, Count)

        self.openAwards[awardsID] = Count
        self.awardsTempList.append(awardsID)

        self.__checkValidate()
        return False
        pass

    def __showAwardOpen(self, awardsID):
        Awards = AwardsManager.getAwards(awardsID)
        if Awards is None:
            return False
            pass
        awardData = AwardsManager.getAwardData(Awards)
        TextID = awardData.getOpenTextID()
        self.Text_Open.setTextID(TextID)

        self.awardsTempList.remove(awardsID)

        alternativeMovie = AwardsManager.getAwardOpenMovie(awardsID)
        movie = self.Movie_AwardsOpen
        if alternativeMovie is not None:
            movie = alternativeMovie
            pass

        with TaskManager.createTaskChain(Name="AwardsOpenPlay", Cb=self.__removeCurrentAward) as tc:
            tc.addTask("TaskEnable", Object=movie, Value=True)
            tc.addTask("TaskPrint", Value="__showAwardOpen %s" % (movie.getName()))
            tc.addTask("TaskMoviePlay", Movie=movie, Wait=True)
            tc.addTask("TaskEnable", Object=movie, Value=False)
            pass
        pass

    def _onStop(self):
        if TaskManager.existTaskChain("AwardsOpenPlay"):
            TaskManager.cancelTaskChain("AwardsOpenPlay")
            pass

        self.openAwards = {}
        self.awardsTempList = []
        pass

    def __onSceneEnter(self, sceneName):
        self.__checkValidate()

        if len(self.awardsTempList) == 0:
            return False
            pass

        return False
        pass

    def __onSceneLeave(self, sceneName):
        self.__checkTasks()
        return False
        pass

    def __checkValidate(self):
        if len(self.awardsTempList) == 0:
            return
            pass

        if TaskManager.existTaskChain("AwardsOpenPlay") is True:
            return
            pass

        if SceneManager.isTransitionProgress() is True:
            return
            pass

        description = SceneManager.getCurrentDescription()
        descriptionName = description.getName()

        if SceneManager.hasLayerScene("AwardsOpen") is False:
            return
            pass

        nextAward = self.awardsTempList[0]
        self.__showAwardOpen(nextAward)
        pass

    def __checkTasks(self):
        if TaskManager.existTaskChain("AwardsOpenPlay") is True:
            TaskManager.cancelTaskChain("AwardsOpenPlay")
            pass
        pass

    def __removeCurrentAward(self, isSkip):
        self.__checkTasks()
        self.__checkValidate()
        pass

    pass
