from Foundation.Initializer import Initializer
from Foundation.TaskManager import TaskManager


class Symbol(Initializer):

    def _onInitialize(self, name, movie_backplate, movie_mouseover, movie_open, movie_activate, movie_close, movie_sound):
        super(Symbol, self)._onInitialize(name, movie_backplate, movie_mouseover, movie_open, movie_activate, movie_close, movie_sound)

        self.name = name
        self.movie_backplate = movie_backplate
        self.movie_mouseover = movie_mouseover
        self.movie_open = movie_open
        self.movie_activate = movie_activate
        self.movie_close = movie_close
        self.movie_sound = movie_sound

        self.isOpen = False
        self.blocked = False

        self.movie_open.setEnable(False)
        self.movie_activate.setEnable(False)
        self.movie_close.setEnable(False)
        self.movie_backplate.setEnable(True)
        self.movie_mouseover.setEnable(False)
        pass

    def closeSymbol(self):
        self.isOpen = False
        self.activateSymbol()

    def openSymbol(self):
        self.isOpen = True
        self.activateSymbol()

    def activateSymbol(self):
        with TaskManager.createTaskChain() as tc:
            if self.isOpen is False:
                tc.addEnable(self.movie_close)
                tc.addTask("TaskMoviePlay", Movie=self.movie_close, Wait=True)
                tc.addDisable(self.movie_close)
                tc.addDisable(self.movie_activate)
                tc.addDisable(self.movie_open)
                tc.addEnable(self.movie_backplate)
                tc.addFunction(self.mouseOff)
            else:
                if self.movie_sound is not None:
                    tc.addTask("TaskMoviePlay", Movie=self.movie_sound, Wait=False, Loop=False)
                tc.addDisable(self.movie_backplate)
                tc.addEnable(self.movie_activate)
                tc.addTask("TaskMoviePlay", Movie=self.movie_activate, Wait=True)
                tc.addDisable(self.movie_activate)
                tc.addEnable(self.movie_open)
                tc.addEnable(self.movie_mouseover)

    def mouseOn(self):
        self.movie_mouseover.setEnable(True)

    def mouseOff(self):
        self.movie_mouseover.setEnable(False)

    def getIsOpen(self):
        return self.isOpen

    def restore(self):
        self.movie_backplate.setEnable(False)
        self.movie_mouseover.setEnable(True)
        self.movie_open.setEnable(True)
        self.isOpen = True
        self.blocked = True
