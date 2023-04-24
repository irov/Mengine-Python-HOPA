from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager
from Foundation.Utils import isCollectorEdition


class BonusManager(Manager):
    s_states = {}
    s_states_default_status = {}
    s_transitions = {}

    class State:
        def __init__(self, state_id, button_name, demon_name, status):
            self.state_id = state_id
            self.button_name = button_name
            self.demon_name = demon_name
            self.status = status

    class Transition:
        def __init__(self, transition_button, scene_to):
            self.transition_button = transition_button
            self.scene_to = scene_to

    @staticmethod
    def loadParams(module, param):
        if isCollectorEdition() is False:
            return True

        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            state_id = record.get("StateID")
            button_name = record.get("ButtonName")
            demon_name = record.get("DemonName")
            status = record.get("Status")

            transition_button = record.get("TransitionButton")
            scene_to = record.get("SceneTo")

            if state_id is not None:
                status = bool(int(status))

                BonusManager.s_states[state_id] = BonusManager.State(state_id, button_name, demon_name, status)
                BonusManager.s_states_default_status[state_id] = status

            if transition_button is not None:
                if scene_to == "Guide" and Mengine.getGameParamBool("Guides", True) is False:
                    continue

                BonusManager.s_transitions[scene_to] = BonusManager.Transition(transition_button, scene_to)

        return True

    @staticmethod
    def getStates():
        return BonusManager.s_states

    @staticmethod
    def getStatesDefaultStatus():
        return BonusManager.s_states_default_status

    @staticmethod
    def getState(state_id):
        state = BonusManager.s_states.get(state_id, None)
        if state is None:
            Trace.log('Manager', 0, 'State {} is not exist'.format(state_id))

        return state

    @staticmethod
    def getTransitions():
        return BonusManager.s_transitions
