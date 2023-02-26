from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from HOPA.TransitionManager import TransitionManager

from MagicVisionManager import MagicVisionManager

class MagicVision(BaseEntity):
    Socket_Name = "Socket_MagicVision"
    Movie_ReadyName = "Movie_Ready"
    Movie_ActivateName = "Movie_Activate"
    Movie_RechargeName = "Movie_Recharge"
    Movie_ChargingCompleteName = "Movie_ChargingComplete"

    PRE_ACTIVATE = "preActivate"
    ACTIVATE = "activate"
    READY = "ready"
    CHARGE = "charging"
    CHARGE_COMPLETE = "chargingComplete"

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addActionActivate(Type, "State", Update=MagicVision.stateUpdate)
        Type.addAction(Type, "AllDoneScenes")
        Type.addAction(Type, "BlockedScenes")
        pass

    def __init__(self):
        super(MagicVision, self).__init__()
        self.Socket = None
        self.activateFlag = False
        self.deactivateFlag = False
        self.timing = 0
        self.saveReload = 0
        pass

    def getSocket(self):
        return self.Socket
        pass

    def changeState(self, isSkip=False):
        if isSkip is True:
            return True
            pass
        if self.deactivateFlag is True:
            return True
            pass

        currentState = self.object.getState()
        if currentState == MagicVision.CHARGE:
            self.saveReload = 0
            self.timing = 0
            setState = MagicVision.CHARGE_COMPLETE
            pass
        elif currentState == MagicVision.CHARGE_COMPLETE:
            setState = MagicVision.READY
            pass
        elif currentState == MagicVision.READY:
            setState = MagicVision.PRE_ACTIVATE
            pass
        elif currentState == MagicVision.PRE_ACTIVATE:
            setState = MagicVision.ACTIVATE
            pass
        elif currentState == MagicVision.ACTIVATE:
            setState = MagicVision.CHARGE
            pass
        self.object.setState(setState)
        return True
        pass

    def stateUpdate(self, value):
        currentSceneName = SceneManager.getCurrentGameSceneName()
        if MagicVisionManager.isMagicVisionScene(currentSceneName) is True:  # for case if from MV open Map, Diary, Journal etc
            self.deactivateFlag = False
            pass

        if self.activateFlag == True:
            self.activateFlag = False
            self.object.setParam("State", MagicVision.ACTIVATE)
            return
            pass

        if self.deactivateFlag == True:  # for case when we leave MV scene
            self.deactivateFlag = False
            self.object.setParam("State", MagicVision.CHARGE)
            return
            pass

        if value == MagicVision.PRE_ACTIVATE:
            self.preActivate()
            pass
        if value == MagicVision.ACTIVATE:
            self.activate()
            pass
        elif value == MagicVision.READY:
            self.ready()
            pass
        elif value == MagicVision.CHARGE_COMPLETE:
            self.chargingComplete()
            pass
        elif value == MagicVision.CHARGE:
            self.recharging()
            pass
        pass

    def setTotalReloadingTime(self):
        MagicVisionReloadTime = DefaultManager.getDefaultFloat("MagicVisionReloadTime", 3)

        if Mengine.hasCurrentAccountSetting("Difficulty") is True:
            Difficulty = Mengine.getCurrentAccountSetting("Difficulty")
            TypeMagicVisionReloadTime = "%sMagicVisionReloadTime" % (Difficulty)

            if DefaultManager.hasDefault(TypeMagicVisionReloadTime) is True:
                MagicVisionReloadTime = DefaultManager.getDefaultFloat(TypeMagicVisionReloadTime, 3)
                pass
            pass

        MagicVisionReloadTime *= 1000  # speed fix

        Movie_Reload = self.object.getObject(MagicVision.Movie_RechargeName)
        Movie_ReloadDuration = Movie_Reload.getDuration()

        if Movie_ReloadDuration != MagicVisionReloadTime:
            speedFactor = Movie_ReloadDuration / MagicVisionReloadTime
            Movie_Reload.setAnimationSpeedFactor(speedFactor)
            pass

        return
        pass

    def recharging(self):
        RechargeMode = DefaultManager.getDefault("MagicVisionRechargeMode", "Repeat")
        if RechargeMode == "Repeat":
            self.repeatCharge()
            return
            pass
        if RechargeMode == "Scale":
            self.scaleCharge()
            return
            pass
        pass

    def scaleCharge(self):
        MovieEn = self.Movie_Recharge.getEntity()
        self.setTotalReloadingTime()
        self.cancelTaskChains()
        with TaskManager.createTaskChain(Name="MagicVisionRecharge", Cb=self.changeState) as tc_charge:
            tc_charge.addTask("TaskEnable", Object=self.Movie_Recharge)
            tc_charge.addTask("TaskFunction", Fn=MovieEn.setTiming, Args=(self.timing,))
            tc_charge.addTask("TaskMoviePlay", Movie=self.Movie_Recharge, Wait=True, Skiped=False)
            tc_charge.addTask("TaskEnable", Object=self.Movie_Recharge, Value=False)
            pass

        # with TaskManager.createTaskChain(Name = "MagicVisionRechargeMind", Repeat = True) as tc_chargeMind:
        #     tc_chargeMind.addTask("TaskSocketClick", Socket = self.Socket)
        #     tc_chargeMind.addTask("AliasMindPlay", MindID = "ID_MV_CHARGE")
        #     pass
        pass

    def setRepeatReloadingTime(self):
        MagicVisionRepeatRecharge = DefaultManager.getDefaultFloat("MagicVisionRepeatRecharge", 10)

        Difficulty = Mengine.getCurrentAccountSetting("Difficulty")
        if Difficulty != u"":
            TypeMagicVisionRepeatRecharge = "%sMagicVisionRepeatRecharge" % (Difficulty)
            if DefaultManager.hasDefault(TypeMagicVisionRepeatRecharge) is True:
                MagicVisionRepeatRecharge = DefaultManager.getDefaultFloat(TypeMagicVisionRepeatRecharge, 10)
                pass
            pass

        MagicVisionRepeatRecharge *= 1000  # speed fix

        value = MagicVisionRepeatRecharge
        if self.saveReload != 0:
            return self.saveReload
            pass
        return value
        pass

    def repeatCharge(self):
        rechargeTime = self.setRepeatReloadingTime()
        self.cancelTaskChains()
        MovieEn = self.Movie_Recharge.getEntity()
        MovieEn.setPlayCount(rechargeTime)

        with TaskManager.createTaskChain(Name="MagicVisionRecharge", Cb=self.changeState) as tc_charge:
            tc_charge.addTask("TaskEnable", Object=self.Movie_Recharge)
            tc_charge.addTask("TaskFunction", Fn=MovieEn.setTiming, Args=(self.timing,))
            tc_charge.addTask("TaskMoviePlay", Movie=self.Movie_Recharge, Wait=True, Skiped=False)
            tc_charge.addTask("TaskEnable", Object=self.Movie_Recharge, Value=False)
            pass

        # with TaskManager.createTaskChain(Name = "MagicVisionRechargeMind", Repeat = True) as tc_chargeMind:
        #     tc_chargeMind.addTask("TaskSocketClick", Socket = self.Socket)
        #     tc_chargeMind.addTask("AliasMindPlay", MindID = "ID_MV_CHARGE")
        #     pass
        pass

    def chargingComplete(self):
        self.cancelTaskChains()
        with TaskManager.createTaskChain(Name="MagicVisionChargingComplete", Cb=self.changeState) as tc_chargeComplete:
            tc_chargeComplete.addTask("TaskEnable", Object=self.Movie_ChargingComplete)
            tc_chargeComplete.addTask("TaskMoviePlay", Movie=self.Movie_ChargingComplete)
            tc_chargeComplete.addTask("TaskEnable", Object=self.Movie_ChargingComplete, Value=False)
            pass
        pass

    def _readySwitch(self, isSkip, cb):
        currentSceneName = SceneManager.getCurrentGameSceneName()
        sceneNameTo = MagicVisionManager.getSceneNameTo(currentSceneName)

        if sceneNameTo is None:
            cb(isSkip, 1)
            return
            pass
        elif sceneNameTo in self.AllDoneScenes:
            cb(isSkip, 1)
            return
            pass
        elif sceneNameTo in self.BlockedScenes:
            cb(isSkip, 1)
            return
            pass
        else:
            cb(isSkip, 0)
            return
            pass
        pass

    def preActivate(self):
        currentSceneName = SceneManager.getCurrentGameSceneName()
        sceneNameTo = MagicVisionManager.getSceneNameTo(currentSceneName)
        movieTransition = MagicVisionManager.getActivateMovie(currentSceneName)
        self.cancelTaskChains()

        def flag():
            self.activateFlag = True
            pass

        with TaskManager.createTaskChain(Name="MagicVisionPreActivate") as tc:
            tc.addTask("TaskFunction", Fn=flag)
            tc.addTask("TaskEnable", Object=self.Movie_Activate)
            tc.addTask("TaskMoviePlay", Movie=self.Movie_Activate, Wait=False, Loop=True)

            with GuardBlockInput(tc) as guard_tc:
                guard_tc.addTask("TaskEnable", Object=movieTransition)
                guard_tc.addTask("TaskMoviePlay", Movie=movieTransition, Wait=True)
                pass

            tc.addTask("TaskEnable", Object=movieTransition, Value=False)
            tc.addTask("TaskFunction", Fn=TransitionManager.changeScene, Args=(sceneNameTo, None, False,))
            pass
        pass

    def ready(self):
        self.cancelTaskChains()

        with TaskManager.createTaskChain(Name="MagicVisionReady") as tc_ready:
            tc_ready.addTask("TaskEnable", Object=self.Movie_Ready)
            tc_ready.addTask("TaskMoviePlay", Movie=self.Movie_Ready, Loop=True, Wait=False)
            pass

        with TaskManager.createTaskChain(Name="MagicVisionPreReady", Repeat=True) as tc_do:
            tc_do.addTask("TaskSocketClick", Socket=self.Socket)
            with tc_do.addSwitchTask(2, self._readySwitch) as (tc_ok, tc_no):
                tc_ok.addTask("TaskEnable", Object=self.Movie_Ready, Value=False)
                tc_ok.addTask("TaskSetParam", Object=self.object, Param="State", Value=MagicVision.PRE_ACTIVATE)

                # tc_no.addTask("AliasMindPlay", MindID = "ID_MV_INVALID")
                tc_no.addTask("TaskDummy")
                pass
            pass
        pass

    def activate(self):
        currentSceneName = SceneManager.getCurrentSceneName()
        sceneNameTo = MagicVisionManager.getSceneNameFrom(currentSceneName)
        movieTransition = MagicVisionManager.getDeactivateMovie(currentSceneName)
        self.cancelTaskChains()

        with TaskManager.createTaskChain(Name="MagicVisionClick") as tc:
            tc.addTask("TaskEnable", Object=self.Movie_Ready)
            tc.addTask("TaskMoviePlay", Movie=self.Movie_Ready, Wait=False, Loop=True)
            tc.addTask("TaskSocketClick", Socket=self.Socket)

            with GuardBlockInput(tc) as guard_tc:
                guard_tc.addTask("TaskEnable", Object=movieTransition)
                guard_tc.addTask("TaskMoviePlay", Movie=movieTransition, Wait=True)
                guard_tc.addTask("TaskEnable", Object=movieTransition, Value=False)
                guard_tc.addTask("TaskEnable", Object=self.Movie_Ready, Value=False)
                pass

            tc.addTask("TaskFunction", Fn=TransitionManager.changeScene, Args=(sceneNameTo, None, False,))
            pass
        pass

    def _onPreparation(self):
        super(MagicVision, self)._onPreparation()
        self.Movie_Ready = self.object.getObject(MagicVision.Movie_ReadyName)
        self.Movie_Ready.setEnable(False)
        self.Movie_Activate = self.object.getObject(MagicVision.Movie_ActivateName)
        self.Movie_Activate.setEnable(False)
        self.Movie_Recharge = self.object.getObject(MagicVision.Movie_RechargeName)
        self.Movie_Recharge.setEnable(False)
        self.Movie_ChargingComplete = self.object.getObject(MagicVision.Movie_ChargingCompleteName)
        self.Movie_ChargingComplete.setEnable(False)

        self.Socket = self.object.getObject(MagicVision.Socket_Name)

        currentSceneName = SceneManager.getCurrentSceneName()
        if MagicVisionManager.hasActivateMovie(currentSceneName) is True:
            movieTransition = MagicVisionManager.getActivateMovie(currentSceneName)
            movieTransition.setEnable(False)
            pass

        if MagicVisionManager.hasDeactivateMovie(currentSceneName) is True:
            movieTransition = MagicVisionManager.getDeactivateMovie(currentSceneName)
            movieTransition.setEnable(False)
            pass
        pass

    def _onActivate(self):
        super(MagicVision, self)._onActivate()
        pass

    def _onPreparationDeactivate(self):
        super(MagicVision, self)._onPreparationDeactivate()
        currentState = self.object.getState()
        if currentState == MagicVision.ACTIVATE:
            self.deactivateFlag = True
            pass
        if currentState == MagicVision.CHARGE:
            MovieRechargingEntity = self.Movie_Recharge.getEntity()
            self.timing = MovieRechargingEntity.getTiming()
            self.saveReload = MovieRechargingEntity.getPlayIterator()
            self.deactivateFlag = True
            pass
        pass

    def _onDeactivate(self):
        super(MagicVision, self)._onDeactivate()
        self.cancelTaskChains()
        pass

    def cancelTaskChains(self):
        if TaskManager.existTaskChain("MagicVisionClick"):
            TaskManager.cancelTaskChain("MagicVisionClick")
            pass

        if TaskManager.existTaskChain("MagicVisionReady"):
            TaskManager.cancelTaskChain("MagicVisionReady")
            pass

        if TaskManager.existTaskChain("MagicVisionRecharge"):
            TaskManager.cancelTaskChain("MagicVisionRecharge")
            pass

        # if TaskManager.existTaskChain("MagicVisionRechargeMind"):
        #     TaskManager.cancelTaskChain("MagicVisionRechargeMind")
        #     pass

        if TaskManager.existTaskChain("MagicVisionChargingComplete"):
            TaskManager.cancelTaskChain("MagicVisionChargingComplete")
            pass

        if TaskManager.existTaskChain("MagicVisionPreActivate"):
            TaskManager.cancelTaskChain("MagicVisionPreActivate")
            pass

        if TaskManager.existTaskChain("MagicVisionPreReady"):
            TaskManager.cancelTaskChain("MagicVisionPreReady")
            pass
        pass
    pass