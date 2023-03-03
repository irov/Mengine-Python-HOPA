from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.PolicyManager import PolicyManager
from Foundation.TaskManager import TaskManager
from Notification import Notification


class SkipPuzzle(BaseEntity):
    def __init__(self):
        super(SkipPuzzle, self).__init__()
        self.reloadTime = 0
        self.scheduleId = 0
        self.startReload = False

        self.PolicySkipPuzzleReady = None
        self.PolicySkipPuzzlePlay = None

        self.Movie_Reload = None
        self.Movie_Charged = None
        self.Movie_Activate = None

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "ForceReload")

    def runReloadSkipTC(self):
        if TaskManager.existTaskChain("SkipPuzzle"):
            TaskManager.cancelTaskChain("SkipPuzzle")

        with TaskManager.createTaskChain(Name="SkipPuzzle", Group=self.object) as tc:
            tc.addFunction(self.setupTimer)

            if self.object.hasObject("Movie2_Ready_Effect") is True:
                tc.addTask("TaskEnable", ObjectName="Movie2_Ready_Effect", Value=False)

            if self.object.hasObject("Movie2_Ready") is True:
                # tc.addTask("TaskObjectSetPosition", ObjectName = "Movie_Ready", Value = Position)
                tc.addTask("TaskSetParam", ObjectName="Movie2_Ready", Param="Loop", Value=False)
                tc.addTask("TaskMovie2Stop", Movie2Name="Movie2_Ready")

            if self.object.hasObject("Movie2_Ready") is True:
                tc.addTask("TaskEnable", ObjectName="Movie2_Ready", Value=False)

            if self.object.hasObject("Movie2_Activate") is True:
                tc.addTask("TaskEnable", ObjectName="Movie2_Activate", Value=False)

            if self.object.hasObject("Movie2_Reload") is True:
                tc.addTask("TaskEnable", ObjectName="Movie2_Reload", Value=True)
                tc.addTask("TaskMovie2Play", Movie2=self.Movie_Reload, Wait=True)
                tc.addTask("TaskEnable", ObjectName="Movie2_Reload", Value=False)

            if self.object.hasObject("Movie2_Charged") is True:
                tc.addTask("TaskEnable", ObjectName="Movie2_Charged", Value=True)
                tc.addTask("TaskMovie2Play", Movie2=self.Movie_Charged, Wait=True)
                tc.addTask("TaskEnable", ObjectName="Movie2_Charged", Value=False)

            tc.addFunction(self._State_Idle)

            with tc.addRepeatTask() as (repeat, until):
                # repeat task used for no reload if monetization is enabled
                # - user clicks skip, view dialogwindow and tc was repeated from the reloading

                repeat.addTask(self.PolicySkipPuzzleReady)
                repeat.addTask(self.PolicySkipPuzzlePlay)

                until.addListener(Notificator.onEnigmaSkip)

    def _onActivate(self):
        self.Movie_Reload = self.object.getObject("Movie2_Reload")

        if self.object.hasObject("Movie2_Charged") is True:
            self.Movie_Charged = self.object.getObject("Movie2_Charged")
            self.Movie_Charged.setEnable(False)

        if self.object.hasObject("Movie2_Activate") is True:
            self.Movie_Activate = self.object.getObject("Movie2_Activate")
            self.Movie_Activate.setLastFrame(False)

        self.onChangeDifficultyObserver = Notification.addObserver(Notificator.onChangeDifficulty, self.__filterOnChangeDifficulty)

        self.PolicySkipPuzzleReady = PolicyManager.getPolicy("PolicySkipPuzzleReady", "PolicySkipPuzzleReadyEffect")
        self.PolicySkipPuzzlePlay = PolicyManager.getPolicy("SkipPuzzlePlay", "PolicySkipPuzzlePlayDefault")

        self.runReloadSkipTC()

    def __filterOnChangeDifficulty(self, difficulty):
        current_reload_time = self.__getLoadSkipTime()
        if self.reloadTime is None:
            self.reloadTime = current_reload_time
            return False
        elif self.reloadTime == current_reload_time:
            return False

        self.removeSchedule()
        self.runReloadSkipTC()

        return False

    def _State_Idle(self):
        self.object.setParam("ForceReload", None)

    def _onDeactivate(self):
        super(SkipPuzzle, self)._onDeactivate()
        self.object.setParam("ForceReload", None)

        Notification.removeObserver(self.onChangeDifficultyObserver)

        self.removeSchedule()

        if TaskManager.existTaskChain("SkipPuzzle"):
            TaskManager.cancelTaskChain("SkipPuzzle")

    # -------------------------------------------------------------------------------------------------------------------

    def setupTimer(self):
        self.reloadTime = self.__getLoadSkipTime()

        CurrentTiming = self.getCurrentTiming()

        self.Movie_Reload.setStartTiming(CurrentTiming)
        self.attachSchedule(self.reloadTime)

        self.Movie_Reload.setLastFrame(False)
        Movie_ReloadDuration = self.Movie_Reload.getDuration()

        if Movie_ReloadDuration != self.reloadTime:
            speedFactor = Movie_ReloadDuration / self.reloadTime
            self.Movie_Reload.setSpeedFactor(speedFactor)

    def __getLoadSkipTime(self):
        if self.ForceReload is not None:
            return self.ForceReload
        return Mengine.getCurrentAccountSettingFloat("DifficultyCustomSkipTime")

    def getReloadTimeLeft(self):
        if self.scheduleId == 0:
            return 0.0

        timeLeft = Mengine.scheduleGlobalPassed(self.scheduleId)
        if timeLeft <= 0:
            timeLeft = 1

        return timeLeft

    def getReloadPercentage(self):
        if self.isOnSchedule() is False:
            return 100

        if self.reloadTime == 0 or self.reloadTime is None:
            return 0

        timeLeft = self.getReloadTimeLeft()
        percents = round((100 * timeLeft) / self.reloadTime)
        return percents

    def getCurrentTiming(self):
        if self.object is None:
            return 0

        percentsLeft = self.getReloadPercentage()

        Movie_ReloadDuration = self.Movie_Reload.getDuration()

        if percentsLeft == 100 or percentsLeft == 0:
            return 0

        curTime = (Movie_ReloadDuration * percentsLeft) / 100
        return curTime

    # -------------- Reload Schedule -----------------------------------------------------------------------------------
    def __onSchedule(self, scheduleId, isRemoved, *_):
        if self.scheduleId != scheduleId:
            return

        if isRemoved is False:
            return

        self.scheduleId = 0
        self.removeSchedule()
        self.startReload = False

    def attachSchedule(self, reloadTime):
        if self.scheduleId != 0:
            Trace.log("System", 0, "attachSchedule already exist schedule %d" % self.scheduleId)
            return

        self.scheduleId = Mengine.scheduleGlobal(reloadTime, self.__onSchedule)

        if self.scheduleId == 0:
            Trace.log("System", 0, "attachSchedule invalid schedule")
            return

    def isOnSchedule(self):
        state = self.scheduleId != 0
        return state

    def removeSchedule(self):
        if self.isOnSchedule() is False:
            return

        if Mengine.scheduleGlobalRemove(self.scheduleId) is False:
            Trace.trace()

        self.scheduleId = 0
