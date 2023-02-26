from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from HOPA.MagicGloveManager import MagicGloveManager

class MagicGlove(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "Point")
        Type.addActionActivate(Type, "Runes", Append=Type.__appendRune, Remove=Type.__delRune)
        Type.addAction(Type, "State", Update=Type.__updateState)

    def __appendRune(self, key, value):
        Notification.notify(Notificator.onRuneListChanges)

    def __delRune(self, index, value, old):
        pass

    def __updateState(self, state):
        if state == 'Light':
            Notification.notify(Notificator.onShowMindByID, self.minds["chargedRune"])

        current_state_button = self.getCurrentStateButton()
        new_state_button = self.movie_buttons.get(state, None)

        if current_state_button is None or new_state_button is None:
            return
        current_state_button.setEnable(False)
        new_state_button.setEnable(True)

        self.setCurrentStateButton(new_state_button)

    def __init__(self):
        super(MagicGlove, self).__init__()
        self.movie_buttons = {}
        self.current_state_button = None
        self.callbacks = {"Idle": self.__cb_scope_idle, "Ready": self.__cb_scope_ready, "Light": self.__cb_scope_light, }
        self.minds = {"noRunes": "ID_MIND_GloveEmpty", "hasRunes": "ID_MIND_GloveWithSpells", "wrongRune": "ID_MIND_GloveWrongSpell", "chargedRune": "ID_MIND_MagicGlove_IsReady"}

    def __cb_scope_idle(self, source):
        # source.addPrint('__cb_scope_idle')

        Notification.notify(Notificator.onShowMindByID, self.minds["noRunes"])

    def __cb_scope_ready(self, source):
        # source.addPrint('__cb_scope_ready')

        quest = self.object.getActiveUseRuneQuest()
        if quest:
            if quest.params['Rune_ID'] not in self.Runes:
                Notification.notify(Notificator.onShowMindByID, self.minds["wrongRune"])
                return

        Notification.notify(Notificator.onShowMindByID, self.minds["hasRunes"])

    def __cb_scope_light(self, source):
        # source.addPrint('__cb_scope_light')

        quest = self.object.getActiveUseRuneQuest()
        if quest is None:
            return
        rune_id = quest.params['Rune_ID']
        object_ = quest.params['Object']

        source.addNotify(Notificator.onStartUseRune, rune_id, object_)
        source.addFunction(self.object.delParam, "Runes", rune_id)
        source.addFunction(self._change_state)

    def _change_state(self):
        active_use_rune_quest = self.object.getActiveUseRuneQuest()

        if len(self.object.getParam("Runes")) == 0:
            self.object.setParam("State", "Idle")
            return False
        elif active_use_rune_quest is not None:
            self.object.setParam("State", "Light")
            return False
        self.object.setParam("State", "Ready")
        return False

    def setCurrentStateButton(self, button):
        self.current_state_button = button

    def getCurrentStateButton(self):
        return self.current_state_button

    def _onPreparation(self):
        movie_button_names = MagicGloveManager.getButtonNames()
        for state, movie_button_name in movie_button_names.iteritems():
            button = self.object.getObject(movie_button_name)
            button.setEnable(False)

            if self.State == state:
                button.setEnable(True)
                self.current_state_button = button
            self.movie_buttons[state] = button

    def _onActivate(self):
        self._runTaskChain()

    def _onDeactivate(self):
        self._cleanUp()
        pass

    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

    def _runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)

        with self.tc as tc:
            for (state_name, button), source in tc.addRaceTaskList(self.movie_buttons.iteritems()):
                source.addTask("TaskMovie2ButtonClick", Movie2Button=button)
                source.addScope(self.callbacks.get(state_name))
            tc.addNotify(Notificator.onMagicGloveClick)