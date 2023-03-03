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
                guard_tc.addTask("TaskEnable", Object=self.movie_open)
                guard_tc.addTask("TaskEnable", Object=self.movie_close, Value=False)

                guard_tc.addTask("TaskFunction", Fn=self.setBlocked, Args=(True,))
                guard_tc.addTask("TaskMoviePlay", Movie=self.movie_open, Loop=False, Wait=True)
                guard_tc.addTask("TaskFunction", Fn=self.setOpen, Args=(True,))
                if bufferElement is None:
                    guard_tc.addTask("TaskFunction", Fn=self.setBlocked, Args=(False,))
                    pass
                elif self.name == bufferElement.name:
                    guard_tc.addTask("TaskFunction", Fn=self.onActive)
                    guard_tc.addTask("TaskFunction", Fn=bufferElement.onActive)
                    pass
                else:
                    guard_tc.addTask("TaskFunction", Fn=self.onClose)
                    guard_tc.addTask("TaskFunction", Fn=bufferElement.onClose)
                    pass
                pass
            pass

        return
        pass

    def onClose(self):
        with TaskManager.createTaskChain() as tc:
            tc.addTask("TaskFunction", Fn=self.setBlocked, Args=(True,))
            tc.addTask("TaskEnable", Object=self.movie_close)
            tc.addTask("TaskEnable", Object=self.movie_open, Value=False)
            tc.addTask("TaskEnable", Object=self.movie_active, Value=False)
            tc.addTask("TaskMoviePlay", Movie=self.movie_close, Loop=False, Wait=True)
            tc.addTask("TaskFunction", Fn=self.setOpen, Args=(False,))
            tc.addTask("TaskFunction", Fn=self.setBlocked, Args=(False,))
            pass
        return
        pass

    def onActive(self):
        with TaskManager.createTaskChain() as tc:
            tc.addTask("TaskFunction", Fn=self.setBlocked, Args=(True,))
            tc.addTask("TaskEnable", Object=self.movie_active)
            tc.addTask("TaskEnable", Object=self.movie_open, Value=False)
            tc.addTask("TaskEnable", Object=self.movie_close, Value=False)
            tc.addTask("TaskMoviePlay", Movie=self.movie_active, Loop=True, Wait=False)
            tc.addTask("TaskFunction", Fn=self.setActive, Args=(True,))
            tc.addTask("TaskNotify", ID=Notificator.onAssociationElementActive)
            pass
        return
