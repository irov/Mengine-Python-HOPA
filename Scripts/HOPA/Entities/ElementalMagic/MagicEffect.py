from Foundation.Initializer import Initializer
from Foundation.GroupManager import GroupManager
from HOPA.ElementalMagicManager import ElementalMagicManager


class MagicEffect(Initializer):
    
    def __init__(self):
        super(MagicEffect, self).__init__()
        self.element = None
        self.params = None
        self.Movies = {}
        self.__state = None
        self._slot = None

        self.EventUpdateState = None
        self._releaseObserverId = None

    def _onInitialize(self, slot):
        self._slot = slot
        self.EventUpdateState = Event("onMagicEffectStateUpdate")

    def _onFinalize(self):
        self._slot = None
        if self._releaseObserverId is not None:
            self.EventUpdateState.removeObserver(self._releaseObserverId)
            self._releaseObserverId = None
        self.EventUpdateState = None
        self.removeElement()

    def getElement(self):
        return self.element

    def releaseElement(self):
        if self._releaseObserverId is not None:
            Trace.log("Entity", 1, "Already setup release observer")
            return

        if self.getState() == "Idle":
            self.removeElement()
            return

        def _cb(prev_state, new_state):
            if new_state == "Idle":
                self.removeElement()
                self.EventUpdateState.removeObserver(self._releaseObserverId)
                self._releaseObserverId = None
                return True
            return False

        self._releaseObserverId = self.EventUpdateState.addObserver(_cb)

    def removeElement(self):
        self.element = None
        self.params = None
        for movie in self.Movies.values():
            movie.removeFromParent()
            movie.onDestroy()
        self.Movies = {}
        self.__state = None

    def setElement(self, element):
        self.element = element
        self.params = ElementalMagicManager.getElementParams(element)

        for state, movie in self.generateMagicEffects():
            node = movie.getEntityNode()
            self._slot.addChild(node)

            self.Movies[state] = movie

    def getState(self):
        return self.__state

    def setState(self, state):
        if state not in self.Movies:
            return

        prev_state = self.__state

        if self.__state is not None:
            current_movie = self.Movies[self.__state]
            current_movie.setEnable(False)

        self.Movies[state].setEnable(True)
        self.__state = state

        self.EventUpdateState(prev_state, state)

        Trace.msg_dev("    Ring.MagicEffect: run state {}".format(self.__state))

    def scopePlayCurrentState(self, source, **params):
        if self.getCurrentMovie() is None:
            return
        source.addTask("TaskMovie2Play", Movie2=self.getCurrentMovie(), **params)

    def getCurrentMovie(self):
        if self.__state is None:
            return None
        return self.Movies[self.__state]

    def generateMagicEffects(self):
        states = {
            "Appear": [self.params.state_Appear, True, False],
            "Idle": [self.params.state_Idle, True, True],
            "Ready": [self.params.state_Ready, True, True],
            "Release": [self.params.state_Release, True, False],
        }
        group = GroupManager.getGroup(self.params.group_name)

        for state, (prototype_name, play, loop) in states.items():
            movie_name = "Movie2_Element_%s" % state

            movie = group.generateObjectUnique(movie_name, prototype_name,
                Enable=False, Play=play, Loop=loop, Interactive=False)

            yield state, movie
