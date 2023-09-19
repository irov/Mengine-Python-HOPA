from Foundation.Initializer import Initializer
from Foundation.TaskManager import TaskManager
from Foundation.GuardBlockInput import GuardBlockInput
from HOPA.ChangeScreenOnClickManager import BoardCell
from HOPA.Entities.ChangeScreenOnClick.Direction import Direction


class Lever(object):
    def __init__(self):
        self.idle = None
        self.use = None
        self.done = None

    def onCreate(self, generator, name):
        self.idle = generator(name + "_Idle")
        self.use = generator(name + "_Use")
        self.done = generator(name + "_Done")

    def onDestroy(self):
        self.idle.onDestroy()
        self.idle = None
        self.use.onDestroy()
        self.use = None
        self.done.onDestroy()
        self.done = None

    def setEnable(self, value):
        self.idle.setEnable(value)
        self.use.setEnable(value)
        self.done.setEnable(value)


class GateHandler(Initializer):

    def __init__(self):
        super(GateHandler, self).__init__()
        self._owner = None
        self.tc = None
        self.Movies = {}        # {id: {GateOpen, GateClose, Lever}}
        self.States = {}        # {id: isOpen}
        self._active_gate = False

    def _onInitialize(self, owner):
        self._owner = owner

        GateCloseNames = self._owner.param.GateCloseNames
        GateOpenNames = self._owner.param.GateOpenNames
        LeverNames = self._owner.param.LeverNames

        for i, (open_name, close_name, lever_name) in enumerate(zip(GateOpenNames, GateCloseNames, LeverNames), 1):
            gate_open_movie = self._generate(open_name)
            gate_close_movie = self._generate(close_name)
            lever_movie = Lever()
            lever_movie.onCreate(self._generate, lever_name)

            gate_open_movie.setEnable(False)

            params = {
                "GateOpen": gate_open_movie,
                "GateClose": gate_close_movie,
                "Lever": lever_movie,
            }

            self.Movies[i] = params
            self.States[i] = False

    def onActivate(self):
        if len(self.States) == 0:
            return
        self.runTaskChain()

    def _onFinalize(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        for movies in self.Movies.values():
            for movie in movies.values():
                movie.onDestroy()
        self.Movies = {}
        self.States = {}

    # main

    def runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Name="ChangeScreenOnClickGateHandler")
        with self.tc as tc:
            for id_, parallel in tc.addParallelTaskList(self.Movies.keys()):
                parallel.addScope(self._scopeLever, id_)

    def _scopeLever(self, source, id_):
        lever = self.getMovie(id_, "Lever")

        def _replaceCurrentMovie():
            self._owner.Movies_actual.remove(lever.idle)
            self._owner.Movies_actual.append(lever.done)

        source.addTask("TaskMovie2SocketClick", Movie2=lever.idle, SocketName="socket")
        source.addPrint("Lever tc {} click...".format(id_))
        with GuardBlockInput(source) as tc_lever:
            with tc_lever.addParallelTask(2) as (parallel_1, parallel_2):
                parallel_1.addTask("AliasObjectAlphaTo", Time=100, Object=lever.idle, To=0.0)
                parallel_2.addTask("AliasObjectAlphaTo", Time=100, Object=lever.use, To=1.0)
                parallel_2.addTask("TaskMovie2Play", Movie2=lever.use, Wait=True)
            with tc_lever.addParallelTask(2) as (parallel_1, parallel_2):
                parallel_1.addTask("AliasObjectAlphaTo", Time=100, Object=lever.use, To=0.0)
                parallel_2.addTask("AliasObjectAlphaTo", Time=100, Object=lever.done, To=1.0)
            tc_lever.addFunction(_replaceCurrentMovie)
            tc_lever.addFunction(self.setOpen, id_)
        source.addPrint("Lever tc {} done!!!".format(id_))

    def getActualMovies(self, Cur_pos):
        movies = []

        bottom_cell = Cur_pos[2][1]     # actual cell on which player stays

        if bottom_cell.equalTo(BoardCell.Gate):
            id_ = bottom_cell.params["target"]
            if self.isOpen(id_) is True:
                gate = self.getMovie(id_, "GateOpen")
            else:
                gate = self.getMovie(id_, "GateClose")
                self._active_gate = True
            movies.append(gate)

        if bottom_cell.equalTo(BoardCell.Lever):
            id_ = bottom_cell.params["target"]
            lever_movie = self.getMovie(id_, "Lever")
            movies.append(lever_movie)

        return movies

    def isCellBlocked(self, cell):
        if cell.equalTo(BoardCell.Gate) is False:
            return False
        id_ = cell.params["target"]
        return self.isOpen(id_)

    def canGoUp(self, Cur_pos):
        return self.isCellBlocked(Cur_pos[2][1])

    def createScene(self):
        self._active_gate = False

        movies = []

        bottom_cell = self._owner.Cur_pos[2][1]     # actual cell on which player stays

        if bottom_cell.equalTo(BoardCell.Gate):
            id_ = bottom_cell.params["target"]
            if self.isOpen(id_) is True:
                gate = self.getMovie(id_, "GateOpen")
            else:
                gate = self.getMovie(id_, "GateClose")
                self._active_gate = True
            movies.append(gate)

        if bottom_cell.equalTo(BoardCell.Lever):
            id_ = bottom_cell.params["target"]
            lever = self.getMovie(id_, "Lever")

            if self.isOpen(id_) is True:
                lever_movie = lever.done
            else:
                lever_movie = lever.idle

            movies.append(lever_movie)

        self._owner.Movies_actual.extend(movies)

        if self._active_gate is True:
            self._owner.removeCurrentArrow(Direction.Up)

    # utils

    def _generate(self, name):
        movie = self._owner.object.generateObject(name, name)
        movie.setAlpha(0.0)
        return movie

    def getMovie(self, id_, key):
        movies = self.getMovies(id_)
        movie = movies[key]
        return movie

    def getMovies(self, id_):
        movies = self.Movies[id_]
        return movies

    def setOpen(self, id_):
        gate_open_movie = self.getMovie(id_, "GateOpen")
        gate_close_movie = self.getMovie(id_, "GateClose")

        gate_close_movie.setEnable(False)
        gate_open_movie.setEnable(True)

        self.States[id_] = True

    def isOpen(self, id_):
        return self.States[id_] is True
