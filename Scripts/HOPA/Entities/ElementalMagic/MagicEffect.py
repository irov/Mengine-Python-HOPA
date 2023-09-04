from Foundation.Initializer import Initializer
from HOPA.ElementalMagicManager import ElementalMagicManager
from Foundation.GroupManager import GroupManager


class MagicEffect(Initializer):
    
    def __init__(self):
        super(MagicEffect, self).__init__()
        self.element = None
        self.params = None
        self.Movies = {}
        self.state = None
        self._slot = None

    def _onInitialize(self, slot):
        self._slot = slot

    def _onFinalize(self):
        self._slot = None
        self.removeElement()

    def getElement(self):
        return self.element

    def removeElement(self):
        self.element = None
        for movie in self.Movies.values():
            movie.removeFromParent()
            movie.onDestroy()
        self.Movies = {}
        self.state = None

    def setElement(self, element):
        self.element = element
        self.params = ElementalMagicManager.getElementParams(element)

        for state, movie in self.generateMagicEffects():
            node = movie.getEntityNode()
            self._slot.addChild(node)

            self.Movies[state] = movie

    def setState(self, state):
        if state not in self.Movies:
            return

        if self.state is not None:
            current_movie = self.Movies[self.state]
            current_movie.setEnable(False)

        self.Movies[state].setEnable(True)
        self.state = state

        Trace.msg_dev("    Ring.MagicEffect: run state {}".format(self.state))

    def scopePlayCurrentState(self, source, **params):
        if self.getCurrentMovie() is None:
            return
        source.addTask("TaskMovie2Play", Movie2=self.getCurrentMovie(), **params)

    def getCurrentMovie(self):
        if self.state is None:
            return None
        return self.Movies[self.state]

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
