from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.TaskManager import TaskManager


class Element(object):
    def __init__(self, name, movie_open, movie_active, movie_close):
        # movieObject instance
        self.name = name
        self.movie_open = movie_open
        self.movie_close = movie_close
        self.movie_active = movie_active
        self.isOpen = False
        self.isActive = False
        self.isBlocked = False
        pass

    def onPrepare(self):
        self.movie_active.setEnable(False)
        self.movie_close.setEnable(False)
        self.movie_open.setEnable(True)
        pass

    def setBlocked(self, value):
        self.isBlocked = value
        pass

    def getBlocked(self):
        return self.isBlocked
        pass

    def setOpen(self, value):
        self.isOpen = value
        pass

    def getOpen(self):
        return self.isOpen
        pass

    def setActive(self, value):
        self.isActive = value
        pass

    def getActive(self):
        return self.isActive
        pass

    def onOpen(self, bufferElement=None):
        with TaskManager.createTaskChain() as tc:
            with GuardBlockInput(tc) as guard_tc:
                guard_tc.addEnable(self.movie_open)
                guard_tc.addDisable(self.movie_close)

                guard_tc.addFunction(self.setBlocked, True)
                guard_tc.addTask("TaskMoviePlay", Movie=self.movie_open, Loop=False, Wait=True)
                guard_tc.addFunction(self.setOpen, True)
                if bufferElement is None:
                    guard_tc.addFunction(self.setBlocked, False)
                    pass
                elif self.name == bufferElement.name:
                    guard_tc.addFunction(self.onActive)
                    guard_tc.addFunction(bufferElement.onActive)
                    pass
                else:
                    guard_tc.addFunction(self.onClose)
                    guard_tc.addFunction(bufferElement.onClose)
                    pass
                pass
            pass

        return
        pass

    def onClose(self):
        with TaskManager.createTaskChain() as tc:
            tc.addFunction(self.setBlocked, True)
            tc.addEnable(self.movie_close)
            tc.addDisable(self.movie_open)
            tc.addDisable(self.movie_active)
            tc.addTask("TaskMoviePlay", Movie=self.movie_close, Loop=False, Wait=True)
            tc.addFunction(self.setOpen, False)
            tc.addFunction(self.setBlocked, False)
            pass
        return
        pass

    def onActive(self):
        with TaskManager.createTaskChain() as tc:
            tc.addFunction(self.setBlocked, True)
            tc.addEnable(self.movie_active)
            tc.addDisable(self.movie_open)
            tc.addDisable(self.movie_close)
            tc.addTask("TaskMoviePlay", Movie=self.movie_active, Loop=True, Wait=False)
            tc.addFunction(self.setActive, True)
            tc.addNotify(Notificator.onAssociationElementActive)
            pass
        return
