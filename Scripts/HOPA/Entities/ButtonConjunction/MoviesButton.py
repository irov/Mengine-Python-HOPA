from Foundation.TaskManager import TaskManager


class MoviesButton(object):

    def __init__(self, movie_active, movie_down, movie_over):
        self.movie_active = movie_active
        self.movie_down = movie_down
        self.movie_over = movie_over
        self.state = movie_active
        self._initialize()
        pass

    def _initialize(self):
        self.movie_down.setEnable(False)
        self.movie_over.setEnable(False)
        self.movie_active.setEnable(True)
        self.movie_active.setPlay(True)

        pass

    def getMovieOver(self):
        return self.movie_over

    def push(self, cbBoundMethod):
        activate_name = self.movie_active.getName()
        Name = "%s_%s" % (self.__class__.__name__, activate_name)
        if TaskManager.existTaskChain(Name):
            return

        self.movie_over.setEnable(False)
        self.movie_active.setEnable(False)

        with TaskManager.createTaskChain(Name=Name) as tc:
            tc.addEnable(self.movie_down)
            tc.addTask("TaskMoviePlay", Movie=self.movie_down)
            tc.addFunction(cbBoundMethod, True)

    def reset(self):
        self.state = self.movie_active
        self._initialize()
