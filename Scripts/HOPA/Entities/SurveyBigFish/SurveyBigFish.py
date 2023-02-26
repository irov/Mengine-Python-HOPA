from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.Task.Semaphore import Semaphore
from Foundation.TaskManager import TaskManager
from HOPA.TransitionManager import TransitionManager

ALPHA = 400.0

class PurchaseButton(object):
    IDLE = 0
    OVER = 1
    PRESSED = 2

    def __init__(self, idle, over, pressed):
        self.movies = {self.IDLE: idle, self.OVER: over, self.PRESSED: pressed}

        self.cur_movie = idle
        self.cur_state = self.IDLE

        idle.setEnable(True)
        over.setEnable(False)
        pressed.setEnable(False)

    def setState(self, new_state):
        self.cur_movie.setEnable(False)

        self.cur_movie = self.movies[new_state]
        self.cur_movie.setEnable(True)

        self.cur_state = new_state

        self.cur_movie.setPlay(True)

    def getClickEvent(self):
        return self.movies[self.OVER].onMovieSocketButtonEvent

    def getEnterEvent(self):
        return self.movies[self.IDLE].onMovieSocketEnterEvent

class SurveyBigFish(BaseEntity):
    def __init__(self):
        super(SurveyBigFish, self).__init__()

        self.ce_info = None
        self.se_info = None

        self.purchase_button_se = None
        self.purchase_button_ce = None

        self.button_menu = None

        self.tcs = []

        self.purchase_link_se = None
        self.purchase_link_ce = None

    def _onInitialize(self, *args, **kwargs):
        super(SurveyBigFish, self)._onInitialize(*args, **kwargs)

        getObject = self.object.getObject

        self.purchase_button_ce = PurchaseButton(getObject("Movie2_PurchaseCE_Idle"), getObject("Movie2_PurchaseCE_Over"), getObject("Movie2_PurchaseCE_Pressed"))
        self.purchase_button_ce.setState(PurchaseButton.OVER)

        self.purchase_button_se = PurchaseButton(getObject("Movie2_PurchaseSE_Idle"), getObject("Movie2_PurchaseSE_Over"), getObject("Movie2_PurchaseSE_Pressed"))

        self.se_info = self.object.getObject("Movie2_PurchaseSE_Info")
        self.se_info.setPlay(True)
        self.se_info.setLoop(True)
        self.se_info.setAlpha(0.0)

        self.ce_info = self.object.getObject("Movie2_PurchaseCE_Info")
        self.ce_info.setPlay(True)
        self.ce_info.setLoop(True)

        self.button_menu = self.object.getObject("Movie2Button_ToMenu")

        self.purchase_link_se = Mengine.getGameParamUnicode("SurveyBigFishSE")

        if self.purchase_link_se is None:
            msg = "SurveyBigFishSE is not found. Please set it in Configs.ini"

            Trace.log("Entity", 0, "SurveyBigFishSE is not found. Please set it in Configs.ini")

            self.purchase_link_se = (unicode("https://" + msg, "utf-8"))

        self.purchase_link_ce = Mengine.getGameParamUnicode("SurveyBigFishCE")

        if self.purchase_link_ce is None:
            msg = "SurveyBigFishCE is not found. Please set it in Configs.ini"

            Trace.log("Entity", 0, "SurveyBigFishCE is not found. Please set it in Configs.ini")

            self.purchase_link_ce = (unicode("https://" + msg, "utf-8"))

    def _onPreparation(self):
        super(SurveyBigFish, self)._onPreparation()

    def _onActivate(self):
        super(SurveyBigFish, self)._onActivate()

        """ TCS Open Purchase URL On Purchase Button Click """

        tc = TaskManager.createTaskChain(Repeat=True)
        self.tcs.append(tc)

        with tc as tc:
            ''' TC SE Click '''

            tc.addEvent(self.purchase_button_se.getClickEvent())

            tc.addFunction(self.purchase_button_se.setState, PurchaseButton.PRESSED)

            tc.addFunction(Mengine.openUrlInDefaultBrowser, self.purchase_link_se)

        tc = TaskManager.createTaskChain(Repeat=True)
        self.tcs.append(tc)

        with tc as tc:
            ''' TC CE Click '''

            tc.addEvent(self.purchase_button_ce.getClickEvent())

            tc.addFunction(self.purchase_button_ce.setState, PurchaseButton.PRESSED)

            tc.addFunction(Mengine.openUrlInDefaultBrowser, self.purchase_link_ce)

        """ TC Menu Transition On Menu Button Click """

        tc = TaskManager.createTaskChain()
        self.tcs.append(tc)

        with tc as tc:
            tc.addTask('TaskMovie2ButtonClick', Movie2Button=self.button_menu)
            tc.addFunction(TransitionManager.changeScene, "Menu")

        tc = TaskManager.createTaskChain()
        self.tcs.append(tc)

        """ TC Info CE/SE FlipFlop On Purchase Button Enter"""

        self.RunTCFlipFlopPurchaseInfo()

    def _onDeactivate(self):
        super(SurveyBigFish, self)._onDeactivate()

        for tc in self.tcs:
            tc.cancel()

        self.tcs = []

    def RunTCFlipFlopPurchaseInfo(self):
        """ TC'S Movie Info Appear/Disappear
        """

        en_ce_info = self.ce_info.getEntityNode()
        en_se_info = self.se_info.getEntityNode()

        semaphore = Semaphore(True, 'SurveyAppearDisappearCEInfo')

        ''' CE Movie Appear, SE Movie Disappear'''

        tc = TaskManager.createTaskChain(Repeat=True)
        self.tcs.append(tc)

        with tc as tc:
            tc.addEvent(self.purchase_button_ce.getEnterEvent())
            tc.addSemaphore(semaphore, From=True, To=False)

            tc.addFunction(self.purchase_button_ce.setState, PurchaseButton.OVER)

            tc.addFunction(self.purchase_button_se.setState, PurchaseButton.IDLE)

            with tc.addRaceTask(2) as (enter, interrupt):
                with enter.addParallelTask(2) as (ce_appear, se_disappear):
                    ce_appear.addTask('TaskNodeAlphaTo', Node=en_ce_info, To=1.0, Time=ALPHA, Interrupt=True)
                    se_disappear.addTask('TaskNodeAlphaTo', Node=en_se_info, To=0.0, Time=ALPHA, Interrupt=True)

                interrupt.addEvent(self.purchase_button_se.getEnterEvent())

            tc.addSemaphore(semaphore, To=True)

        ''' SE Movie Appear, CE Movie Disappear '''

        tc = TaskManager.createTaskChain(Repeat=True)
        self.tcs.append(tc)

        with tc as tc:
            tc.addEvent(self.purchase_button_se.getEnterEvent())
            tc.addSemaphore(semaphore, From=True, To=False)

            tc.addFunction(self.purchase_button_se.setState, PurchaseButton.OVER)

            tc.addFunction(self.purchase_button_ce.setState, PurchaseButton.IDLE)

            with tc.addRaceTask(2) as (enter, interrupt):
                with enter.addParallelTask(2) as (se_appear, ce_disappear):
                    se_appear.addTask('TaskNodeAlphaTo', Node=en_se_info, To=1.0, Time=ALPHA, Interrupt=True)
                    ce_disappear.addTask('TaskNodeAlphaTo', Node=en_ce_info, To=0.0, Time=ALPHA, Interrupt=True)

                interrupt.addEvent(self.purchase_button_ce.getEnterEvent())

            tc.addSemaphore(semaphore, To=True)