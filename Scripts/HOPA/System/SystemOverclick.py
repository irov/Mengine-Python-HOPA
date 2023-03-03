from Foundation.System import System
from Foundation.TaskManager import TaskManager


class SystemOverclick(System):
    def _onParams(self, params):
        super(SystemOverclick, self)._onParams(params)
        self.timeClick = []
        pass

    def _onRun(self):
        self.addObserver(Notificator.onOverclickHook, self._onOverclickHook)
        self.addObserver(Notificator.onHOGItemPicked, self._onHOGItemPicked)

        return True
        pass

    def _onOverclickHook(self):
        time = Mengine.getTime()
        self.timeClick.append(time)

        if self.__checkOverclick() is True:
            with TaskManager.createTaskChain(Name="Overclick", GroupName="Overclick") as tc:
                tc.addTask("TaskNotify", ID=Notificator.onOverClick)
                tc.addTask("TaskSceneLayerGroupEnable", LayerName="Overclick", Value=True)
                tc.addTask("TaskInteractive", ObjectName="Socket_Block", Value=True)

                tc.addTask("TaskMoviePlay", MovieName="Movie_Hypnotoad", Wait=True)
                # with tc.addParallelTask(2) as (tc1,tc2):
                #     tc1.addTask("TaskMoviePlay",  MovieName = "Movie_Hypnotoad", Wait = True)
                #     tc2.addTask("TaskSoundEffect", SoundName = "HypnoToad", Wait = True)
                #     pass

                tc.addTask("TaskInteractive", ObjectName="Socket_Block", Value=False)
                tc.addTask("TaskSceneLayerGroupEnable", LayerName="Overclick", Value=False)
                pass

            pass

        return False
        pass

    def _onHOGItemPicked(self):
        self.timeClick = []
        return False
        pass

    def __checkOverclick(self):
        if TaskManager.existTaskChain("Overclick"):
            return False
            pass

        if len(self.timeClick) < 6:
            return False

        currentTime = self.timeClick[-1]

        for time in self.timeClick[-1:-6:-1]:
            if currentTime - time < 2:
                continue
                pass

            return False
            pass

        return True
        pass

    def _onStop(self):
        pass

    pass
