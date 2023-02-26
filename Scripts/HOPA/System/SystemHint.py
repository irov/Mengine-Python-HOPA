from Event import Event
from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.Notificator import Notificator
from Foundation.PolicyManager import PolicyManager
from Foundation.StateManager import StateManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager

class SystemHint(System):
    def __init__(self):
        super(SystemHint, self).__init__()
        self.totalTimeToReload = 0
        self.scheduleId = 0
        self.StateHintChargeId = "StateHintCharge"
        self.timeLeft = 0
        self.CurrentTiming = None
        self.Demon_Hint = None
        self.startReload = False

        self.HintGroup = None

        self.cache_reload_time = None

        ''' for calling show hint action from code '''
        self.showHintEvent = None

    def _onInitialize(self):
        super(SystemHint, self)._onInitialize()

    def _onRun(self):
        self.addObserver(Notificator.onSceneInit, self.__onSceneInit)
        self.addObserver(Notificator.onStateChange, self.__onStateChange)
        self.addObserver(Notificator.onHintClick, self.__onHintClick)
        self.addObserver(Notificator.onHintActivate, self.__onHintActivate)
        self.addObserver(Notificator.onChangeDifficulty, self.__onChangeDifficulty)
        self.addObserver(Notificator.onSetReloading, self.__onSetReloading)

        self.showHintEvent = Event("ShowHintEvent")
        self.addEvent(self.showHintEvent, self.__onShowHintEvent)

        if self.totalTimeToReload > self.timeLeft and self.startReload is True:
            time = self.timeLeft

            self.startReloading(time)

            StateManager.changeState("StateHintCharge", False)
            StateManager.changeState("StateHintReady", False)

        if _DEVELOPMENT:
            def checkEditBox():
                if SystemManager.hasSystem("SystemEditBox"):
                    system_edit_box = SystemManager.getSystem("SystemEditBox")
                    if system_edit_box.hasActiveEditbox():
                        return False
                return True

            with self.createTaskChain("ForceShowHintOnKey", Repeat=True) as tc:
                tc.addTask('TaskKeyPress', Keys=[DefaultManager.getDefaultKey("DevDebugShowHintKey", 'VK_Q')])
                with tc.addIfTask(checkEditBox) as (tc_true, _):
                    tc_true.addFunction(self.showHintEvent)

        return True

    def _onStop(self):
        self.resetReloading()

    def _onSave(self):
        CurrentTiming = self.getCurrentTiming()
        timeLeft = self.getReloadTimeLeft()

        data_save = (CurrentTiming, timeLeft, self.totalTimeToReload, self.startReload)
        return data_save

    def _onLoad(self, data_save):
        self.CurrentTiming, self.timeLeft, self.totalTimeToReload, self.startReload = data_save

        if self.startReload is True:
            if self.totalTimeToReload > self.timeLeft:
                time = self.timeLeft
            else:
                time = self.totalTimeToReload

            self.startReloading(time)

    # -------------- Observer's Callbacks ------------------------------------------------------------------------------
    def __onShowHintEvent(self, cb=None):
        hintDemon = self.getHintObject()

        if hintDemon.isActive():
            hint = hintDemon.entity

            hint.currentHintEnd()
            hintAction = hint.hintGive()

            if hintAction is not None:
                if cb is not None:
                    with TaskManager.createTaskChain() as tc:
                        tc.addListener(Notificator.onHintActionEnd)
                        tc.addFunction(cb)

                hint.hintShow(hintAction)

                return

        if cb is not None:
            cb()

    def __onHintActivate(self, hint):
        if hint == self.Demon_Hint:
            return False

        self.Demon_Hint = hint
        self.HintGroup = self.Demon_Hint.getGroup()
        self.totalTimeToReload = self.getTotalReloadingTime()
        return False

    def __onSceneInit(self, _sceneName):
        if self.isOnSchedule() is False:
            return False
        if self.HintGroup is None:
            return False
        if self.HintGroup.hasObject("Movie2_Reload") is False:
            return False

        CurrentTiming = self.getCurrentTiming()
        Movie_Reload = self.HintGroup.getObject("Movie2_Reload")

        self.getTotalReloadingTime()
        Movie_Reload.setStartTiming(CurrentTiming)
        return False

    def __onChangeDifficulty(self, _difficulty):
        current_reload_time = Mengine.getCurrentAccountSetting("DifficultyCustomHintTime")
        if self.cache_reload_time is None:
            self.cache_reload_time = current_reload_time
            return False
        elif self.cache_reload_time == current_reload_time:
            return False

        self.cache_reload_time = current_reload_time

        if self.HintGroup is None:
            return False

        if self.HintGroup.hasObject("Movie2_Reload") is False:
            return False

        totalReloadingTime = self.getTotalReloadingTime()
        self.totalTimeToReload = totalReloadingTime
        self.resetReloading()
        self.startReloading(totalReloadingTime)

        Movie_Reload = self.HintGroup.getObject("Movie2_Reload")
        CurrentTiming = self.getCurrentTiming()
        Movie_Reload.setStartTiming(CurrentTiming)

        if not Movie_Reload.isActive():
            return False

        StateManager.changeState("StateHintCharge", False)
        StateManager.changeState("StateHintReady", False)

        if self.HintGroup.getEnable() is False:
            MovieGroup = self.getHintObject().getGroup()
            Movie2_Reload = MovieGroup.getObject("Movie2_Reload")
            Movie2_Reload.setEnable(True)
            Movie_ReloadDuration = Movie2_Reload.getDuration()
            CurrentReloadTiming = self.getCurrentTiming()

            if Movie_ReloadDuration == CurrentReloadTiming:
                if self.isReloadStarted() is False:
                    Movie2_Reload.setLastFrame(True)
                    return False

                CurrentReloadTiming = 0

            if MovieGroup.hasObject("Movie2_Ready"):
                Movie_Ready = MovieGroup.getObject("Movie2_Ready")
                Movie_Ready.setEnable(False)

            if MovieGroup.hasObject("Movie2_Ready_Effect"):
                Movie_Ready = MovieGroup.getObject("Movie2_Ready_Effect")
                Movie_Ready.setEnable(False)

            Movie2_Reload.setStartTiming(CurrentReloadTiming)

            StateManager.changeState("StateHintCharge", True)
            StateManager.changeState("StateHintReady", True)

        else:
            PolicyHintReload = PolicyManager.getPolicy("HintReload")
            PolicyHintReadyInterrupt = PolicyManager.getPolicy("HintReadyInterrupt")

            with TaskManager.createTaskChain(Repeat=False) as tc:
                tc.addTask(PolicyHintReadyInterrupt)
                tc.addTask(PolicyHintReload)

                tc.addTask("TaskStateChange", ID="StateHintCharge", Value=True)
                tc.addTask("TaskStateChange", ID="StateHintReady", Value=True)

        return False

    def __onHintClick(self, _object, valid, *args):
        if valid is False:
            return False

        self.startReload = True

        return False

    def __onStateChange(self, ID, newValue, *_):
        if ID != self.StateHintChargeId:
            return False
        if newValue is False:
            return False
        if self.isOnSchedule() is True:
            return False

        self.startReloading(self.totalTimeToReload)

        return False

    def __onSetReloading(self, reloadTime=2000):
        self.resetReloading()
        self.startReloading(reloadTime)
        return False

    # ------------------------------------------------------------------------------------------------------------------
    def isReloadStarted(self):
        return self.startReload

    def getHintObject(self):
        if self.Demon_Hint is None:
            self.Demon_Hint = DemonManager.getDemon("Hint")
        return self.Demon_Hint

    def getTotalReloadingTime(self):
        HintReloadTime = Mengine.getCurrentAccountSettingFloat("DifficultyCustomHintTime")

        if self.HintGroup.hasObject("Movie2_Reload") is False:
            return HintReloadTime

        Movie_Reload = self.HintGroup.getObject("Movie2_Reload")
        Movie_ReloadDuration = Movie_Reload.getDuration()

        Movie_Reload.setSpeedFactor(Movie_ReloadDuration / HintReloadTime)

        return HintReloadTime

    def getReloadTimeLeft(self):
        if self.timeLeft is not None:
            timeLeft = self.timeLeft
            self.timeLeft = None
            return timeLeft

        if self.scheduleId == 0:
            return 0.0

        timeLeft = Mengine.scheduleGlobalPassed(self.scheduleId)
        if timeLeft <= 0:
            timeLeft = 1

        return timeLeft

    def getReloadPercentage(self):
        if self.isOnSchedule() is False:
            return 100

        if self.totalTimeToReload == 0 or self.totalTimeToReload is None:
            return 0

        timeLeft = self.getReloadTimeLeft()
        percents = round((100 * timeLeft) / self.totalTimeToReload)
        return percents

    def getCurrentTiming(self):
        if self.HintGroup is None:
            return 0

        percentsLeft = self.getReloadPercentage()

        Movie_Reload = self.HintGroup.getObject("Movie2_Reload")
        Movie_ReloadDuration = Movie_Reload.getDuration()

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
        self.resetReloading()
        self.startReload = False

    def startReloading(self, reloadTime):
        self.attachSchedule(reloadTime)
        Notification.notify(Notificator.onHintStartReloading, reloadTime)

    def resetReloading(self):
        StateManager.changeState("StateHintCharge", False)

        if self.isOnSchedule() is False:
            return

        self.removeSchedule()

    def attachSchedule(self, reloadTime):
        if self.scheduleId != 0:
            Trace.log("System", 0, "Hint.attachSchedule already exist schedule %d" % self.scheduleId)
            return

        self.scheduleId = Mengine.scheduleGlobal(reloadTime, self.__onSchedule)

        if self.scheduleId == 0:
            Trace.log("System", 0, "Hint.attachSchedule invalid schedule")
            return

    def isOnSchedule(self):
        state = self.scheduleId != 0
        return state

    def removeSchedule(self):
        if Mengine.scheduleGlobalRemove(self.scheduleId) is False:
            Trace.trace()

        self.scheduleId = 0