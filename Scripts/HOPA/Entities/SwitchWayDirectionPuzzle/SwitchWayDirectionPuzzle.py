from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.SwitchWayDirectionPuzzleManager import SwitchWayDirectionPuzzleManager

Enigma = Mengine.importEntity("Enigma")

class SwitchWayDirectionPuzzle(Enigma):
    class Slot(object):
        def __init__(self, id, socket, winSubMovie, winCount, movieMain):
            self.id = id
            self.socket = socket
            self.winSubMovie = winSubMovie
            self.winCount = winCount
            self.movieMain = movieMain

        def scopeClick(self, source):
            source.addTask('TaskNodeSocketClick', Socket=self.socket)  # source.addPrint(' click on slot {} '.format(self.id))

        def scopeClickDown(self, source):
            source.addTask("TaskMovie2SocketClick", Movie2=self.movieMain, SocketName="socket_{}".format(self.id), isDown=True)
            # source.addPrint(" click down on slot {}".format(self.id))
            source.addFunction(self.movieMain.delParam, 'DisableLayers', 'Sprite_Number_{}_Scale'.format(self.id))
            source.addFunction(self.movieMain.appendParam, 'DisableLayers', 'Sprite_Number_{}'.format(self.id))

        def scopeClickUp(self, source):
            source.addTask("TaskMouseButtonClick", isDown=False)
            source.addFunction(self.movieMain.delParam, 'DisableLayers', 'Sprite_Number_{}'.format(self.id))
            source.addFunction(self.movieMain.appendParam, 'DisableLayers', 'Sprite_Number_{}_Scale'.format(self.id))

        def scopeUpdateWin(self, source, movie, win):
            source.addFunction(movie.appendParam, 'DisableSubMovies', self.winSubMovie)
            source.addFunction(movie.delParam, 'DisableSubMovies', self.winSubMovie)
            if win is False:
                source.addFunction(movie.appendParam, 'DisableSubMovies', self.winSubMovie)
                pass
            else:
                source.addTask('TaskSubMovie2Play', Movie2=movie, SubMovie2Name=self.winSubMovie, Loop=True, Wait=False)
            pass

    class Way(object):
        def __init__(self, fromID, toID, submovieName, state):
            self.fromID = fromID
            self.toID = toID
            self.submovieName = submovieName
            self.state = state

        def scopeChangeState(self, source, movie):
            movie.entity.movie.getSubComposition(self.submovieName).setEnable(self.state)

            if self.state is True:
                source.addTask('TaskSubMovie2Play', Movie2=movie, SubMovie2Name=self.submovieName)

            self.state = not self.state

    class WayFinder(object):
        def __init__(self, ways):
            self.ways = ways

        def getWaysForSlot(self, slotID):
            result = []
            for way in self.ways:
                if way.fromID == slotID or way.toID == slotID:
                    result.append(way)
            return result

    def __init__(self):
        super(SwitchWayDirectionPuzzle, self).__init__()
        self.param = None

        self.slots = {}
        self.wayFinder = None

    def _onPreparation(self):
        super(SwitchWayDirectionPuzzle, self)._onPreparation()
        self.Prepare()

    def Prepare(self):
        self.loadParam()
        self.disableScaleMovies()
        self.setup()

    def disableScaleMovies(self):
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        self.movie_main = GroupManager.getObject(GroupName, self.param.MovieMain)
        if self.param.scaledSprites is not None:
            for spriteName in self.param.scaledSprites:
                self.movie_main.appendParam('DisableLayers', spriteName)

    def loadParam(self):
        self.param = SwitchWayDirectionPuzzleManager.getParam(self.EnigmaName)

    def setup(self):
        group_name = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        self.movie_main = GroupManager.getObject(group_name, self.param.MovieMain)

        slot_dict = self.param.SlotsDict
        for slotID in slot_dict:
            socket_name, sub_movie_win, win_count = slot_dict[slotID]
            socket = self.movie_main.getSocket(socket_name)
            slot = SwitchWayDirectionPuzzle.Slot(slotID, socket, sub_movie_win, win_count, self.movie_main)
            self.slots[slotID] = slot

        graph_dict = self.param.GraphDict
        ways = []
        for graphID in graph_dict:
            FromSlotID, ToSlotID = graphID
            SubMoviePath, StartState = graph_dict[graphID]

            sub_composition = self.movie_main.entity.movie.getSubComposition(SubMoviePath)
            sub_composition.getAnimation().stop()
            sub_composition.getAnimation().setFirstFrame()
            sub_composition.setEnable(StartState)

            way = SwitchWayDirectionPuzzle.Way(FromSlotID, ToSlotID, SubMoviePath, StartState)
            ways.append(way)

        self.wayFinder = SwitchWayDirectionPuzzle.WayFinder(ways)
        pass

    def _playEnigma(self):
        super(SwitchWayDirectionPuzzle, self)._playEnigma()

        self._runtaskChain()

    def _runtaskChain(self):
        ClickHolder = Holder()

        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self.scopeCheckWin)
            for slotID, tcRace in tc.addRaceTaskList(self.slots):
                # tcRace.addPrint(" click race on slot {}".format(slotID))
                tcRace.addScope(self.slots[slotID].scopeClickDown)
                tcRace.addNotify(Notificator.onSoundEffectOnObject, self.object, "SwitchWayDirectionPuzzle_PressOnNumber")
                tcRace.addScope(self.slots[slotID].scopeClickUp)
                # tcRace.addScope(self.slots[slotID].scopeClick)
                tcRace.addFunction(ClickHolder.set, slotID)
            tc.addScope(self.scopeResolveClick, ClickHolder)

    def _resetEnigma(self):
        self._cleanUp()
        self.Prepare()
        self._runtaskChain()

    def _restoreEnigma(self):
        super(SwitchWayDirectionPuzzle, self)._restoreEnigma()
        self._playEnigma()

    def scopeResolveClick(self, source, clickHolder):
        slotID = clickHolder.get()

        ways = self.wayFinder.getWaysForSlot(slotID)
        for way, tcParallel in source.addParallelTaskList(ways):
            tcParallel.addScope(way.scopeChangeState, self.movie_main)

    def scopeCheckWin(self, source):
        isWin = True

        for slotID in self.slots:
            slot = self.slots[slotID]
            ways = self.wayFinder.getWaysForSlot(slotID)
            count = 0
            for way in ways:
                if way.fromID == slotID and way.state is True:
                    count += 1
            win = slot.winCount == count
            source.addScope(slot.scopeUpdateWin, self.movie_main, win)
            if win is False:
                isWin = False

        if isWin is True:
            source.addFunction(self.enigmaComplete)

    def _onDeactivate(self):
        super(SwitchWayDirectionPuzzle, self)._onDeactivate()
        self._cleanUp()

    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
        self.tc = None

        self.slots = {}
        self.wayFinder = None