from Foundation.Initializer import Initializer
from HOPA.ElementalMagicManager import ElementalMagicManager
from Foundation.ObjectManager import ObjectManager
from Foundation.GroupManager import GroupManager


def generateMagicEffects(element):
    group = GroupManager.getGroup("ElementalMagic")
    states = ElementalMagicManager.getMagicElementStates(element)

    for state, prototype_name in states.items():
        movie_name = "Movie2_Element_%s" % state
        movie = ObjectManager.createObjectUnique(movie_name, prototype_name, group)
        yield state, movie


class MagicEffect(Initializer):
    
    def __init__(self):
        super(MagicEffect, self).__init__()
        self.element = None
        self.Movies = {}
        self.state = None
        self._slot = None

    def _onInitialize(self, slot):
        self._slot = slot

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

        for state, movie in generateMagicEffects(element):
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

    def _onFinalize(self):
        self._slot = None
        self.removeElement()
