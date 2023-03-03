from Foundation.TaskManager import TaskManager


class SecretElement(object):
    def __init__(self, movie_secret, movie_classified):
        # movieObject instance
        self.movie_classified = movie_classified
        self.movie_secret = movie_secret
        self.classified = False
        self._onInitial()
        pass

    def __repr__(self):
        Name = self.movie_classified.getName()
        return "%s_with_%s" % (self.__class__.__name__, Name)
        pass

    def _onInitial(self):
        self.movie_classified.setPlay(False)
        self.movie_classified.setEnable(False)
        self.movie_secret.setEnable(True)
        pass

    def toClassified(self):
        self.classified = True
        self._switch()
        pass

    def toSecret(self):
        self.classified = False
        self._switch()
        pass

    def _switch(self):
        if self.classified is False:
            if TaskManager.existTaskChain(repr(self)):
                TaskManager.cancelTaskChain(repr(self))
                pass
            with TaskManager.createTaskChain(Name=repr(self)) as tc_play:
                tc_play.addTask("TaskEnable", Object=self.movie_classified)
                tc_play.addTask("TaskMoviePlay", Movie=self.movie_classified)
                tc_play.addTask("TaskEnable", Object=self.movie_classified, Value=False)
                tc_play.addTask("TaskEnable", Object=self.movie_secret)
                pass
            pass
        else:
            self.movie_classified.setEnable(True)
            self.movie_classified.setPlay(True)
            self.movie_secret.setEnable(False)
            pass
        pass

    def getClassified(self):
        return self.classified
