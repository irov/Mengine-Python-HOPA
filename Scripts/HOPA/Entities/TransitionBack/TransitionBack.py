from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from Foundation.Task.Semaphore import Semaphore
from Foundation.TaskManager import TaskManager
from HOPA.TransitionManager import TransitionManager

class TransitionBack(BaseEntity):
    def __init__(self):
        super(TransitionBack, self).__init__()
        self.movie_transition_back = None

        self.timer = 600

        self.__tc_show = None
        self.__tc_hide = None

        self.semaphore = Semaphore(False, 'TransitionBackFinishTC')

    def __runTaskChain(self):
        node = self.movie_transition_back.getEntityNode()
        node.getRender().setLocalAlpha(0.0)

        self.__tc_hide = TaskManager.createTaskChain(Name="TransitionBackEffectHide", Repeat=True)
        with self.__tc_hide as tc:
            tc.addListener(Notificator.onTransitionBackMouseEnter)
            tc.addSemaphore(self.semaphore, From=False)

            with tc.addRaceTask(2) as (hide, interrupt):
                hide.addTask("TaskNodeAlphaTo", Node=node, To=1.0, Time=self.timer, Interrupt=True)
                interrupt.addListener(Notificator.onTransitionBackMouseLeave)

            tc.addSemaphore(self.semaphore, To=True)

        self.__tc_show = TaskManager.createTaskChain(Name="TransitionBackEffectShow", Repeat=True)
        with self.__tc_show as tc:
            tc.addListener(Notificator.onTransitionBackMouseLeave)
            tc.addSemaphore(self.semaphore, From=True)

            with tc.addRaceTask(2) as (show, interrupt):
                show.addTask("TaskNodeAlphaTo", Node=node, To=0.0, Time=self.timer, Interrupt=True)
                interrupt.addListener(Notificator.onTransitionBackMouseEnter)

            tc.addSemaphore(self.semaphore, To=False)

    def _onPreparation(self):
        super(TransitionBack, self)._onPreparation()

        if self.object.hasObject("Movie2_TransitionBack_Idle"):
            self.movie_transition_back = self.object.getObject("Movie2_TransitionBack_Idle")
        elif self.object.hasObject("Movie_TransitionBack_Idle"):
            self.movie_transition_back = self.object.getObject("Movie_TransitionBack_Idle")
        else:
            Trace.log("Entity", 0, "TransitionBack Should has 'Movie2_TransitionBack_Idle' or 'Movie_TransitionBack_Idle")

    def _onActivate(self):
        super(TransitionBack, self)._onActivate()

        if self.movie_transition_back is None:
            Trace.log("Entity", 0, "TransitionBack movie not found. Please add. To is this feature.")
            return

        # do not use transition back in mobile version (there will be navigation buttons)
        if Mengine.hasTouchpad():
            self.movie_transition_back.setEnable(False)
            transitionBack = self.object.getObject("Transition_Back")
            if transitionBack:
                transitionBack.setEnable(False)
            return

        sceneNameFrom = SceneManager.getCurrentSceneName()

        if TransitionManager.hasTransitionBack(sceneNameFrom) is True:
            self.movie_transition_back.setEnable(True)
            self.__runTaskChain()
        else:
            self.movie_transition_back.setEnable(False)

    def _onDeactivate(self):
        super(TransitionBack, self)._onDeactivate()

        if self.__tc_hide is not None:
            self.__tc_hide.cancel()
            self.__tc_hide = None

        if self.__tc_show is not None:
            self.__tc_show.cancel()
            self.__tc_show = None