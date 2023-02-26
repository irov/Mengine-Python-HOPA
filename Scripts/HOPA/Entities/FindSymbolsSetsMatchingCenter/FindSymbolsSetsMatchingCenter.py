from Foundation.TaskManager import TaskManager
from HOPA.FindSymbolsSetsMatchingCenterManager import FindSymbolsSetsMatchingCenterManager
from Holder import Holder

Enigma = Mengine.importEntity("Enigma")

class Symbol(object):
    def __init__(self, movie_idle, movie_select):
        movie_idle.setEnable(True)
        movie_select.setEnable(False)

        self.movie_idle = movie_idle
        self.movie_select = movie_select

        self.selected = False

        self.__tc_idle_play = None

    def setSelected(self, selected):
        self.selected = selected
        self.movie_select.setEnable(selected)
        self.movie_idle.setEnable(not selected)

    def enableIdlePlayTC(self):
        self.__tc_idle_play = TaskManager.createTaskChain(Repeat=True)
        with self.__tc_idle_play as tc:
            with tc.addIfTask(self.movie_idle.getEnable) as (_, false):
                false.addBlock()

            tc.addTask("TaskMovie2SocketEnter", Movie2=self.movie_idle, SocketName='socket')
            tc.addPlay(self.movie_idle, Wait=True)

    def scopeSelect(self, source):
        source.addTask("TaskMovie2SocketClick", Movie2=self.movie_idle, SocketName='socket')
        source.addFunction(self.setSelected, True)
        source.addPlay(self.movie_select, Wait=False, Loop=True)

    def disableIdlePlayTC(self):
        if self.__tc_idle_play is not None:
            self.__tc_idle_play.cancel()

    def cleanUp(self):
        self.disableIdlePlayTC()

class SymbolSet(object):
    MOVIE2_SET_COMPLETE = None
    MOVIE2_SET_FAIL = None
    MOVIE2_WIN = None

    def __init__(self, order, movie_center, symbols):
        self.order = order
        self.movie_center = movie_center
        self.symbols = symbols

        self.movie_center.setEnable(False)
        self.complete = None

    def setComplete(self, complete):
        if self.complete != complete:
            self.complete = complete
            self.movie_center.setEnable(not complete)
            self.movie_center.setPlay(not complete)
            self.movie_center.setLoop(not complete)

    @classmethod
    def scopePlaySetComplete(cls, source):
        source.addPlay(cls.MOVIE2_SET_COMPLETE, AutoEnable=True)

    @classmethod
    def scopePlaySetFail(cls, source):
        source.addPlay(cls.MOVIE2_SET_FAIL, AutoEnable=True)

    @classmethod
    def scopePlayWin(cls, source):
        source.addPlay(cls.MOVIE2_WIN, AutoEnable=True)

class FindSymbolsSetsMatchingCenter(Enigma):
    def __init__(self):
        super(FindSymbolsSetsMatchingCenter, self).__init__()
        self.tc_main = None

        self.params = None

        self.symbols = list()
        self.symbol_sets_sorted = list()

    # -------------- Preparation ---------------------------------------------------------------------------------------
    def loadParam(self):
        self.params = FindSymbolsSetsMatchingCenterManager.getParam(self.EnigmaName)

    def setup(self):
        SymbolSet.MOVIE2_WIN = self.object.getObject(self.params.movie_win)
        SymbolSet.MOVIE2_WIN.setEnable(False)

        SymbolSet.MOVIE2_SET_COMPLETE = self.object.getObject(self.params.movie_set_complete)
        SymbolSet.MOVIE2_SET_COMPLETE.setEnable(False)

        SymbolSet.MOVIE2_SET_FAIL = self.object.getObject(self.params.movie_set_fail)
        SymbolSet.MOVIE2_SET_FAIL.setEnable(False)

        for movie_center, (set_order_index, symbol_param_list) in self.params.symbols.items():
            movie_center = self.object.getObject(movie_center)

            symbols = []

            for movie_symbol_idle, movie_symbol_select in symbol_param_list:
                movie_idle = self.object.getObject(movie_symbol_idle)
                movie_select = self.object.getObject(movie_symbol_select)

                symbol = Symbol(movie_idle, movie_select)

                symbols.append(symbol)
                self.symbols.append(symbol)

            symbol_set = SymbolSet(set_order_index, movie_center, symbols)
            self.symbol_sets_sorted.append(symbol_set)

        self.symbol_sets_sorted.sort(key=lambda obj_: obj_.order)

    def cleanUp(self):
        if self.tc_main is not None:
            self.tc_main.cancel()
        self.tc_main = None

        for symbol in self.symbols:
            symbol.cleanUp()
        self.symbols = []

        self.symbol_sets_sorted = []

    # -------------- Run Task Chain ------------------------------------------------------------------------------------
    def runTaskChains(self):
        current_symbol_set_holder = Holder()

        def updateCurrentSymbolSet():
            for symbol_set_ in self.symbol_sets_sorted:
                if symbol_set_.complete is False or symbol_set_.complete is None:
                    symbol_set_.setComplete(False)
                    current_symbol_set_holder.set(symbol_set_)
                    break

        current_symbol_holder = Holder()

        def scopeUpdateCurrentSymbol(source):
            symbols = []
            for symbol in self.symbols:
                if not symbol.selected:
                    symbols.append(symbol)

            for symbol, race in source.addRaceTaskList(symbols):
                race.addFunction(symbol.enableIdlePlayTC)
                race.addScope(symbol.scopeSelect)
                race.addFunction(current_symbol_holder.set, symbol)

            with source.addFork() as fork:
                for symbol, parallel in fork.addParallelTaskList(self.symbols):
                    parallel.addFunction(symbol.disableIdlePlayTC)

        self.tc_main = TaskManager.createTaskChain(Repeat=True)
        with self.tc_main as tc:
            tc.addFunction(updateCurrentSymbolSet)
            tc.addScope(scopeUpdateCurrentSymbol)

            with tc.addIfTask(lambda: current_symbol_holder.get() in current_symbol_set_holder.get().symbols) as (_, false):
                false.addFunction(lambda: current_symbol_holder.get().setSelected(False))
                false.addFunction(lambda: [symbol.setSelected(False) for symbol in current_symbol_set_holder.get().symbols])
                false.addScope(SymbolSet.scopePlaySetFail)

            with tc.addIfTask(lambda: all(symbol_.selected for symbol_ in current_symbol_set_holder.get().symbols)) as (true, _):
                true.addFunction(lambda: current_symbol_set_holder.get().setComplete(True))
                true.addScope(SymbolSet.scopePlaySetComplete)

            with tc.addIfTask(lambda: all(symbol_set_.complete for symbol_set_ in self.symbol_sets_sorted)) as (true, _):
                true.addScope(SymbolSet.scopePlayWin)
                true.addFunction(self.enigmaComplete)

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(FindSymbolsSetsMatchingCenter, self)._onPreparation()
        self.loadParam()
        self.setup()

    def _onActivate(self):
        super(FindSymbolsSetsMatchingCenter, self)._onActivate()

    def _onDeactivate(self):
        super(FindSymbolsSetsMatchingCenter, self)._onDeactivate()
        self.cleanUp()

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self.runTaskChains()

    def _stopEnigma(self):
        if self.tc_main is not None:
            self.tc_main.cancel()

    def _restoreEnigma(self):
        self.runTaskChains()

    def _resetEnigma(self):
        self.cleanUp()
        self.setup()
        self.runTaskChains()

    def _skipEnigma(self):
        return