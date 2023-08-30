from Foundation.Initializer import Initializer
from HOPA.ElementalMagicManager import ElementalMagicManager
from Foundation.ObjectManager import ObjectManager
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
            movie.setEnable(False)
            movie.setPlay(True)
            movie.setLoop(True)
            movie.setInteractive(False)

            node = movie.getEntityNode()
            self._slot.addChild(node)

            self.Movies[state] = movie

    def setState(self, state):
        if state not in self.Movies:
            return

        current_movie = self.Movies[self.state]
        current_movie.setEnable(False)

        self.Movies[state].setEnable(True)
        self.state = state

    def getCurrentMovie(self):
        if self.state is None:
            return None
        return self.Movies[self.state]

    def generateMagicEffects(self):
        states = {
            "Appear": self.params.state_Appear,
            "Idle": self.params.state_Idle,
            "Ready": self.params.state_Ready,
            "Release": self.params.state_Release,
        }
        group = GroupManager.getGroup(self.params.group_name)

        for state, prototype_name in states.items():
            movie_name = "Movie2_Element_%s" % state
            movie = ObjectManager.createObjectUnique(movie_name, prototype_name, group)
            yield state, movie
