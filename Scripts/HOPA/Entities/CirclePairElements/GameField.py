from Foundation.TaskManager import TaskManager


class GameField(object):
    def __init__(self, sound):
        self.movieList = []
        self.isRotate = False
        self.sound = sound

    def addMovie(self, value):
        self.movieList.append(value)

    def Rotate(self):
        self.isRotate = True

        with TaskManager.createTaskChain(Name="CircleRotate", Cb=self.noRotate) as tc:
            tc.addTask("TaskMoviePlay", Movie=self.sound, Wait=False, Loop=False)
            with tc.addParallelTask(len(self.movieList)) as tcs:
                for tci, Movie in zip(tcs, self.movieList):
                    tci.addScope(self._scopeRotateMovie, Movie)

    def _scopeRotateMovie(self, source, Movie):
        MovieEn = Movie.getEntity()
        duration = Movie.getDuration()
        current_timing = MovieEn.getTiming()
        rewind_timing = duration / 4
        set_time = current_timing + rewind_timing

        if set_time >= duration:
            source.addTask("TaskFunction", Fn=MovieEn.setInterval, Args=(current_timing, duration))
            source.addTask("TaskMoviePlay", Movie=Movie, Wait=True)
            source.addTask("TaskFunction", Fn=MovieEn.setInterval, Args=(0, duration - 1))
            source.addTask("TaskFunction", Fn=MovieEn.setTiming, Args=(0,))
        else:
            source.addTask("TaskFunction", Fn=MovieEn.setInterval, Args=(current_timing, set_time))
            source.addTask("TaskMoviePlay", Movie=Movie, Wait=True)
            source.addTask("TaskFunction", Fn=MovieEn.setInterval, Args=(0, duration - 1))
            source.addTask("TaskFunction", Fn=MovieEn.setTiming, Args=(set_time,))

    def noRotate(self, isSkip):
        self.isRotate = False

    def restore(self, Save):
        for timing, Movie in zip(Save, self.movieList):
            MovieEn = Movie.getEntity()
            MovieEn.setTiming(timing)

    def makeSave(self):
        Save = []
        for Movie in self.movieList:
            MovieEn = Movie.getEntity()
            current_timing = MovieEn.getTiming()
            Save.append(current_timing)
        return Save
