from Foundation.ArrowManager import ArrowManager
from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from HOPA.TransitionManager import TransitionManager

class Achievements(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addActionActivate(Type, "PreviousSceneName")

    def __init__(self):
        super(Achievements, self).__init__()
        self.arrow = ArrowManager.getArrow()
        self.fade_time = DefaultManager.getDefaultFloat("AchievementSceneTextFade", 150.0)

        self.back_button = None
        self.tc_back_button = None

        self.button_with_texts = list()
        self.tc_text_on_cursor = list()

    def _onPreparation(self):
        SystemAchievements = SystemManager.getSystem("SystemAchievements")

        achievements = SystemAchievements.getAchievements()

        if self.object.hasObject('Movie2Button_Back'):
            self.back_button = self.object.getObject('Movie2Button_Back')

        for achievement in achievements.values():
            param = achievement.params
            button_unlocked = self.object.getObject(param.movie_unlocked)
            button_locked = self.object.getObject(param.movie_locked)

            if achievement.isComplete():
                button_locked.setEnable(False)
                button_unlocked.setEnable(True)
                current_button = button_unlocked
            else:
                button_locked.setEnable(True)
                button_unlocked.setEnable(False)
                current_button = button_locked

            movie_text = self.object.getObject(param.movie_text)
            self.arrow.addChild(movie_text.getEntityNode())
            movie_text.setAlpha(0.0)

            self.button_with_texts.append((current_button, movie_text))

    def __scopeTextAppear(self, source, button, text):
        text_node = text.getEntityNode()

        source.addTask('TaskMovie2ButtonEnter', Movie2Button=button)
        source.addDelay(1)

        with source.addRaceTask(2) as (enter, interrupt):
            enter.addTask("TaskNodeAlphaTo", Node=text_node, To=1.0, Time=self.fade_time, Interrupt=True)
            enter.addBlock()

            interrupt.addTask('TaskMovie2ButtonLeave', Movie2Button=button)

        source.addDelay(1)
        source.addTask("TaskNodeAlphaTo", Node=text_node, To=0.0, Time=self.fade_time, Interrupt=True)
        pass

    def _runTaskChains(self):
        def _goPreviousScene():
            PreviousSceneName = self.object.getParam("PreviousSceneName") or "Menu"
            TransitionManager.changeScene(PreviousSceneName)

        self.tc_back_button = TaskManager.createTaskChain()
        with self.tc_back_button as tc:
            tc.addTask('TaskMovie2ButtonClick', Movie2Button=self.back_button)
            tc.addFunction(_goPreviousScene)
            tc.addFunction(self.object.setParam, 'PreviousSceneName', None)

        for (button, text) in self.button_with_texts:
            tc_appear = TaskManager.createTaskChain(Repeat=True)

            self.tc_text_on_cursor.append(tc_appear)

            with tc_appear as tc:
                tc.addScope(self.__scopeTextAppear, button, text)

    def _onActivate(self):
        if self.back_button is None:
            return

        self._runTaskChains()

    def _onDeactivate(self):
        if self.tc_back_button is not None:
            self.tc_back_button.cancel()

        for tc_appear in self.tc_text_on_cursor:
            tc_appear.cancel()

        for (button, text) in self.button_with_texts:
            node = text.getEntityNode()
            node.removeFromParent()