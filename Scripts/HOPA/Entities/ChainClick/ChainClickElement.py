from Foundation.TaskManager import TaskManager
from Functor import Functor

class ChainClickElement(object):
    def __init__(self, item, itemClick, movieComplete):
        self.chainId = None
        self.item = item
        self.item.setParam("Enable", True)

        self.itemClick = itemClick
        self.itemClick.setParam("Enable", False)

        self.movieComplete = movieComplete
        self.movieComplete.setParam("Enable", False)
        self.item.addObject(self.movieComplete)
        self.active = False
        self.onItemClickObserver = None
        self.onItemMouseEnterObserver = None
        self.onItemMouseLeaveObserver = None
        pass

    def initialize(self, callback):
        self.__removeObservers()
        self.item.setInteractive(True)
        self.onItemClickObserver = Notification.addObserver(Notificator.onItemClick, Functor(self._onItemClick, self.item, callback))
        self.onItemMouseEnterObserver = Notification.addObserver(Notificator.onItemMouseEnter, Functor(self._onItemMouseEnter, self.item))
        self.onItemMouseLeaveObserver = Notification.addObserver(Notificator.onItemMouseLeave, Functor(self._onItemMouseLeave, self.item))
        pass

    def setChain(self, chainId):
        self.chainId = chainId
        pass

    def getChain(self):
        return self.chainId
        pass

    def setActive(self, value):
        if self.active == value:
            return
            pass

        self.active = value
        self.updateActive()
        pass

    def updateActive(self):
        if self.active is True:
            if self.itemClick.getParam("Enable") is True:
                return
                pass

            self.itemClick.setParam("Enable", True)
        else:
            if self.itemClick.getParam("Enable") is False:
                return
                pass

            self.itemClick.setParam("Enable", False)
            pass
        pass

    def getActive(self):
        return self.active
        pass

    def complete(self):
        taskName = "%s_PLAY" % (self.item.getName())
        if TaskManager.existTaskChain(taskName) is True:
            TaskManager.cancelTaskChain(taskName)
            pass

        group = self.movieComplete.getGroup()
        movieName = self.movieComplete.getName()

        with TaskManager.createTaskChain(Name=taskName, Group=group) as tc:
            tc.addEnable(movieName)
            tc.addTask("TaskMoviePlay", MovieName=movieName)
            tc.addFunction(self.__onComplete)
            pass
        pass

    def finalize(self):
        if self.item is None:
            return

        taskName = "%s_PLAY" % (self.item.getName())
        TaskManager.cancelTaskChain(taskName, exist=False)
        self.__onComplete()

    def __removeObservers(self):
        Notification.removeObserver(self.onItemClickObserver)
        Notification.removeObserver(self.onItemMouseEnterObserver)
        Notification.removeObserver(self.onItemMouseLeaveObserver)
        self.onItemClickObserver = None
        self.onItemMouseEnterObserver = None
        self.onItemMouseLeaveObserver = None

    def __onComplete(self):
        movie = self.movieComplete
        if movie is None:
            return

        self.movieComplete = None
        item = self.item
        self.item = None
        item_click = self.itemClick
        self.itemClick = None
        self.chainId = None
        self.active = False

        self.__removeObservers()

        if movie.isDestroy() is False:
            movie.onDestroy()
        item.setParam("Enable", False)
        item_click.setParam("Enable", False)

    def _onItemClick(self, item, x, y, wait, callback):
        if item is not wait:
            return False
            pass

        callback(self)
        return False
        pass

    def _onItemMouseEnter(self, item, wait):
        if item is not wait:
            return False
            pass

        if self.itemClick.getParam("Enable") is True:
            return False
            pass

        self.itemClick.setParam("Enable", True)
        return False
        pass

    def _onItemMouseLeave(self, item, wait):
        if item is not wait:
            return False
            pass

        if self.itemClick.getParam("Enable") is False:
            return False
            pass

        if self.active is True:
            return False
            pass

        self.itemClick.setParam("Enable", False)
        return False
