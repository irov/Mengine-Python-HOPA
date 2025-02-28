from Foundation.System import System
from Foundation.TaskManager import TaskManager
from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager


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

        group_name = "Overclick"
        socket_block = "Socket_Block"
        movie_name = DefaultManager.getDefault("OverclickMovie", "Movie_Hypnotoad")

        if GroupManager.hasObject(group_name, movie_name):
            movie = GroupManager.getObject(group_name, movie_name)
            movie_type = movie.getType()
        else:
            Trace.msg_err("Group {!r} doesn't have object with name {!r}!".format(group_name, movie_name))
            movie_name = "Movie_Hypnotoad"
            movie_type = "ObjectMovie"

        if self.__checkOverclick() is True:
            with TaskManager.createTaskChain(Name="Overclick", GroupName=group_name) as tc:
                tc.addNotify(Notificator.onOverClick)
                tc.addTask("TaskSceneLayerGroupEnable", LayerName=group_name, Value=True)
                tc.addTask("TaskInteractive", ObjectName=socket_block, Value=True)

                if movie_type == "ObjectMovie":
                    tc.addTask("TaskMoviePlay", MovieName=movie_name, Wait=True)
                elif movie_type == "ObjectMovie2":
                    tc.addTask("TaskMovie2Play", Movie2Name=movie_name, Wait=True)

                # with tc.addParallelTask(2) as (tc1,tc2):
                #     tc1.addTask("TaskMoviePlay",  MovieName = "Movie_Hypnotoad", Wait = True)
                #     tc2.addTask("TaskSoundEffect", SoundName = "HypnoToad", Wait = True)
                #     pass

                tc.addTask("TaskInteractive", ObjectName=socket_block, Value=False)
                tc.addTask("TaskSceneLayerGroupEnable", LayerName=group_name, Value=False)
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
