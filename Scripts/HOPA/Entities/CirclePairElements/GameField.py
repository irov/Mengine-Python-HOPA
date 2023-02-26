from Foundation.TaskManager import TaskManager

class GameField(object):
    def __init__(self, sound):
        self.movieList = []
        self.isRotate = False
        self.sound = sound
        pass

    def addMovie(self, value):
        self.movieList.append(value)
        pass

    def Rotate(self):
        self.isRotate = True
        with TaskManager.createTaskChain(Name="CircleRotate", Cb=self.noRotate) as tc:
            tc.addTask("TaskMoviePlay", Movie=self.sound, Wait=False, Loop=False)
            with tc.addParallelTask(len(self.movieList)) as tcs:
                for tci, Movie in zip(tcs, self.movieList):
                    MovieEn = Movie.getEntity()
                    duration = Movie.getDuration()
                    current_timing = MovieEn.getTiming()
                    rewind_timing = duration / 4
                    set_time = current_timing + rewind_timing
                    if set_time >= duration:
                        tci.addTask("TaskFunction", Fn=MovieEn.setInterval, Args=(current_timing, duration))
                        tci.addTask("TaskMoviePlay", Movie=Movie, Wait=True)
                        tci.addTask("TaskFunction", Fn=MovieEn.setInterval, Args=(0, duration - 1))
                        tci.addTask("TaskFunction", Fn=MovieEn.setTiming, Args=(0,))
                        pass
                    else:
                        tci.addTask("TaskFunction", Fn=MovieEn.setInterval, Args=(current_timing, set_time))
                        tci.addTask("TaskMoviePlay", Movie=Movie, Wait=True)
                        tci.addTask("TaskFunction", Fn=MovieEn.setInterval, Args=(0, duration - 1))
                        tci.addTask("TaskFunction", Fn=MovieEn.setTiming, Args=(set_time,))
                        pass
                    pass
                pass
            pass
        pass

    def noRotate(self, isSkip):
        self.isRotate = False
        pass

    def restore(self, Save):
        for timing, Movie in zip(Save, self.movieList):
            MovieEn = Movie.getEntity()
            MovieEn.setTiming(timing)
            pass
        pass

    def makeSave(self):
        Save = []
        for Movie in self.movieList:
            MovieEn = Movie.getEntity()
            current_timing = MovieEn.getTiming()
            Save.append(current_timing)
            pass
        return Save
        pass
    pass